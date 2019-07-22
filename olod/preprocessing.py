#!/usr/bin/python
import argparse
import sys
import os
from subprocess import call

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
animaExtraDataDir = configParser.get("anima-scripts",'extra-data-root') # atlas path redefined later - issue space in udd/fgalassi

parser = argparse.ArgumentParser(
    prog = 'preprocessing',
    formatter_class = argparse.RawDescriptionHelpFormatter)

parser.add_argument('-r','--reference',required=True,help='Path to the ref image')
parser.add_argument('-f','--flair',required=True,help='Path to the FLAIR image')
parser.add_argument('-i','--t1',required=True,help='Path to the T1 image')
parser.add_argument('-j','--t2', default="", help='Path to the T2 image')
#parser.add_argument('-k','--t1g', default="", help='Path to the T1G image')
#parser.add_argument('-c','--lesions',required=True,help='Path to the consensus image')
parser.add_argument('-o','--outFolder',required=True,help='Path to the outputFolder')
parser.add_argument('-T','--nbThreads',required=False,type=int,help='Number of execution threads (default: 0 = all cores)',default=0)
args = parser.parse_args()

#lesionImg = args.lesions
refImage = args.reference
tmpFolder = args.outFolder
#listImages = [args.flair, args.t1, args.t2, args.t1g]
listImages = [args.flair, args.t1, args.t2]
nbThreads=str(args.nbThreads)

# Anima commands
animaPyramidalBMRegistration = os.path.join(animaDir,"animaPyramidalBMRegistration")
animaMaskImage = os.path.join(animaDir,"animaMaskImage")
animaNLMeans = os.path.join(animaDir,"animaNLMeans")
animaN4BiasCorrection = os.path.join(animaDir,"animaN4BiasCorrection")
animaApplyTransformSerie = os.path.join(animaDir,"animaApplyTransformSerie")
animaMaskImage = os.path.join(animaDir,"animaMaskImage")
animaTransformSerieXmlGenerator = os.path.join(animaDir,"animaTransformSerieXmlGenerator")
animaDenseSVFBMRegistration = os.path.join(animaDir,"animaDenseSVFBMRegistration")
animaConvertImage = os.path.join(animaDir,"animaConvertImage")
animaImageArithmetic = os.path.join(animaDir,"animaImageArithmetic")

animaBrainExtractionScript = os.path.join(animaScriptsDir,"brain_extraction","animaAtlasBasedBrainExtraction.py")

# Atlas
atlasDir = "/temp_dd/igrida-fs1/fgalassi/Anima-Scripts_data/olivier-atlas"
atlasImage = os.path.join(atlasDir,"ATLAS.nrrd")
atlasImageMasked = os.path.join(atlasDir,"ATLAS-masked.nrrd")
mask = os.path.join(atlasDir,"ATLAS-mask.nrrd") 
mask_up = os.path.join(atlasDir,"ATLAS-mask-cropped.nrrd") 
mask_down = os.path.join(atlasDir,"ATLAS-mask-down.nrrd")

# brain extraction ref image
refImagePrefix = os.path.splitext(refImage)[0]
if os.path.splitext(refImage)[1] == '.gz' :
	refImagePrefix = os.path.splitext(refImagePrefix)[0]

command = [animaN4BiasCorrection, "-i", os.path.join(tmpFolder, refImage), "-o",  os.path.join(tmpFolder,refImagePrefix + "_unbiased.nrrd")]
call(command)
command = ["python", animaBrainExtractionScript, os.path.join(tmpFolder,refImagePrefix + "_unbiased.nrrd")]
call(command)

brainMask = refImagePrefix + "_unbiased_brainMask.nrrd"        
maskname = "Mask_registered.nii.gz" #rename mask
command = [animaConvertImage, "-i", brainMask, "-o", os.path.join(tmpFolder,maskname)]
call(command)

