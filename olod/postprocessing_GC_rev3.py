# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 10:24:42 2018

@author: fgalassi
"""

#!/usr/bin/python
import itertools
import nibabel as nib
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
atlasDir = "/temp_dd/igrida-fs1/fgalassi/Anima-Scripts_data/uspio-atlas"

parser = argparse.ArgumentParser(
    prog = 'postprocessing',
    formatter_class = argparse.RawDescriptionHelpFormatter)

parser.add_argument('-i','--dir_subj',required=True,help='')
parser.add_argument('-o','--dir_out',required=True,help='')
parser.add_argument('-T','--nbThreads',required=False,type=int,help='Number of execution threads (default: 0 = all cores)',default=0)

args = parser.parse_args()

nbThreads=str(args.nbThreads)
dir_subj = args.dir_subj
dir_results = args.dir_out

#anima tools - some not used
animaConvertImage=os.path.join(animaDir,"animaConvertImage")
animaVectorizeImages=os.path.join(animaDir,"animaVectorizeImages")
animaPatientToGroupComparison=os.path.join(animaDir,"animaPatientToGroupComparison")
animaNotsuStandardization=os.path.join(animaDir,"animaNotsuStandardization")
animaMaskImage=os.path.join(animaDir,"animaMaskImage")
animaFDRCorrectPValues=os.path.join(animaDir,"animaFDRCorrectPValues")
animaConvertImage=os.path.join(animaDir,"animaConvertImage")
animaThrImage=os.path.join(animaDir,"animaThrImage")
animaApplyTransformSerie=os.path.join(animaDir,"animaApplyTransformSerie")
animaImageArithmetic=os.path.join(animaDir,"animaImageArithmetic")
animaPyramidalBMRegistration=os.path.join(animaDir,"animaPyramidalBMRegistration")
animaTransformSerieXmlGenerator=os.path.join(animaDir,"animaTransformSerieXmlGenerator")
animaApplyTransformSerie=os.path.join(animaDir,"animaApplyTransformSerie")
animaDenseSVFBMRegistration=os.path.join(animaDir,"animaDenseSVFBMRegistration")
animaConnectedComponents=os.path.join(animaDir,"animaConnectedComponents")
animaInfluenceZones=os.path.join(animaDir,"animaInfluenceZones")
animaRemoveTouchingBorder=os.path.join(animaDir,"animaRemoveTouchingBorder")
animaOtsuThrImage = os.path.join(animaDir,"animaOtsuThrImage")
animaFillHoleImage = os.path.join(animaDir,"animaFillHoleImage")
animaImageSmoother = os.path.join(animaDir,"animaImageSmoother")


#UP
# thresh wm gm csf
command=[animaThrImage, "-i", os.path.join(dir_results,'ATLAS-wm_masked_up-reg-bs.nii.gz'), "-t", "0.1" ,"-o", os.path.join(dir_results,'ATLAS-wm_mask_up-reg-bs-wm.nii.gz')]
call(command)
command=[animaThrImage, "-i", os.path.join(dir_results,'ATLAS-csf_masked_up-reg-bs.nii.gz'), "-t", "0.8" ,"-o", os.path.join(dir_results,'ATLAS-csf_mask_up-reg-bs-wm.nii.gz')]
call(command)
command=[animaThrImage, "-i", os.path.join(dir_results,'ATLAS-gm_masked_up-reg-bs.nii.gz'), "-t", "0.2" ,"-o", os.path.join(dir_results,'ATLAS-gm_mask_up-reg-bs-wm.nii.gz')]
call(command)
# otsu thr flair2
command=[animaThrImage, "-i", os.path.join(dir_results,"flair2-notsu-up-otsu.nii.gz"),"-o", os.path.join(dir_results, "flair2-notsu-up-otsu-6.nii.gz"), "-t", "6"]
call(command)

# remove les in csf and gm & keep wm lesions
segm_img1 = nib.load(os.path.join(dir_results, "segm-ini0-pr-flair-up.nii.gz")); segm1 = segm_img1.get_data(); 
values1 = segm_img1.shape;
mask_wm_img = nib.load(os.path.join(dir_results, "ATLAS-wm_mask_up-reg-bs-wm.nii.gz")); mask_wm = mask_wm_img.get_data();
mask_csf_img = nib.load(os.path.join(dir_results, "ATLAS-csf_mask_up-reg-bs-wm.nii.gz")); mask_csf = mask_csf_img.get_data();
mask_gm_img = nib.load(os.path.join(dir_results, "ATLAS-gm_mask_up-reg-bs-wm.nii.gz")); mask_gm = mask_gm_img.get_data();
for i, j, k in itertools.product(*map(xrange, values1)):
    if (mask_csf[i, j, k] == 1) or (mask_gm[i, j, k] == 1) or (mask_wm[i, j, k] == 0):
       segm1[i, j, k] = 0
nib.save(nib.Nifti1Image(segm1, segm_img1.affine), os.path.join(dir_results,"segm-csf.nii.gz")); 

# remove les touching outer mask border
command=[animaInfluenceZones, "-i", os.path.join(dir_results,'segm-csf.nii.gz'), "-o", os.path.join(dir_results,'segm-wm-les-label1.nii.gz')]
call(command)
command=[animaRemoveTouchingBorder, "-i", os.path.join(dir_results,'segm-wm-les-label1.nii.gz'), "-m", os.path.join(dir_subj, "mask-up-int-bs.nii.gz"), "-o", os.path.join(dir_results,'segm-wm-les-label1.nii.gz'), "-L", "-T", nbThreads]
call(command)
# remove small lesions
command=[animaConnectedComponents, "-i", os.path.join(dir_results,'segm-wm-les-label1.nii.gz'), "-m", "12", "-o", os.path.join(dir_results,'segm-wm-les-label-conn1.nii.gz')]
call(command)
command=[animaThrImage, "-i", os.path.join(dir_results,'segm-wm-les-label-conn1.nii.gz'), "-t", "0", "-o", os.path.join(dir_results,'segm-wm-les-label-conn-thr1.nii.gz')]
call(command)
# fill lesions
command=[animaFillHoleImage, "-i", os.path.join(dir_results,'segm-wm-les-label-conn-thr1.nii.gz'), "-o", os.path.join(dir_results,'segm-wm-les-label-conn-thr-fh1.nii.gz')]
call(command)    
# final output
command=[animaThrImage, "-i", os.path.join(dir_results,'segm-wm-les-label-conn-thr-fh1.nii.gz'), "-t", "0", "-o", os.path.join(dir_results,'segm-ini0-pr-flair-up-PP.nii.gz')]
call(command)



#DOWN
# thresh wm gm csf
command=[animaThrImage, "-i", os.path.join(dir_results,'ATLAS-wm_masked_down-reg-bs.nii.gz'), "-t", "0.8" ,"-o", os.path.join(dir_results,'ATLAS-wm_mask_down-reg-bs-wm-t.nii.gz')]
call(command)
command=[animaThrImage, "-i", os.path.join(dir_results,'ATLAS-csf_masked_down-reg-bs.nii.gz'), "-t", "0.001" ,"-o", os.path.join(dir_results,'ATLAS-csf_mask_down-reg-bs-wm-t.nii.gz')]
call(command)
command=[animaThrImage, "-i", os.path.join(dir_results,'ATLAS-gm_masked_down-reg-bs.nii.gz'), "-t", "0.01" ,"-o", os.path.join(dir_results,'ATLAS-gm_mask_down-reg-bs-wm-t.nii.gz')]
call(command)
# otsu thr flair2
command=[animaThrImage, "-i", os.path.join(dir_results,"flair2-notsu-down-otsu.nii.gz"),"-o", os.path.join(dir_results, "flair2-notsu-down-otsu-5.nii.gz"), "-t", "5"]
call(command)

# remove les in csf and gm & keep wm lesions in flair2 otsu thr
mask_wm_img_t = nib.load(os.path.join(dir_results, "ATLAS-wm_mask_down-reg-bs-wm-t.nii.gz")); mask_wm_t = mask_wm_img_t.get_data();
mask_csf_img_t = nib.load(os.path.join(dir_results, "ATLAS-csf_mask_down-reg-bs-wm-t.nii.gz")); mask_csf_t = mask_csf_img_t.get_data();
mask_gm_img_t = nib.load(os.path.join(dir_results, "ATLAS-gm_mask_down-reg-bs-wm-t.nii.gz")); mask_gm_t = mask_gm_img_t.get_data();
segm_img1 = nib.load(os.path.join(dir_results, "flair2-notsu-down-otsu-5.nii.gz")); segm1 = segm_img1.get_data(); 
values1 = segm_img1.shape;
for i, j, k in itertools.product(*map(xrange, values1)):
    if (mask_csf_t[i, j, k] == 1) or (mask_gm_t[i, j, k] == 1) or (mask_wm_t[i, j, k] == 0):
       segm1[i, j, k] = 0
nib.save(nib.Nifti1Image(segm1, segm_img1.affine), os.path.join(dir_results,"flair2-notsu-down-otsu-5-t.nii.gz")); 
# remove small lesions from flair2 contrast in the wm
command=[animaConnectedComponents, "-i", os.path.join(dir_results,'flair2-notsu-down-otsu-5-t.nii.gz'), "-m", "27", "-o", os.path.join(dir_results,'flair2-notsu-down-otsu-5-wm-t-conn1.nii.gz')]
call(command)
command=[animaThrImage, "-i", os.path.join(dir_results,'flair2-notsu-down-otsu-5-wm-t-conn1.nii.gz'), "-t", "0", "-o", os.path.join(dir_results,'flair2-notsu-down-otsu-5-wm-t.nii.gz')]
call(command)

# add hyperintensities from flair2 otsu thr
segm_img1 = nib.load(os.path.join(dir_results, "segm-ini0-pr-flair-down.nii.gz")); segm1 = segm_img1.get_data(); 
values1 = segm_img1.shape;
segm_img2 = nib.load(os.path.join(dir_results, "flair2-notsu-down-otsu-5-wm-t.nii.gz")); segm2 = segm_img2.get_data();
for i, j, k in itertools.product(*map(xrange, values1)):
    if (segm2[i, j, k]) == 1 :
       segm1[i, j, k] = 1
nib.save(nib.Nifti1Image(segm1, segm_img1.affine), os.path.join(dir_results,"segm.nii.gz")); 
# remove lesions in csf and gm - keep wm lesions
mask_wm_img = nib.load(os.path.join(dir_results, "ATLAS-wm_mask_down-reg-bs-wm-t.nii.gz")); mask_wm = mask_wm_img.get_data();
mask_csf_img = nib.load(os.path.join(dir_results, "ATLAS-csf_mask_down-reg-bs-wm-t.nii.gz")); mask_csf = mask_csf_img.get_data();
mask_gm_img = nib.load(os.path.join(dir_results, "ATLAS-gm_mask_down-reg-bs-wm-t.nii.gz")); mask_gm = mask_gm_img.get_data();
for i, j, k in itertools.product(*map(xrange, values1)):
    if (mask_csf[i, j, k] == 1) or (mask_gm[i, j, k] == 1) or (mask_wm[i, j, k] == 0):
       segm1[i, j, k] = 0
nib.save(nib.Nifti1Image(segm1, segm_img1.affine), os.path.join(dir_results,"segm-csf.nii.gz")); 

# remove les touching outer wm mask border
command=[animaInfluenceZones, "-i", os.path.join(dir_results,'segm-csf.nii.gz'), "-o", os.path.join(dir_results,'segm-wm-les-label1.nii.gz')]
call(command)
command=[animaRemoveTouchingBorder, "-i", os.path.join(dir_results,'segm-wm-les-label1.nii.gz'), "-m", os.path.join(dir_subj, "ATLAS-wm_mask_down-reg-bs-wm-t.nii.gz"), "-o", os.path.join(dir_results,'segm-wm-les-label1.nii.gz'), "-L", "-T", nbThreads]
call(command)
# remove small lesions
command=[animaConnectedComponents, "-i", os.path.join(dir_results,'segm-wm-les-label1.nii.gz'), "-m", "9", "-o", os.path.join(dir_results,'segm-wm-les-label-conn1.nii.gz')]
call(command)
command=[animaThrImage, "-i", os.path.join(dir_results,'segm-wm-les-label-conn1.nii.gz'), "-t", "0", "-o", os.path.join(dir_results,'segm-wm-les-label-conn-thr1.nii.gz')]
call(command)
# fill lesions
command=[animaFillHoleImage, "-i", os.path.join(dir_results,'segm-wm-les-label-conn-thr1.nii.gz'), "-o", os.path.join(dir_results,'segm-wm-les-label-conn-thr-fh1.nii.gz')]
call(command)    
# final output
command=[animaThrImage, "-i", os.path.join(dir_results,'segm-wm-les-label-conn-thr-fh1.nii.gz'), "-t", "0", "-o", os.path.join(dir_results,'segm-ini0-pr-flair-down-PP.nii.gz')]
call(command)


