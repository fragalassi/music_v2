#!/usr/bin/python

import argparse
import sys

if sys.version_info[0] > 2:
    import configparser as ConfParser
else:
    import ConfigParser as ConfParser

import os
import tempfile
from subprocess import call

configFilePath = os.path.expanduser("~") + "/.anima/config.txt"
if not os.path.exists(configFilePath):
    print('Please create a configuration file for Anima python scripts. Refer to the README')
    quit()

configParser = ConfParser.RawConfigParser()
configParser.read(configFilePath)

animaDir = configParser.get("anima-scripts", 'anima')
animaScriptsDir = configParser.get("anima-scripts", 'anima-scripts-root')

parser = argparse.ArgumentParser(
    prog='animaMSExamRegistration',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Registers input images onto a common reference for subsequent longitudinal analysis. There will be two outputs for each image, one registered image and one pre-processed image.")

parser.add_argument('-r', '--reference', required=True,
                    help='Path to the MS patient reference image (usually FLAIR at first time point)')
parser.add_argument('-f', '--flair', required=True, help='Path to the MS patient FLAIR image to register')
parser.add_argument('-t', '--t1', required=True, help='Path to the MS patient T1 image to register')
parser.add_argument('-g', '--t1-gd', required=True, help='Path to the MS patient T1-Gd image to register')
parser.add_argument('-T', '--t2', default="", help='Path to the MS patient T2 image to register')

args = parser.parse_args()
tmpFolder = tempfile.mkdtemp()

# Anima commands
animaPyramidalBMRegistration = os.path.join(animaDir, "animaPyramidalBMRegistration")
animaMaskImage = os.path.join(animaDir, "animaMaskImage")
animaNLMeans = os.path.join(animaDir, "animaNLMeans")
animaN4BiasCorrection = os.path.join(animaDir, "animaN4BiasCorrection")
animaBrainExtractionScript = os.path.join(animaScriptsDir, "brain_extraction", "animaAtlasBasedBrainExtraction.py")

refImage = args.reference
listImages = [args.flair, args.t1, args.t1_gd]
if args.t2 != "":
    listImages.append(args.t2)

brainExtractionCommand = ["python", animaBrainExtractionScript, refImage]
call(brainExtractionCommand)

refImagePrefix = os.path.splitext(refImage)[0]
if os.path.splitext(refImage)[1] == '.gz':
    refImagePrefix = os.path.splitext(refImagePrefix)[0]

brainMask = refImagePrefix + "_brainMask.nrrd"

# Main loop
for i in range(0, len(listImages)):
    inputPrefix = os.path.splitext(listImages[i])[0]
    if os.path.splitext(listImages[i])[1] == '.gz':
        inputPrefix = os.path.splitext(inputPrefix)[0]

    outputDataFile = inputPrefix + "_registered.nrrd"

    rigidRegistrationCommand = [animaPyramidalBMRegistration, "-r", refImage, "-m", listImages[i], "-o", outputDataFile,
                                "-p", "4", "-l", "1"]
    call(rigidRegistrationCommand)

    unbiasedSecondImage = os.path.join(tmpFolder, "SecondImage_unbiased.nrrd")
    biasCorrectionCommand = [animaN4BiasCorrection, "-i", outputDataFile, "-o", unbiasedSecondImage, "-B", "0.3"]
    call(biasCorrectionCommand)

    nlmSecondImage = os.path.join(tmpFolder, "SecondImage_unbiased_nlm.nrrd")
    nlmCommand = [animaNLMeans, "-i", unbiasedSecondImage, "-o", nlmSecondImage, "-n", "3"]
    call(nlmCommand)

    outputPreprocessedFile = inputPrefix + "_preprocessed.nrrd"
    secondMaskCommand = [animaMaskImage, "-i", nlmSecondImage, "-m", brainMask, "-o", outputPreprocessedFile]
    call(secondMaskCommand)
