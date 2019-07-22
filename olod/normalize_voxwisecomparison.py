# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 13:13:25 2018

@author: fgalassi
"""

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
animaExtraDataDir = configParser.get("anima-scripts",'extra-data-root')

parser = argparse.ArgumentParser(
    prog = 'normalise_vxcomparion',
    formatter_class = argparse.RawDescriptionHelpFormatter)

parser.add_argument('-i','--dir_subj_r', required=True, help='')
#parser.add_argument('-c','--dir_subj_r_c', required=True, help='')
parser.add_argument('-T','--nbThreads',required=False,type=int,help='Number of execution threads (default: 0 = all cores)', default=0)
args = parser.parse_args()

nbThreads=str(args.nbThreads)
dir_subj_r = args.dir_subj_r
#dir_subj_r_c = args.dir_subj_r_c

# anima tools
animaVectorizeImages=os.path.join(animaDir,"animaVectorizeImages")
animaNotsuStandardization=os.path.join(animaDir,"animaNotsuStandardization")
animaMaskImage=os.path.join(animaDir,"animaMaskImage")
animaConvertImage=os.path.join(animaDir,"animaConvertImage")
animaApplyTransformSerie=os.path.join(animaDir,"animaApplyTransformSerie")
animaImageArithmetic=os.path.join(animaDir,"animaImageArithmetic")
animaPyramidalBMRegistration=os.path.join(animaDir,"animaPyramidalBMRegistration")
animaTransformSerieXmlGenerator=os.path.join(animaDir,"animaTransformSerieXmlGenerator")
animaApplyTransformSerie=os.path.join(animaDir,"animaApplyTransformSerie")
animaDenseSVFBMRegistration=os.path.join(animaDir,"animaDenseSVFBMRegistration")
animaPatientToGroupComparison=os.path.join(animaDir,"animaPatientToGroupComparison")
animaFDRCorrectPValues=os.path.join(animaDir,"animaFDRCorrectPValues")
animaThrImage=os.path.join(animaDir,"animaThrImage")
animaOtsuThrImage = os.path.join(animaDir,"animaOtsuThrImage")

# control subjs
atlasDir = "/temp_dd/igrida-fs1/fgalassi/Anima-Scripts_data"
dir_controlT1 =os.path.join(atlasDir,"uspio-atlas","scalar-space","T1")
dir_controlT2 =os.path.join(atlasDir,"uspio-atlas","scalar-space","T2")
dir_controlFLAIR =os.path.join(atlasDir,"uspio-atlas","scalar-space","FLAIR")
dir_controlFLAIR_T2=os.path.join(atlasDir,"uspio-atlas","scalar-space","FLAIR_T2")
dir_controlFLAIR_avg =os.path.join(atlasDir,"uspio-atlas","scalar-space","space-ref")

# register FLAIR template to FLAIR img
command = [animaPyramidalBMRegistration,"-m",os.path.join(dir_controlFLAIR_avg,"FLAIR_averaged.nrrd"),"-r",os.path.join(dir_subj_r,"FLAIR_preprocessed.nii.gz"), "-o", "avg_rig.nrrd","-O",os.path.join(dir_subj_r,"avg_rig_tr.txt"),"-p","4","-l","1","--sp","3","-T", nbThreads]
call(command)
command = [animaPyramidalBMRegistration,"-m",os.path.join(dir_controlFLAIR_avg,"FLAIR_averaged.nrrd"),"-r",os.path.join(dir_subj_r,"FLAIR_preprocessed.nii.gz"),"-o", os.path.join(dir_subj_r,"avg_aff.nrrd"),"-O",os.path.join(dir_subj_r,"avg_aff_tr.txt"),"-i",os.path.join(dir_subj_r, "avg_rig_tr.txt"),"-p","4","-l","1","--sp","3","--ot","2","-T", nbThreads]
call(command)
command = [animaDenseSVFBMRegistration,"-r",os.path.join(dir_subj_r,"FLAIR_preprocessed.nii.gz"),"-m",os.path.join(dir_subj_r,"avg_aff.nrrd"),"-o", os.path.join(dir_subj_r, "avg_nl.nrrd"),"-O", os.path.join(dir_subj_r,"avg_nl_tr.nrrd"),"-p","4","-l","1","--sr","1","-T", nbThreads]
call(command)
command = [animaTransformSerieXmlGenerator,"-i",os.path.join(dir_subj_r,"avg_aff_tr.txt"),"-i", os.path.join(dir_subj_r,"avg_nl_tr.nrrd"),"-o",os.path.join(dir_subj_r,"avg_nl_tr.xml")]
call(command)
command = [animaApplyTransformSerie,"-i", os.path.join(dir_controlFLAIR_avg,"FLAIR_averaged.nrrd"),"-t", os.path.join(dir_subj_r,"avg_nl_tr.xml"),"-g",os.path.join(dir_subj_r,"FLAIR_preprocessed.nii.gz"),"-o", os.path.join(dir_subj_r,"FLAIR_averaged-reg.nii.gz"),"-p", nbThreads]
call(command)
command = [animaApplyTransformSerie,"-i", os.path.join(dir_controlFLAIR_avg,"FLAIR_averaged.nrrd"),"-t", os.path.join(dir_subj_r,"avg_nl_tr.xml"),"-g",os.path.join(dir_subj_r,"FLAIR_preprocessed.nii.gz"),"-o", os.path.join(dir_subj_r, "FLAIR_averaged-reg.nii.gz"),"-p", nbThreads]
call(command) 

# apply transform to template masks
command = [animaApplyTransformSerie,"-i", os.path.join(dir_controlFLAIR_avg,"brain-mask_intersected.nrrd"),"-t", os.path.join(dir_subj_r,"avg_nl_tr.xml"),"-g",os.path.join(dir_subj_r,"FLAIR_preprocessed.nii.gz"),"-o",  os.path.join(dir_subj_r,"brain-mask_intersected-reg.nii.gz"),"-n","nearest","-p", nbThreads]
call(command)
command = [animaApplyTransformSerie,"-i", os.path.join(dir_controlFLAIR_avg,"brainstemMask.nii.gz"),"-t", os.path.join(dir_subj_r,"avg_nl_tr.xml"),"-g",os.path.join(dir_subj_r,"FLAIR_preprocessed.nii.gz"),"-o",  os.path.join(dir_subj_r,"brainstemMask-reg.nii.gz"),"-n","nearest","-p", nbThreads]
call(command)

# intersect masks
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"mask-up.nii.gz"), "-m",  os.path.join(dir_subj_r,"brain-mask_intersected-reg.nii.gz"), "-o", os.path.join(dir_subj_r,"mask-up-int.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"mask-down.nii.gz"), "-m",  os.path.join(dir_subj_r,"brain-mask_intersected-reg.nii.gz"), "-o", os.path.join(dir_subj_r,"mask-down-int.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"Mask_registered.nii.gz"), "-m",  os.path.join(dir_subj_r,"brain-mask_intersected-reg.nii.gz"), "-o", os.path.join(dir_subj_r,"mask-int.nii.gz")]
call(command)

# mask out brainst
command=[animaImageArithmetic, "-i", os.path.join(dir_subj_r,"brain-mask_intersected-reg.nii.gz"), "-s",  os.path.join(dir_subj_r,"brainstemMask-reg.nii.gz"), "-o", os.path.join(dir_subj_r,"brain-mask_intersected-reg-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"mask-up.nii.gz"), "-m",  os.path.join(dir_subj_r,"brain-mask_intersected-reg-bs.nii.gz"), "-o", os.path.join(dir_subj_r,"mask-up-int-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"mask-down.nii.gz"), "-m",  os.path.join(dir_subj_r,"brain-mask_intersected-reg-bs.nii.gz"), "-o", os.path.join(dir_subj_r,"mask-down-int-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"Mask_registered.nii.gz"), "-m",  os.path.join(dir_subj_r,"brain-mask_intersected-reg-bs.nii.gz"), "-o", os.path.join(dir_subj_r,"mask-int-bs.nii.gz")]
call(command)

# apply masks to subj images
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"FLAIR_preprocessed.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-int.nii.gz"), "-o", os.path.join(dir_subj_r, "FLAIR_preprocessed.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"T2_preprocessed.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-int.nii.gz"), "-o", os.path.join(dir_subj_r, "T2_preprocessed.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"T1_preprocessed.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-int.nii.gz"), "-o", os.path.join(dir_subj_r, "T1_preprocessed.nii.gz")]
call(command)
#up
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"FLAIR_preprocessed.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r, "FLAIR_preprocessed-up.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"T2_preprocessed.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r, "T2_preprocessed-up.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"T1_preprocessed.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r, "T1_preprocessed-up.nii.gz")]
call(command)
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r_c,"Consensus.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r, "Consensus-up.nii.gz")]
#call(command)
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r_c,"Consensus.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r, "Consensus-down.nii.gz")]
#call(command)
# down
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"FLAIR_preprocessed.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r, "FLAIR_preprocessed-down.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"T2_preprocessed.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r, "T2_preprocessed-down.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"T1_preprocessed.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r, "T1_preprocessed-down.nii.gz")]
call(command)

# register controls to subj images
for counter in range(1,21):
    command = [animaApplyTransformSerie,"-i", os.path.join(dir_controlFLAIR, "FLAIR_" + str(counter) + ".nrrd"),"-t",os.path.join(dir_subj_r,"avg_nl_tr.xml"),"-g",os.path.join(dir_subj_r,"FLAIR_preprocessed.nii.gz"),"-o", os.path.join(dir_subj_r, "FLAIR_" + str(counter) + "reg.nrrd"),"-p", nbThreads]
    call(command)
    command = [animaApplyTransformSerie,"-i", os.path.join(dir_controlT1, "T1_" + str(counter) + ".nrrd"),"-t",os.path.join(dir_subj_r,"avg_nl_tr.xml"),"-g",os.path.join(dir_subj_r,"FLAIR_preprocessed.nii.gz"),"-o", os.path.join(dir_subj_r, "T1_" + str(counter) + "reg.nrrd"),"-p", nbThreads]
    call(command)
    command = [animaApplyTransformSerie,"-i", os.path.join(dir_controlT2, "T2_" + str(counter) + ".nrrd"),"-t",os.path.join(dir_subj_r,"avg_nl_tr.xml"),"-g",os.path.join(dir_subj_r,"FLAIR_preprocessed.nii.gz"),"-o", os.path.join(dir_subj_r, "T2_" + str(counter) + "reg.nrrd"),"-p", nbThreads]
    call(command)
    command=[animaNotsuStandardization, "-r", os.path.join(dir_subj_r, "FLAIR_1reg.nrrd"), "-m", os.path.join(dir_subj_r, "FLAIR_" + str(counter) + "reg.nrrd"), "-R", os.path.join(dir_subj_r, "brain-mask_intersected-reg.nii.gz"), "-o", os.path.join(dir_subj_r, "FLAIR-normalized_" + str(counter) + "reg.nrrd")]
    call(command)
    command=[animaNotsuStandardization, "-r", os.path.join(dir_subj_r, "T1_1reg.nrrd"), "-m", os.path.join(dir_subj_r, "T1_" + str(counter) + "reg.nrrd"), "-R", os.path.join(dir_subj_r, "brain-mask_intersected-reg.nii.gz"), "-o", os.path.join(dir_subj_r, "T1-normalized_" + str(counter) + "reg.nrrd")]
    call(command)
    command=[animaNotsuStandardization, "-r", os.path.join(dir_subj_r, "T2_1reg.nrrd"), "-m", os.path.join(dir_subj_r, "T2_" + str(counter) + "reg.nrrd"), "-R", os.path.join(dir_subj_r, "brain-mask_intersected-reg.nii.gz"), "-o", os.path.join(dir_subj_r, "T2-normalized_" + str(counter) + "reg.nrrd")]
    call(command)

#    command=[animaNotsuStandardization, "-r", os.path.join(dir_controlFLAIR, "FLAIR_1reg.nrrd"), "-m", os.path.join(dir_controlFLAIR, "FLAIR_" + str(counter) + "reg.nrrd"), "-R", os.path.join(dir_subj_r, "mask-up-int.nii.gz"), "-o", os.path.join(dir_controlFLAIR, "FLAIR-up-normalized_" + str(counter) + "reg.nrrd")]
#    call(command)
#    command=[animaNotsuStandardization, "-r", os.path.join(dir_controlT1, "T1_1reg.nrrd"), "-m", os.path.join(dir_controlT1, "T1_" + str(counter) + "reg.nrrd"), "-R", os.path.join(dir_subj_r, "mask-up-int.nii.gz"), "-o", os.path.join(dir_controlT1, "T1-up-normalized_" + str(counter) + "reg.nrrd")]
#    call(command)
#    command=[animaNotsuStandardization, "-r", os.path.join(dir_controlT2, "T2_1reg.nrrd"), "-m", os.path.join(dir_controlT2, "T2_" + str(counter) + "reg.nrrd"), "-R", os.path.join(dir_subj_r, "mask-up-int.nii.gz"), "-o", os.path.join(dir_controlT2, "T2-up-normalized_" + str(counter) + "reg.nrrd")]
#    call(command)
#    command=[animaNotsuStandardization, "-r", os.path.join(dir_controlFLAIR, "FLAIR_1reg.nrrd"), "-m", os.path.join(dir_controlFLAIR, "FLAIR_" + str(counter) + "reg.nrrd"), "-R", os.path.join(dir_subj_r, "mask-down-int.nii.gz"), "-o", os.path.join(dir_controlFLAIR, "FLAIR-down-normalized_" + str(counter) + "reg.nrrd")]
#    call(command)
#    command=[animaNotsuStandardization, "-r", os.path.join(dir_controlT1, "T1_1reg.nrrd"), "-m", os.path.join(dir_controlT1, "T1_" + str(counter) + "reg.nrrd"), "-R", os.path.join(dir_subj_r, "mask-down-int.nii.gz"), "-o", os.path.join(dir_controlT1, "T1-down-normalized_" + str(counter) + "reg.nrrd")]
#    call(command)
#    command=[animaNotsuStandardization, "-r", os.path.join(dir_controlT2, "T2_1reg.nrrd"), "-m", os.path.join(dir_controlT2, "T2_" + str(counter) + "reg.nrrd"), "-R", os.path.join(dir_subj_r, "mask-down-int.nii.gz"), "-o", os.path.join(dir_controlT2, "T2-down-normalized_" + str(counter) + "reg.nrrd")]
#    call(command)
#    command=[animaImageArithmetic, "-i", os.path.join(dir_controlFLAIR, "FLAIR-up-normalized_" + str(counter) + "reg.nrrd"), "-a", os.path.join(dir_controlFLAIR, "FLAIR-down-normalized_" + str(counter) + "reg.nrrd"), "-o", os.path.join(dir_controlFLAIR, "FLAIR-normalized_" + str(counter) + "reg.nrrd"),"-T",nbThreads]
#    call(command)
#    command=[animaImageArithmetic, "-i", os.path.join(dir_controlT1, "T1-up-normalized_" + str(counter) + "reg.nrrd"), "-a", os.path.join(dir_controlT1, "T1-down-normalized_" + str(counter) + "reg.nrrd"), "-o", os.path.join(dir_controlT1, "T1-normalized_" + str(counter) + "reg.nrrd"),"-T",nbThreads]
#    call(command)
#    command=[animaImageArithmetic, "-i", os.path.join(dir_controlT2, "T2-up-normalized_" + str(counter) + "reg.nrrd"), "-a", os.path.join(dir_controlT2, "T2-down-normalized_" + str(counter) + "reg.nrrd"), "-o", os.path.join(dir_controlT2, "T2-normalized_" + str(counter) + "reg.nrrd"),"-T",nbThreads]
#    call(command)    
       
# normalize up
command=[animaNotsuStandardization, "-r", os.path.join(dir_subj_r, "FLAIR-normalized_1reg.nrrd"), "-m", os.path.join(dir_subj_r, "FLAIR_preprocessed-up.nii.gz"), "-R", os.path.join(dir_subj_r, "mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r, "FLAIR-up-notsu.nii.gz")]
call(command)
command=[animaNotsuStandardization, "-r", os.path.join(dir_subj_r, "T2-normalized_1reg.nrrd"), "-m", os.path.join(dir_subj_r, "T2_preprocessed-up.nii.gz"), "-R", os.path.join(dir_subj_r, "mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r, "T2-up-notsu.nii.gz")]
call(command)
command=[animaNotsuStandardization, "-r", os.path.join(dir_subj_r, "T1-normalized_1reg.nrrd"), "-m", os.path.join(dir_subj_r, "T1_preprocessed-up.nii.gz"), "-R", os.path.join(dir_subj_r, "mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r, "T1-up-notsu.nii.gz")]
call(command)
# normalize down
command=[animaNotsuStandardization, "-r", os.path.join(dir_subj_r, "FLAIR-normalized_1reg.nrrd"), "-m", os.path.join(dir_subj_r, "FLAIR_preprocessed-down.nii.gz"), "-R", os.path.join(dir_subj_r, "mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r, "FLAIR-down-notsu.nii.gz")]
call(command)
command=[animaNotsuStandardization, "-r", os.path.join(dir_subj_r, "T2-normalized_1reg.nrrd"), "-m", os.path.join(dir_subj_r, "T2_preprocessed-down.nii.gz"), "-R", os.path.join(dir_subj_r, "mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r, "T2-down-notsu.nii.gz")]
call(command)
command=[animaNotsuStandardization, "-r", os.path.join(dir_subj_r, "T1-normalized_1reg.nrrd"), "-m", os.path.join(dir_subj_r, "T1_preprocessed-down.nii.gz"), "-R", os.path.join(dir_subj_r, "mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r, "T1-down-notsu.nii.gz")]
call(command)
##merge up and down
#command=[animaImageArithmetic, "-i", os.path.join(dir_subj_r, "FLAIR-down-notsu.nii.gz"), "-a", os.path.join(dir_subj_r, "FLAIR-up-notsu.nii.gz"), "-o", os.path.join(dir_subj_r, "FLAIR-notsu.nii.gz"),"-T",nbThreads]
#call(command)
#command=[animaImageArithmetic, "-i", os.path.join(dir_subj_r, "T2-down-notsu.nii.gz"), "-a", os.path.join(dir_subj_r, "T2-up-notsu.nii.gz"), "-o", os.path.join(dir_subj_r, "T2-notsu.nii.gz"),"-T",nbThreads]
#call(command)
#command=[animaImageArithmetic, "-i", os.path.join(dir_subj_r, "T1-down-notsu.nii.gz"), "-a", os.path.join(dir_subj_r, "T1-up-notsu.nii.gz"), "-o", os.path.join(dir_subj_r, "T1-notsu.nii.gz"),"-T",nbThreads]
#call(command)    

#increase contrast
#command=[animaImageArithmetic, "-i", os.path.join(dir_subj_r,"FLAIR-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "FLAIR-notsu.nii.gz"), "-o", os.path.join(dir_subj_r,"flair2-notsu.nii.gz")]
#call(command)
command=[animaImageArithmetic, "-i", os.path.join(dir_subj_r,"FLAIR-up-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "FLAIR-up-notsu.nii.gz"), "-o", os.path.join(dir_subj_r,"flair2-notsu-up.nii.gz")]
call(command)
command=[animaImageArithmetic, "-i", os.path.join(dir_subj_r,"FLAIR-down-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "FLAIR-down-notsu.nii.gz"), "-o", os.path.join(dir_subj_r,"flair2-notsu-down.nii.gz")]
call(command)
#
## vectorize imgs controls
#for counter in range(1,21):
#    command=[animaVectorizeImages, "-i", os.path.join(dir_subj_r, "FLAIR-normalized_" + str(counter) + "reg.nrrd"), "-i", os.path.join(dir_subj_r, "T2-normalized_" + str(counter) + "reg.nrrd"), "-o", os.path.join(dir_subj_r, "FLAIR_T2-normalized_" + str(counter) + "reg.nrrd")]
#    call(command)
#    command=[animaImageArithmetic, "-i", os.path.join(dir_subj_r,"FLAIR-normalized_" + str(counter) + "reg.nrrd"), "-m", os.path.join(dir_subj_r, "FLAIR-normalized_" + str(counter) + "reg.nrrd"), "-o", os.path.join(dir_subj_r, "FLAIR2-normalized_" + str(counter) + "reg.nrrd")]
#    call(command)
#    
## vectorize img subj
#command=[animaVectorizeImages, "-i", os.path.join(dir_subj_r, "FLAIR-notsu.nii.gz"), "-i", os.path.join(dir_subj_r, "T2-notsu.nii.gz"), "-o", os.path.join(dir_subj_r, "FLAIR_T2-notsu.nii.gz")]
#call(command)
#
#a = open(os.path.join(dir_subj_r,"FLAIR-normalized-reg.txt"), "w")
#for controlFLAIR in os.listdir(dir_subj_r):
#    if 'FLAIR-normalized_' in os.path.splitext(controlFLAIR)[0]:
#        f = os.path.join(dir_subj_r, controlFLAIR)
#        a.write(str(f) + os.linesep) 
#a.close()        
#        
#b = open(os.path.join(dir_subj_r,"T2-normalized-reg.txt"), "w")
#for controlFLAIR in os.listdir(dir_subj_r):
#    if 'T2-normalized_' in os.path.splitext(controlFLAIR)[0] and 'FLAIR' not in os.path.splitext(controlFLAIR)[0]:
#        f = os.path.join(dir_subj_r, controlFLAIR)
#        b.write(str(f) + os.linesep) 
#b.close()
#
#c = open(os.path.join(dir_subj_r,"FLAIR-T2-normalized-reg.txt"), "w")
#for controlFLAIR in os.listdir(dir_subj_r):
#    if 'FLAIR_T2-normalized_' in os.path.splitext(controlFLAIR)[0]:
#        f = os.path.join(dir_subj_r, controlFLAIR)
#        c.write(str(f) + os.linesep) 
#c.close()
#
#d = open(os.path.join(dir_subj_r,"FLAIR2-normalized-reg.txt"), "w")
#for controlFLAIR in os.listdir(dir_subj_r):
#    if 'FLAIR2-normalized_' in os.path.splitext(controlFLAIR)[0]:
#        f = os.path.join(dir_subj_r, controlFLAIR)
#        d.write(str(f) + os.linesep) 
#d.close()


## patient to group comparison
#command=[animaPatientToGroupComparison, "-I", os.path.join(dir_subj_r,"FLAIR-normalized-reg.txt"), "-i", os.path.join(dir_subj_r, "FLAIR-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "mask-int.nii.gz"), "-o", os.path.join(dir_subj_r,"flair-zsc.nii.gz"), "-O", os.path.join(dir_subj_r,"flair-pv.nii.gz"),"-p", nbThreads]
#call(command)
#command=[animaPatientToGroupComparison, "-I", os.path.join(dir_subj_r,"T2-normalized-reg.txt"), "-i", os.path.join(dir_subj_r, "T2-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "mask-int.nii.gz"), "-o", os.path.join(dir_subj_r,"t2-zsc.nii.gz"), "-O", os.path.join(dir_subj_r,"t2-pv.nii.gz"),"-p", nbThreads]
#call(command)
#command=[animaPatientToGroupComparison, "-I", os.path.join(dir_subj_r,"FLAIR-T2-normalized-reg.txt"), "-i", os.path.join(dir_subj_r, "FLAIR_T2-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "mask-int.nii.gz"), "-o", os.path.join(dir_subj_r,"flair-t2-zsc.nii.gz"), "-O", os.path.join(dir_subj_r,"flair-t2-pv.nii.gz"),"-p", nbThreads]
#call(command)
##UP
#command=[animaPatientToGroupComparison, "-I", os.path.join(dir_subj_r,"FLAIR2-normalized-reg.txt"), "-i", os.path.join(dir_subj_r, "flair2-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r,"flair2-up-zsc.nii.gz"), "-O", os.path.join(dir_subj_r,"flair2-up-pv.nii.gz"),"-p", nbThreads]
#call(command)
#command=[animaPatientToGroupComparison, "-I", os.path.join(dir_subj_r,"FLAIR-normalized-reg.txt"), "-i", os.path.join(dir_subj_r, "FLAIR-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r,"flair-up-zsc.nii.gz"), "-O", os.path.join(dir_subj_r,"flair-up-pv.nii.gz"),"-p", nbThreads]
#call(command)
#command=[animaPatientToGroupComparison, "-I", os.path.join(dir_subj_r,"T2-normalized-reg.txt"), "-i", os.path.join(dir_subj_r, "T2-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r,"t2-up-zsc.nii.gz"), "-O", os.path.join(dir_subj_r,"t2-up-pv.nii.gz"),"-p", nbThreads]
#call(command)
#command=[animaPatientToGroupComparison, "-I", os.path.join(dir_subj_r,"FLAIR-T2-normalized-reg.txt"), "-i", os.path.join(dir_subj_r, "FLAIR_T2-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r,"flair-t2-up-zsc.nii.gz"), "-O", os.path.join(dir_subj_r,"flair-t2-up-pv.nii.gz"),"-p", nbThreads]
#call(command)
##DOWN
#command=[animaPatientToGroupComparison, "-I", os.path.join(dir_subj_r,"FLAIR2-normalized-reg.txt"), "-i", os.path.join(dir_subj_r, "flair2-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r,"flair2-down-zsc.nii.gz"), "-O", os.path.join(dir_subj_r,"flair2-down-pv.nii.gz"),"-p", nbThreads]
#call(command)
#command=[animaPatientToGroupComparison, "-I", os.path.join(dir_subj_r,"FLAIR-normalized-reg.txt"), "-i", os.path.join(dir_subj_r, "FLAIR-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r,"flair-down-zsc.nii.gz"), "-O", os.path.join(dir_subj_r,"flair-down-pv.nii.gz"),"-p", nbThreads]
#call(command)
#command=[animaPatientToGroupComparison, "-I", os.path.join(dir_subj_r,"T2-normalized-reg.txt"), "-i", os.path.join(dir_subj_r, "T2-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r,"t2-down-zsc.nii.gz"), "-O", os.path.join(dir_subj_r,"t2-down-pv.nii.gz"),"-p", nbThreads]
#call(command)
#command=[animaPatientToGroupComparison, "-I", os.path.join(dir_subj_r,"FLAIR-T2-normalized-reg.txt"), "-i", os.path.join(dir_subj_r, "FLAIR_T2-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r,"flair-t2-down-zsc.nii.gz"), "-O", os.path.join(dir_subj_r,"flair-t2-down-pv.nii.gz"),"-p", nbThreads]
#call(command)
#
#
##correct p-values
#command=[animaFDRCorrectPValues, "-i", os.path.join(dir_subj_r,"flair-pv.nii.gz"), "-o", os.path.join(dir_subj_r,"flair-pv-corrected.nii.gz"), "-q", "0.05", "-m", os.path.join(dir_subj_r, "mask-int.nii.gz")]
#call(command)
#command=[animaFDRCorrectPValues, "-i", os.path.join(dir_subj_r,"t2-pv.nii.gz"), "-o", os.path.join(dir_subj_r,"t2-pv-corrected.nii.gz"), "-q", "0.05", "-m", os.path.join(dir_subj_r, "mask-int.nii.gz")]
#call(command)
#command=[animaFDRCorrectPValues, "-i", os.path.join(dir_subj_r,"flair-t2-pv.nii.gz"), "-o", os.path.join(dir_subj_r,"flair-t2-pv-corrected.nii.gz"), "-q", "0.05", "-m", os.path.join(dir_subj_r, "mask-int.nii.gz")]
#call(command)
##UP
#command=[animaFDRCorrectPValues, "-i", os.path.join(dir_subj_r,"flair2-up-pv.nii.gz"), "-o", os.path.join(dir_subj_r,"flair2-up-pv-corrected.nii.gz"), "-q", "0.05", "-m", os.path.join(dir_subj_r, "mask-up-int.nii.gz")]
#call(command)
#command=[animaFDRCorrectPValues, "-i", os.path.join(dir_subj_r,"flair-up-pv.nii.gz"), "-o", os.path.join(dir_subj_r,"flair-up-pv-corrected.nii.gz"), "-q", "0.05", "-m", os.path.join(dir_subj_r, "mask-up-int.nii.gz")]
#call(command)
#command=[animaFDRCorrectPValues, "-i", os.path.join(dir_subj_r,"t2-up-pv.nii.gz"), "-o", os.path.join(dir_subj_r,"t2-up-pv-corrected.nii.gz"), "-q", "0.05", "-m", os.path.join(dir_subj_r, "mask-up-int.nii.gz")]
#call(command)
#command=[animaFDRCorrectPValues, "-i", os.path.join(dir_subj_r,"flair-t2-up-pv.nii.gz"), "-o", os.path.join(dir_subj_r,"flair-t2-up-pv-corrected.nii.gz"), "-q", "0.05", "-m", os.path.join(dir_subj_r, "mask-up-int.nii.gz")]
#call(command)
##DOWN
#command=[animaFDRCorrectPValues, "-i", os.path.join(dir_subj_r,"flair2-down-pv.nii.gz"), "-o", os.path.join(dir_subj_r,"flair2-down-pv-corrected.nii.gz"), "-q", "0.05", "-m", os.path.join(dir_subj_r, "mask-down-int.nii.gz")]
#call(command)
#command=[animaFDRCorrectPValues, "-i", os.path.join(dir_subj_r,"flair-down-pv.nii.gz"), "-o", os.path.join(dir_subj_r,"flair-down-pv-corrected.nii.gz"), "-q", "0.05", "-m", os.path.join(dir_subj_r, "mask-down-int.nii.gz")]
#call(command)
#command=[animaFDRCorrectPValues, "-i", os.path.join(dir_subj_r,"flair-t2-down-pv.nii.gz"), "-o", os.path.join(dir_subj_r,"flair-t2-down-pv-corrected.nii.gz"), "-q", "0.05", "-m", os.path.join(dir_subj_r, "mask-down-int.nii.gz")]
#call(command)
#command=[animaFDRCorrectPValues, "-i", os.path.join(dir_subj_r,"t2-down-pv.nii.gz"), "-o", os.path.join(dir_subj_r,"t2-down-pv-corrected.nii.gz"), "-q", "0.05", "-m", os.path.join(dir_subj_r, "mask-down-int.nii.gz")]
#call(command)
#
#
##positive zsc only
##UP
#command=[animaThrImage, "-i", os.path.join(dir_subj_r, "flair2-up-zsc.nii.gz"), "-t", "0", "-o", os.path.join(dir_subj_r, "flair2-up-zsc-pos.nii.gz")]
#call(command) 
#command=[animaThrImage, "-i", os.path.join(dir_subj_r, "flair-up-zsc.nii.gz"), "-t", "0", "-o", os.path.join(dir_subj_r, "flair-up-zsc-pos.nii.gz")]
#call(command)   
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r, "flair-up-pv-corrected.nii.gz"), "-m",  os.path.join(dir_subj_r, "flair-up-zsc-pos.nii.gz"), "-o", os.path.join(dir_subj_r, "flair-up-pv-corrected-posz.nii.gz")]
#call(command)
#command=[animaThrImage, "-i", os.path.join(dir_subj_r, "t2-up-zsc.nii.gz"), "-t", "0", "-o", os.path.join(dir_subj_r, "t2-up-zsc-pos.nii.gz")]
#call(command)   
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r, "t2-up-pv-corrected.nii.gz"), "-m",  os.path.join(dir_subj_r, "t2-up-zsc-pos.nii.gz"), "-o", os.path.join(dir_subj_r, "t2-up-pv-corrected-posz.nii.gz")]
#call(command)
#command=[animaThrImage, "-i", os.path.join(dir_subj_r, "flair-t2-up-zsc.nii.gz"), "-t", "0", "-o", os.path.join(dir_subj_r, "flair-t2-up-zsc-pos.nii.gz")]
#call(command)   
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r, "flair-t2-up-pv-corrected.nii.gz"), "-m",  os.path.join(dir_subj_r, "flair-t2-up-zsc-pos.nii.gz"), "-o", os.path.join(dir_subj_r, "flair-t2-up-pv-corrected-posz.nii.gz")]
#call(command)
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r, "flair2-up-pv-corrected.nii.gz"), "-m",  os.path.join(dir_subj_r, "flair2-up-zsc-pos.nii.gz"), "-o", os.path.join(dir_subj_r, "flair2-up-pv-corrected-posz.nii.gz")]
#call(command)
##DOWN
#command=[animaThrImage, "-i", os.path.join(dir_subj_r, "flair2-down-zsc.nii.gz"), "-t", "0", "-o", os.path.join(dir_subj_r, "flair2-down-zsc-pos.nii.gz")]
#call(command) 
#command=[animaThrImage, "-i", os.path.join(dir_subj_r, "flair-down-zsc.nii.gz"), "-t", "0", "-o", os.path.join(dir_subj_r, "flair-down-zsc-pos.nii.gz")]
#call(command)   
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r, "flair-down-pv-corrected.nii.gz"), "-m",  os.path.join(dir_subj_r, "flair-down-zsc-pos.nii.gz"), "-o", os.path.join(dir_subj_r, "flair-down-pv-corrected-posz.nii.gz")]
#call(command)
#command=[animaThrImage, "-i", os.path.join(dir_subj_r, "t2-down-zsc.nii.gz"), "-t", "0", "-o", os.path.join(dir_subj_r, "t2-down-zsc-pos.nii.gz")]
#call(command)  
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r, "t2-down-pv-corrected.nii.gz"), "-m",  os.path.join(dir_subj_r, "t2-down-zsc-pos.nii.gz"), "-o", os.path.join(dir_subj_r, "t2-down-pv-corrected-posz.nii.gz")]
#call(command)
#command=[animaThrImage, "-i", os.path.join(dir_subj_r, "flair-t2-down-zsc.nii.gz"), "-t", "0", "-o", os.path.join(dir_subj_r, "flair-t2-down-zsc-pos.nii.gz")]
#call(command)   
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r, "flair-t2-down-pv-corrected.nii.gz"), "-m",  os.path.join(dir_subj_r, "flair-t2-down-zsc-pos.nii.gz"), "-o", os.path.join(dir_subj_r, "flair-t2-down-pv-corrected-posz.nii.gz")]
#call(command)
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r, "flair2-down-pv-corrected.nii.gz"), "-m",  os.path.join(dir_subj_r, "flair2-down-zsc-pos.nii.gz"), "-o", os.path.join(dir_subj_r, "flair2-down-pv-corrected-posz.nii.gz")]
#call(command)


#mask atlas (for GC)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"ATLAS-wm_masked-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r, "ATLAS-wm_masked_up-reg.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"ATLAS-gm_masked-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r, "ATLAS-gm_masked_up-reg.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"ATLAS-csf_masked-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r, "ATLAS-csf_masked_up-reg.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"prob_map-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int.nii.gz"), "-o", os.path.join(dir_subj_r, "prob_map_up-reg.nii.gz")]
call(command)

command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"ATLAS-wm_masked-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r, "ATLAS-wm_masked_down-reg.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"ATLAS-gm_masked-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r, "ATLAS-gm_masked_down-reg.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"ATLAS-csf_masked-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r, "ATLAS-csf_masked_down-reg.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"prob_map-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int.nii.gz"), "-o", os.path.join(dir_subj_r, "prob_map_down-reg.nii.gz")]
call(command)


##increase contrast - for testing
#command=[animaImageArithmetic, "-i", os.path.join(dir_subj_r,"FLAIR-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "T2-notsu.nii.gz"), "-o", os.path.join(dir_subj_r,"flairt2-notsu.nii.gz")]
#call(command)
#command=[animaImageArithmetic, "-i", os.path.join(dir_subj_r,"FLAIR-up-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "T2-up-notsu.nii.gz"), "-o", os.path.join(dir_subj_r,"flairt2-notsu-up.nii.gz")]
#call(command)
#command=[animaImageArithmetic, "-i", os.path.join(dir_subj_r,"FLAIR-down-notsu.nii.gz"), "-m", os.path.join(dir_subj_r, "T2-down-notsu.nii.gz"), "-o", os.path.join(dir_subj_r,"flairt2-notsu-down.nii.gz")]
#call(command)

#mask atlas (for GC)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"ATLAS-wm_masked-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "ATLAS-wm_masked_up-reg-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"ATLAS-gm_masked-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "ATLAS-gm_masked_up-reg-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"ATLAS-csf_masked-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "ATLAS-csf_masked_up-reg-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"prob_map-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "prob_map_up-reg-bs.nii.gz")]
call(command)

command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"ATLAS-wm_masked-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "ATLAS-wm_masked_down-reg-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"ATLAS-gm_masked-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "ATLAS-gm_masked_down-reg-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"ATLAS-csf_masked-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "ATLAS-csf_masked_down-reg-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"prob_map-reg.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "prob_map_down-reg-bs.nii.gz")]
call(command)

command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"FLAIR-up-notsu.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "FLAIR-up-notsu-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"FLAIR-down-notsu.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "FLAIR-down-notsu-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"T2-up-notsu.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "T2-up-notsu-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"T2-down-notsu.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "T2-down-notsu-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"T1-up-notsu.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "T1-up-notsu-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"T1-down-notsu.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "T1-down-notsu-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"flair2-notsu-up.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "flair2-notsu-up-bs.nii.gz")]
call(command)
command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"flair2-notsu-down.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "flair2-notsu-down-bs.nii.gz")]
call(command)
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"flairt2-notsu-up.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-up-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "flairt2-notsu-up-bs.nii.gz")]
#call(command)
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"flairt2-notsu-down.nii.gz"), "-m", os.path.join(dir_subj_r,"mask-down-int-bs.nii.gz"), "-o", os.path.join(dir_subj_r, "flairt2-notsu-down-bs.nii.gz")]
#call(command)


#command=[animaOtsuThrImage, "-i", os.path.join(dir_subj_r,"FLAIR-up-notsu-bs.nii.gz"),"-o", os.path.join(dir_subj_r, "flair-notsu-up-otsu.nii.gz"), "-n", "6"]
#call(command)
#command=[animaOtsuThrImage, "-i", os.path.join(dir_subj_r,"FLAIR-down-notsu-bs.nii.gz"),"-o", os.path.join(dir_subj_r, "flair-notsu-down-otsu.nii.gz"), "-n", "6"]
#call(command)

command=[animaOtsuThrImage, "-i", os.path.join(dir_subj_r,"flair2-notsu-up-bs.nii.gz"),"-o", os.path.join(dir_subj_r, "flair2-notsu-up-otsu.nii.gz"), "-n", "6"]
call(command)
command=[animaOtsuThrImage, "-i", os.path.join(dir_subj_r,"flair2-notsu-down-bs.nii.gz"),"-o", os.path.join(dir_subj_r, "flair2-notsu-down-otsu.nii.gz"), "-n", "6"]
call(command)


#command=[animaOtsuThrImage, "-i", os.path.join(dir_subj_r,"flairt2-notsu-up-bs.nii.gz"),"-o", os.path.join(dir_subj_r, "flairt2-notsu-up-otsu.nii.gz"), "-n", "6"]
#call(command)
#command=[animaOtsuThrImage, "-i", os.path.join(dir_subj_r,"flairt2-notsu-down-bs.nii.gz"),"-o", os.path.join(dir_subj_r, "flairt2-notsu-down-otsu.nii.gz"), "-n", "6"]
#call(command)



#command=[animaThrImage, "-i", os.path.join(dir_subj_r, "ATLAS-wm_masked_up-reg-bs.nii.gz"), "-t", "0.5", "-o", os.path.join(dir_subj_r, "ATLAS-wm_masked_up-reg-bs-th.nii.gz")]
#call(command) 
#command=[animaThrImage, "-i", os.path.join(dir_subj_r, "ATLAS-wm_masked_down-reg-bs.nii.gz"), "-t", "0.9", "-o", os.path.join(dir_subj_r, "ATLAS-wm_masked_down-reg-bs-th.nii.gz")]
#call(command) 
#
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"FLAIR-up-notsu.nii.gz"), "-m", os.path.join(dir_subj_r,"ATLAS-wm_masked_up-reg-bs-th.nii.gz"), "-o", os.path.join(dir_subj_r, "FLAIR-up-notsu-bs-wm.nii.gz")]
#call(command)
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"FLAIR-down-notsu.nii.gz"), "-m", os.path.join(dir_subj_r,"ATLAS-wm_masked_down-reg-bs-th.nii.gz"), "-o", os.path.join(dir_subj_r, "FLAIR-down-notsu-bs-wm.nii.gz")]
#call(command)
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"T2-up-notsu.nii.gz"), "-m", os.path.join(dir_subj_r,"ATLAS-wm_masked_up-reg-bs-th.nii.gz"), "-o", os.path.join(dir_subj_r, "T2-up-notsu-bs-wm.nii.gz")]
#call(command)
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"T2-down-notsu.nii.gz"), "-m", os.path.join(dir_subj_r,"ATLAS-wm_masked_down-reg-bs-th.nii.gz"), "-o", os.path.join(dir_subj_r, "T2-down-notsu-bs-wm.nii.gz")]
#call(command)
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"T1-up-notsu.nii.gz"), "-m", os.path.join(dir_subj_r,"ATLAS-wm_masked_up-reg-bs-th.nii.gz"), "-o", os.path.join(dir_subj_r, "T1-up-notsu-bs-wm.nii.gz")]
#call(command)
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"T1-down-notsu.nii.gz"), "-m", os.path.join(dir_subj_r,"ATLAS-wm_masked_down-reg-bs-th.nii.gz"), "-o", os.path.join(dir_subj_r, "T1-down-notsu-bs-wm.nii.gz")]
#call(command)
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"flair2-notsu-up.nii.gz"), "-m", os.path.join(dir_subj_r,"ATLAS-wm_masked_up-reg-bs-th.nii.gz"), "-o", os.path.join(dir_subj_r, "flair2-notsu-up-bs-wm.nii.gz")]
#call(command)
#command=[animaMaskImage, "-i", os.path.join(dir_subj_r,"flair2-notsu-down.nii.gz"), "-m", os.path.join(dir_subj_r,"ATLAS-wm_masked_down-reg-bs-th.nii.gz"), "-o", os.path.join(dir_subj_r, "flair2-notsu-down-bs-wm.nii.gz")]
#call(command)