# register to ref image and process
for i in range(0,len(listImages)) :

	inputPrefix = os.path.splitext(listImages[i])[0]
	if os.path.splitext(listImages[i])[1] == '.gz' :
		inputPrefix = os.path.splitext(inputPrefix)[0]

	outputDataFile0 = inputPrefix + "_unbiased.nrrd"
	command = [animaN4BiasCorrection, "-i", listImages[i], "-o",  os.path.join(tmpFolder, outputDataFile0)]
	call(command)

	outputDataFile1 = inputPrefix + "_registered.nrrd"
	command = [animaPyramidalBMRegistration, "-r", os.path.join(tmpFolder,refImagePrefix + "_unbiased.nrrd"), "-m", os.path.join(tmpFolder,outputDataFile0), "-o", os.path.join(tmpFolder,outputDataFile1), "-O", os.path.join(tmpFolder,inputPrefix + "_rig_tr.txt"), "-p", "4", "-l", "1","-T", nbThreads]
	call(command)

	outputDataFile2 = inputPrefix + "_nlm.nrrd"
	command = [animaNLMeans, "-i", os.path.join(tmpFolder, outputDataFile1), "-o", os.path.join(tmpFolder, outputDataFile2), "-n", "3"]
	call(command)

	outputDataFile3 = inputPrefix + "_preprocessed.nrrd"
	command = [animaMaskImage, "-i", os.path.join(tmpFolder, outputDataFile2), "-m", os.path.join(tmpFolder, brainMask), "-o", os.path.join(tmpFolder, outputDataFile3)]
	call(command)

	if "T1" in inputPrefix and "GADO" not in inputPrefix or "t1" in inputPrefix:
         filename = "T1_preprocessed.nii.gz"
         command = [animaConvertImage, "-i", os.path.join(tmpFolder,outputDataFile3), "-o", os.path.join(tmpFolder,filename)]
         call(command)
#	if "GADO" in inputPrefix :
#         filename = "T1_GADO_preprocessed.nii.gz"
#         command = [animaConvertImage, "-i", os.path.join(tmpFolder,outputDataFile3), "-o", os.path.join(tmpFolder,filename)]
#         call(command)
	if "TSE" in inputPrefix or "DUAL" in inputPrefix or "3Dt2space" in inputPrefix or "T2" in inputPrefix:
         filename = "T2_preprocessed.nii.gz"
         command = [animaConvertImage, "-i", os.path.join(tmpFolder,outputDataFile3), "-o", os.path.join(tmpFolder,filename)]
         call(command)
	if "FLAIR" in inputPrefix or "WIP" in inputPrefix or"t2spaceT2pIRsagc6" in inputPrefix:
         filename = "FLAIR_preprocessed.nii.gz"
         command = [animaConvertImage, "-i", os.path.join(tmpFolder,outputDataFile3), "-o", os.path.join(tmpFolder,filename)]
         call(command)
 
