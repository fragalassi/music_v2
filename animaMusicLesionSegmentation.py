#!/usr/bin/python
# Warning: works only on unix-like systems, not windows where "python animaMusicLesionSegmentation.py ..." has to be run

import os
import sys
import shutil
import argparse
import tempfile

if sys.version_info[0] > 2 :
    import configparser as ConfParser
else :
    import ConfigParser as ConfParser

configFilePath = os.path.expanduser("~") + "/.anima/config.txt"
if not os.path.exists(configFilePath) :
    print('Please create a configuration file for Anima python scripts. Refer to the README')
    quit()

configParser = ConfParser.RawConfigParser()
configParser.read(configFilePath)

animaDir = configParser.get("anima-scripts",'anima')
animaScriptsDir = configParser.get("anima-scripts",'anima-scripts-root')
animaExtraDataDir = configParser.get("anima-scripts",'extra-data-root')
sys.path.append(animaScriptsDir)

import animaMusicLesionAdditionalPreprocessing as preproc
import animaMusicLesionCoreProcessing as coreproc
import animaMusicLesionPostProcessing as postproc
import totalLesionLoadEstimator as tll_estimator

tmpFolder = tempfile.mkdtemp()

parser = argparse.ArgumentParser(
    prog='animaMusicLesionSegmentation.py',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Compute MS lesion segmentation using the graph cuts algorithm. Uses preprocessed images from animaMSExamRegistration.py')

parser.add_argument('-f', '--flair', required=True, help='Path to the MS patient FLAIR image')
parser.add_argument('-t', '--t1', required=True, help='Path to the MS patient T1 image')
parser.add_argument('-T', '--t2', required=True, help='Path to the MS patient T2 image')
parser.add_argument('-m','--maskImage',required=True,help='path to the MS patient brain mask image')
parser.add_argument('-o','--outputImage',required=True,help='path to output image')
parser.add_argument('-n','--nbThreads',required=False,type=int,help='Number of execution threads (default: 0 = all cores)',default=0)

args=parser.parse_args()

t1Image=args.t1
t2Image=args.t2
flairImage=args.flair
maskImage=args.maskImage
outputImage=args.outputImage
nbThreads=str(args.nbThreads)

if not(os.path.isfile(t1Image)):
    print("IO Error: the file "+t1Image+" doesn't exist.")
    quit()

if not(os.path.isfile(t2Image)):
    print("IO Error: the file "+t2Image+" doesn't exist.")
    quit()

if not(os.path.isfile(flairImage)):
    print("IO Error: the file "+flairImage+" doesn't exist.")
    quit()

if not(os.path.isfile(maskImage)):
    print("IO Error: the file "+maskImage+" doesn't exist.")
    quit()

outputFolder=os.path.dirname(outputImage)
if not(os.path.isdir(outputFolder)) and outputFolder != "":
    os.makedirs(outputFolder)

# First perform additional preprocessing
print('Starting additional preprocessing of data')
preproc.music_lesion_additional_preprocessing(animaDir, animaExtraDataDir, tmpFolder, t1Image, t2Image, flairImage,
                                              maskImage,nbThreads)

# Estimation of the TLL to determine the best parameter set

t1NormedImage = os.path.join(tmpFolder,"T1-normed.nrrd")
t2NormedImage = os.path.join(tmpFolder,"T2-normed.nrrd")
flairNormedImage = os.path.join(tmpFolder,"FLAIR-normed.nrrd")

atlasDir = os.path.join(animaExtraDataDir, "olivier-atlas")
tllE = tll_estimator.lesion_load_estimation(animaDir, atlasDir, tmpFolder, t1NormedImage, t2NormedImage,
                                            flairNormedImage, nbThreads)

# Then run core process over up images
upperOutputImage = os.path.join(tmpFolder,"UpperGraphCutSegmentation.nrrd")
t1UpperImage = os.path.join(tmpFolder, "T1-up-normed-bs.nrrd")
t2UpperImage = os.path.join(tmpFolder, "T2-up-normed-bs.nrrd")
flairUpperImage = os.path.join(tmpFolder, "FLAIR-up-normed-bs.nrrd")
maskUpperImage = os.path.join(tmpFolder,"mask-up-int-bs.nrrd")
atlasWMUpperImage = os.path.join(tmpFolder, "ATLAS-wm_masked_up-reg-bs.nrrd")
atlasGMUpperImage = os.path.join(tmpFolder, "ATLAS-gm_masked_up-reg-bs.nrrd")
atlasCSFUpperImage = os.path.join(tmpFolder, "ATLAS-csf_masked_up-reg-bs.nrrd")
msPriorsUpperImage = os.path.join(tmpFolder, "prob_map_up-reg-bs.nrrd")

print('Done with additional preprocessing, starting core processing of data')
coreproc.music_lesion_core_processing(animaDir,upperOutputImage,t1UpperImage,t2UpperImage,
                                      flairUpperImage,maskUpperImage,atlasWMUpperImage,atlasGMUpperImage,
                                      atlasCSFUpperImage,msPriorsUpperImage,tllE,nbThreads)

# Then down images
downOutputImage = os.path.join(tmpFolder,"DownGraphCutSegmentation.nrrd")
t1DownImage = os.path.join(tmpFolder, "T1-down-normed-bs.nrrd")
t2DownImage = os.path.join(tmpFolder, "T2-down-normed-bs.nrrd")
flairDownImage = os.path.join(tmpFolder, "FLAIR-down-normed-bs.nrrd")
maskDownImage = os.path.join(tmpFolder,"mask-down-int-bs.nrrd")
atlasWMDownImage = os.path.join(tmpFolder, "ATLAS-wm_masked_down-reg-bs.nrrd")
atlasGMDownImage = os.path.join(tmpFolder, "ATLAS-gm_masked_down-reg-bs.nrrd")
atlasCSFDownImage = os.path.join(tmpFolder, "ATLAS-csf_masked_down-reg-bs.nrrd")
msPriorsDownImage = os.path.join(tmpFolder, "prob_map_down-reg-bs.nrrd")

coreproc.music_lesion_core_processing(animaDir,downOutputImage,t1DownImage,t2DownImage,
                                      flairDownImage,maskDownImage,atlasWMDownImage,atlasGMDownImage,
                                      atlasCSFDownImage,msPriorsDownImage,tllE,nbThreads)

maskUpperImage = os.path.join(tmpFolder,"mask-up.nrrd")
maskDownImage = os.path.join(tmpFolder,"mask-down.nrrd")
maskBSImage = os.path.join(tmpFolder,"brain-mask_intersected-reg.nrrd")
flair2DownImage = os.path.join(tmpFolder, "FLAIR2-normed-down-bs.nrrd")
flair2BSImage = os.path.join(tmpFolder, "FLAIR2-norm-down-wbs.nrrd")
atlasCSFBSImage = os.path.join(tmpFolder, "ATLAS-csf_masked-down-wbs.nrrd")

# Now run post-processing
print('Done with core processing, starting post processing of data')
postproc.music_lesion_post_processing(animaDir, tmpFolder, outputImage, upperOutputImage, downOutputImage,
                                      flair2DownImage, flair2BSImage, atlasWMUpperImage, atlasGMUpperImage,
                                      atlasCSFUpperImage, atlasWMDownImage, atlasGMDownImage, atlasCSFDownImage,
                                      atlasCSFBSImage, maskUpperImage, maskDownImage, maskBSImage, nbThreads)

shutil.rmtree(tmpFolder)