# REGISTER ATLAS to subj FLAIR
command=[animaDir + "animaPyramidalBMRegistration","-m",atlasImageMasked,"-r",os.path.join(tmpFolder,"T1_preprocessed.nii.gz"),"-o",os.path.join(tmpFolder,"atlas_rig.nrrd"),"-O",os.path.join(tmpFolder,"atlas_rig_tr.txt"),"-p","4","-l","1","--sp","3"]
call(command)
command=[animaDir + "animaPyramidalBMRegistration","-m",atlasImageMasked,"-r",os.path.join(tmpFolder,"T1_preprocessed.nii.gz"),"-o",os.path.join(tmpFolder,"atlas_aff.nrrd"),"-O",os.path.join(tmpFolder,"atlas_aff_tr.txt"),"-i",os.path.join(tmpFolder,"atlas_rig_tr.txt"),"-p","4","-l","1","--sp","3","--ot","2"]
call(command)
command=[animaDir + "animaDenseSVFBMRegistration","-r",os.path.join(tmpFolder,"T1_preprocessed.nii.gz"),"-m",os.path.join(tmpFolder,"atlas_aff.nrrd"),"-o",os.path.join(tmpFolder,"atlas_nl.nrrd"),"-O",os.path.join(tmpFolder,"atlas_nl_tr.nrrd"),"-p","4","-l","1","--sr","1"]
call(command)
command=[animaDir + "animaTransformSerieXmlGenerator","-i",os.path.join(tmpFolder,"atlas_aff_tr.txt"),"-i",os.path.join(tmpFolder,"atlas_nl_tr.nrrd"),"-o",os.path.join(tmpFolder,"atlas_nl_tr.xml")]
call(command)
command=[animaDir + "animaApplyTransformSerie","-i",atlasImageMasked,"-t",os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g",os.path.join(tmpFolder,"T1_preprocessed.nii.gz"),"-o",os.path.join(tmpFolder,"atlasImage_registered.nii.gz")]
call(command)

# register mask up and down
command = [animaDir + "animaApplyTransformSerie","-i",mask,"-t", os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g", os.path.join(tmpFolder,"T1_preprocessed.nii.gz"),"-o", os.path.join(tmpFolder,"mask.nii.gz"),"-n","nearest"]
call(command)
command = [animaDir + "animaApplyTransformSerie","-i",mask_up,"-t", os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g", os.path.join(tmpFolder,"T1_preprocessed.nii.gz"),"-o", os.path.join(tmpFolder,"mask-up.nii.gz"),"-n","nearest"]
call(command) 
command = [animaDir + "animaApplyTransformSerie","-i",mask_down,"-t", os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g", os.path.join(tmpFolder,"T1_preprocessed.nii.gz"),"-o", os.path.join(tmpFolder,"mask-down.nii.gz"),"-n","nearest"]
call(command)

# interesct mask, mask up and down
command=[animaDir + "animaMaskImage", "-i", os.path.join(tmpFolder,"Mask_registered.nii.gz"), "-m",os.path.join(tmpFolder,"mask.nii.gz"), "-o", os.path.join(tmpFolder,"mask.nii.gz")]
call(command)
command=[animaDir + "animaMaskImage", "-i", os.path.join(tmpFolder,"Mask_registered.nii.gz"), "-m",os.path.join(tmpFolder,"mask-up.nii.gz"), "-o", os.path.join(tmpFolder,"mask-up.nii.gz")]
call(command)
command=[animaDir + "animaMaskImage", "-i", os.path.join(tmpFolder,"Mask_registered.nii.gz"), "-m",os.path.join(tmpFolder,"mask-down.nii.gz"), "-o", os.path.join(tmpFolder,"mask-down.nii.gz")]
call(command)

# apply mask, mask  up and down to preprocessed images
command=[animaMaskImage, "-i", os.path.join(tmpFolder,"FLAIR_preprocessed.nii.gz"), "-m", os.path.join(tmpFolder,"mask.nii.gz"), "-o", os.path.join(tmpFolder, "FLAIR_preprocessed.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(tmpFolder,"T2_preprocessed.nii.gz"), "-m", os.path.join(tmpFolder,"mask.nii.gz"), "-o", os.path.join(tmpFolder, "T2_preprocessed.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(tmpFolder,"T1_preprocessed.nii.gz"), "-m", os.path.join(tmpFolder,"mask.nii.gz"), "-o", os.path.join(tmpFolder, "T1_preprocessed.nii.gz")]
call(command)
#command=[animaMaskImage, "-i", os.path.join(tmpFolder,"T1_GADO_preprocessed.nii.gz"), "-m", os.path.join(tmpFolder,"mask.nii.gz"), "-o", os.path.join(tmpFolder, "T1_GADO_preprocessed.nii.gz")]
#call(command)

command=[animaMaskImage, "-i", os.path.join(tmpFolder,"FLAIR_preprocessed.nii.gz"), "-m", os.path.join(tmpFolder,"mask-up.nii.gz"), "-o", os.path.join(tmpFolder, "FLAIR_preprocessed-up.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(tmpFolder,"T2_preprocessed.nii.gz"), "-m", os.path.join(tmpFolder,"mask-up.nii.gz"), "-o", os.path.join(tmpFolder, "T2_preprocessed-up.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(tmpFolder,"T1_preprocessed.nii.gz"), "-m", os.path.join(tmpFolder,"mask-up.nii.gz"), "-o", os.path.join(tmpFolder, "T1_preprocessed-up.nii.gz")]
call(command)

command=[animaMaskImage, "-i", os.path.join(tmpFolder,"FLAIR_preprocessed.nii.gz"), "-m", os.path.join(tmpFolder,"mask-down.nii.gz"), "-o", os.path.join(tmpFolder, "FLAIR_preprocessed-down.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(tmpFolder,"T2_preprocessed.nii.gz"), "-m", os.path.join(tmpFolder,"mask-down.nii.gz"), "-o", os.path.join(tmpFolder, "T2_preprocessed-down.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(tmpFolder,"T1_preprocessed.nii.gz"), "-m", os.path.join(tmpFolder,"mask-down.nii.gz"), "-o", os.path.join(tmpFolder, "T1_preprocessed-down.nii.gz")]
call(command)

# register wm, gm, csf maps, les prob map
command = [animaDir + "animaApplyTransformSerie","-i", os.path.join(atlasDir, "ATLAS-wm_masked.nrrd"),"-t", os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g",os.path.join(tmpFolder,"T1_preprocessed.nii.gz"),"-o", os.path.join(tmpFolder,"ATLAS-wm_masked-reg.nii.gz")]
call(command)
command = [animaDir + "animaApplyTransformSerie","-i", os.path.join(atlasDir, "ATLAS-gm_masked.nrrd"),"-t", os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g", os.path.join(tmpFolder,"T1_preprocessed.nii.gz"),"-o", os.path.join(tmpFolder,"ATLAS-gm_masked-reg.nii.gz")]
call(command)
command = [animaDir + "animaApplyTransformSerie","-i", os.path.join(atlasDir, "ATLAS-csf_masked.nrrd"),"-t", os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g", os.path.join(tmpFolder,"T1_preprocessed.nii.gz"),"-o", os.path.join(tmpFolder, "ATLAS-csf_masked-reg.nii.gz")]
call(command)
command = [animaDir + "animaApplyTransformSerie","-i", os.path.join(atlasDir, "prob_map_lesions_MS-SPI_MICCAI_normalized_masked.nrrd"),"-t", os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g",  os.path.join(tmpFolder,"T1_preprocessed.nii.gz"),"-o", os.path.join(tmpFolder, "prob_map-reg.nii.gz")]
call(command)

# apply mask, mask  up and down to  wm, gm, csf maps, les prob map
command=[animaMaskImage, "-i", os.path.join(tmpFolder,"atlasImage_registered.nii.gz"), "-m", os.path.join(tmpFolder,"mask.nii.gz"), "-o", os.path.join(tmpFolder, "atlasImage_registered.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(tmpFolder,"ATLAS-wm_masked-reg.nii.gz"), "-m", os.path.join(tmpFolder,"mask.nii.gz"), "-o", os.path.join(tmpFolder, "ATLAS-wm_masked-reg.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(tmpFolder,"ATLAS-csf_masked-reg.nii.gz"), "-m", os.path.join(tmpFolder,"mask.nii.gz"), "-o", os.path.join(tmpFolder, "ATLAS-csf_masked-reg.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(tmpFolder,"ATLAS-gm_masked-reg.nii.gz"), "-m", os.path.join(tmpFolder,"mask.nii.gz"), "-o", os.path.join(tmpFolder, "ATLAS-gm_masked-reg.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(tmpFolder,"prob_map-reg.nii.gz"), "-m", os.path.join(tmpFolder,"mask.nii.gz"), "-o", os.path.join(tmpFolder, "prob_map-reg.nii.gz")]
call(command)


