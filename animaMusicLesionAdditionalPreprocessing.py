#!/usr/bin/python

import os
from subprocess import call, check_output


# Data additional preprocessing, uses as inputs the preprocessed images from animaMSExamRegistration.py
def music_lesion_additional_preprocessing(animaDir,animaExtraDataDir,tmpFolder,t1Image,t2Image,flairImage,maskImage,nbThreads):

    # Anima commands
    animaPyramidalBMRegistration = os.path.join(animaDir,"animaPyramidalBMRegistration")
    animaApplyTransformSerie = os.path.join(animaDir,"animaApplyTransformSerie")
    animaMaskImage = os.path.join(animaDir,"animaMaskImage")
    animaTransformSerieXmlGenerator = os.path.join(animaDir,"animaTransformSerieXmlGenerator")
    animaDenseSVFBMRegistration = os.path.join(animaDir,"animaDenseSVFBMRegistration")
    animaKMeansStandardization = os.path.join(animaDir,"animaKMeansStandardization")
    animaImageArithmetic = os.path.join(animaDir,"animaImageArithmetic")
    animaConvertImage = os.path.join(animaDir,"animaConvertImage")

    # Atlases
    olivierAtlasDir = os.path.join(animaExtraDataDir,"olivier-atlas")
    olivierAtlasImageMasked = os.path.join(olivierAtlasDir,"ATLAS-masked.nrrd")
    olivierAtlasMask = os.path.join(olivierAtlasDir,"ATLAS-mask.nrrd")
    olivierAtlasMask_up = os.path.join(olivierAtlasDir,"ATLAS-mask-cropped.nrrd")
    olivierAtlasMask_down = os.path.join(olivierAtlasDir,"ATLAS-mask-down.nrrd")

    uspioAtlasDir = os.path.join(animaExtraDataDir,"uspio-atlas")
    uspioAtlasDir_T1 = os.path.join(uspioAtlasDir,"scalar-space","T1")
    uspioAtlasDir_T2 = os.path.join(uspioAtlasDir,"scalar-space","T2")
    uspioAtlasDir_FLAIR = os.path.join(uspioAtlasDir,"scalar-space","FLAIR")
    uspioAtlasDir_RefSpace = os.path.join(uspioAtlasDir,"scalar-space","space-ref")

    # Decide on whether to use large image setting or small image setting
    command = [animaConvertImage, "-i", t1Image, "-I"]
    convert_output = check_output(command, universal_newlines=True)
    size_info = convert_output.split('\n')[1].split('[')[1].split(']')[0]
    large_image = False
    for i in range(0, 3):
        size_tmp = int(size_info.split(', ')[i])
        if size_tmp >= 256:
            large_image = True
            break

    pyramidOptions = ["-p", "4", "-l", "1"]
    if large_image:
        pyramidOptions = ["-p", "5", "-l", "2"]

    # Register olivier atlas to T1 image
    command = [animaPyramidalBMRegistration,"-m",olivierAtlasImageMasked,"-r",t1Image,"-o",os.path.join(tmpFolder,"atlas_rig.nrrd"),"-O",os.path.join(tmpFolder,"atlas_rig_tr.txt"),"--sp","3","-T",nbThreads] + pyramidOptions
    call(command)
    command = [animaPyramidalBMRegistration,"-m",olivierAtlasImageMasked,"-r",t1Image,"-o",os.path.join(tmpFolder,"atlas_aff.nrrd"),"-O",os.path.join(tmpFolder,"atlas_aff_tr.txt"),
               "-i",os.path.join(tmpFolder,"atlas_rig_tr.txt"),"--sp","3","--ot","2","-T",nbThreads] + pyramidOptions
    call(command)
    command = [animaDenseSVFBMRegistration,"-r",t1Image,"-m",os.path.join(tmpFolder,"atlas_aff.nrrd"),"-o",os.path.join(tmpFolder,"atlas_nl.nrrd"),"-O",os.path.join(tmpFolder,"atlas_nl_tr.nrrd"),"--sr","1","-T",nbThreads] + pyramidOptions
    call(command)
    command = [animaTransformSerieXmlGenerator,"-i",os.path.join(tmpFolder,"atlas_aff_tr.txt"),"-i",os.path.join(tmpFolder,"atlas_nl_tr.nrrd"),"-o",os.path.join(tmpFolder,"atlas_nl_tr.xml")]
    call(command)
    command = [animaApplyTransformSerie,"-i",olivierAtlasImageMasked,"-t",os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g",t1Image,"-o",os.path.join(tmpFolder,"atlasImage_registered.nrrd"),"-p",nbThreads]
    call(command)

    # Apply transform to olivier atlas mask plus up and down
    command = [animaApplyTransformSerie,"-i",olivierAtlasMask,"-t", os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g", t1Image,"-o", os.path.join(tmpFolder,"mask.nrrd"),"-n","nearest","-p",nbThreads]
    call(command)
    command = [animaApplyTransformSerie,"-i",olivierAtlasMask_up,"-t", os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g", t1Image,"-o", os.path.join(tmpFolder,"mask-up.nrrd"),"-n","nearest","-p",nbThreads]
    call(command)
    command = [animaApplyTransformSerie,"-i",olivierAtlasMask_down,"-t", os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g", t1Image,"-o", os.path.join(tmpFolder,"mask-down.nrrd"),"-n","nearest","-p",nbThreads]
    call(command)

    # intersect olivier mask, mask up and down
    command = [animaMaskImage, "-i", maskImage, "-m",os.path.join(tmpFolder,"mask.nrrd"), "-o", os.path.join(tmpFolder,"mask.nrrd")]
    call(command)
    command = [animaMaskImage, "-i", maskImage, "-m",os.path.join(tmpFolder,"mask-up.nrrd"), "-o", os.path.join(tmpFolder,"mask-up.nrrd")]
    call(command)
    command = [animaMaskImage, "-i", maskImage, "-m",os.path.join(tmpFolder,"mask-down.nrrd"), "-o", os.path.join(tmpFolder,"mask-down.nrrd")]
    call(command)

    # register wm, gm, csf maps, les prob map
    command = [animaApplyTransformSerie,"-i", os.path.join(olivierAtlasDir, "ATLAS-wm_masked.nrrd"),"-t", os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g", t1Image, "-o", os.path.join(tmpFolder,"ATLAS-wm_masked-reg.nrrd")]
    call(command)
    command = [animaApplyTransformSerie,"-i", os.path.join(olivierAtlasDir, "ATLAS-gm_masked.nrrd"),"-t", os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g", t1Image, "-o", os.path.join(tmpFolder,"ATLAS-gm_masked-reg.nrrd")]
    call(command)
    command = [animaApplyTransformSerie,"-i", os.path.join(olivierAtlasDir, "ATLAS-csf_masked.nrrd"),"-t", os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g", t1Image, "-o", os.path.join(tmpFolder, "ATLAS-csf_masked-reg.nrrd")]
    call(command)
    command = [animaApplyTransformSerie,"-i", os.path.join(olivierAtlasDir, "prob_map_lesions_MS-SPI_MICCAI_normalized_masked.nrrd"),"-t", os.path.join(tmpFolder,"atlas_nl_tr.xml"),"-g", t1Image, "-o", os.path.join(tmpFolder, "prob_map-reg.nrrd")]
    call(command)

    # apply mask, mask  up and down to  wm, gm, csf maps, les prob map
    command = [animaMaskImage, "-i", os.path.join(tmpFolder,"atlasImage_registered.nrrd"), "-m", os.path.join(tmpFolder,"mask.nrrd"), "-o", os.path.join(tmpFolder, "atlasImage_registered.nrrd")]
    call(command)
    command = [animaMaskImage, "-i", os.path.join(tmpFolder,"ATLAS-wm_masked-reg.nrrd"), "-m", os.path.join(tmpFolder,"mask.nrrd"), "-o", os.path.join(tmpFolder, "ATLAS-wm_masked-reg.nrrd")]
    call(command)
    command = [animaMaskImage, "-i", os.path.join(tmpFolder,"ATLAS-csf_masked-reg.nrrd"), "-m", os.path.join(tmpFolder,"mask.nrrd"), "-o", os.path.join(tmpFolder, "ATLAS-csf_masked-reg.nrrd")]
    call(command)
    command = [animaMaskImage, "-i", os.path.join(tmpFolder,"ATLAS-gm_masked-reg.nrrd"), "-m", os.path.join(tmpFolder,"mask.nrrd"), "-o", os.path.join(tmpFolder, "ATLAS-gm_masked-reg.nrrd")]
    call(command)
    command = [animaMaskImage, "-i", os.path.join(tmpFolder,"prob_map-reg.nrrd"), "-m", os.path.join(tmpFolder,"mask.nrrd"), "-o", os.path.join(tmpFolder, "prob_map-reg.nrrd")]
    call(command)

    # Now take care of uspio atlas and normalize
    # register FLAIR template to FLAIR img
    command = [animaMaskImage, "-i", flairImage, "-m", os.path.join(tmpFolder, "mask.nrrd"), "-o", os.path.join(tmpFolder, "FLAIR_preprocessed.nrrd")]
    call(command)
    command = [animaPyramidalBMRegistration,"-m",os.path.join(uspioAtlasDir_RefSpace,"FLAIR_averaged.nrrd"),"-r",
               os.path.join(tmpFolder,"FLAIR_preprocessed.nrrd"), "-o", os.path.join(tmpFolder,"avg_rig.nrrd"),"-O",
               os.path.join(tmpFolder,"avg_rig_tr.txt"),"--sp","3","-T", nbThreads] + pyramidOptions
    call(command)
    command = [animaPyramidalBMRegistration,"-m",os.path.join(uspioAtlasDir_RefSpace,"FLAIR_averaged.nrrd"),"-r",
               os.path.join(tmpFolder,"FLAIR_preprocessed.nrrd"),"-o", os.path.join(tmpFolder,"avg_aff.nrrd"),"-O",
               os.path.join(tmpFolder,"avg_aff_tr.txt"),"-i",os.path.join(tmpFolder, "avg_rig_tr.txt"),"--sp","3",
               "--ot","2","-T", nbThreads] + pyramidOptions
    call(command)
    command = [animaDenseSVFBMRegistration,"-r",os.path.join(tmpFolder,"FLAIR_preprocessed.nrrd"),"-m",
               os.path.join(tmpFolder,"avg_aff.nrrd"),"-o", os.path.join(tmpFolder, "avg_nl.nrrd"),"-O",
               os.path.join(tmpFolder,"avg_nl_tr.nrrd"),"--sr","1","-T", nbThreads] + pyramidOptions
    call(command)
    command = [animaTransformSerieXmlGenerator,"-i",os.path.join(tmpFolder,"avg_aff_tr.txt"),"-i", os.path.join(tmpFolder,"avg_nl_tr.nrrd"),"-o",os.path.join(tmpFolder,"avg_nl_tr.xml")]
    call(command)
    command = [animaApplyTransformSerie,"-i", os.path.join(uspioAtlasDir_RefSpace,"FLAIR_averaged.nrrd"),"-t", os.path.join(tmpFolder,"avg_nl_tr.xml"),"-g",os.path.join(tmpFolder,"FLAIR_preprocessed.nrrd"),"-o", os.path.join(tmpFolder, "FLAIR_averaged-reg.nrrd"),"-p", nbThreads]
    call(command)

    # apply transform to template masks
    command = [animaApplyTransformSerie,"-i", os.path.join(uspioAtlasDir_RefSpace,"brain-mask_intersected.nrrd"),"-t", os.path.join(tmpFolder,"avg_nl_tr.xml"),"-g",os.path.join(tmpFolder,"FLAIR_preprocessed.nrrd"),"-o",  os.path.join(tmpFolder,"brain-mask_intersected-reg.nrrd"),"-n","nearest","-p", nbThreads]
    call(command)
    command = [animaApplyTransformSerie,"-i", os.path.join(uspioAtlasDir_RefSpace,"brainstemMask.nii.gz"),"-t", os.path.join(tmpFolder,"avg_nl_tr.xml"),"-g",os.path.join(tmpFolder,"FLAIR_preprocessed.nrrd"),"-o", os.path.join(tmpFolder,"brainstemMask-reg.nrrd"),"-n","nearest","-p", nbThreads]
    call(command)

    # mask out brainstem
    command=[animaImageArithmetic, "-i", os.path.join(tmpFolder,"brain-mask_intersected-reg.nrrd"), "-s",  os.path.join(tmpFolder,"brainstemMask-reg.nrrd"), "-o", os.path.join(tmpFolder,"brain-mask_intersected-reg-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"mask-up.nrrd"), "-m",  os.path.join(tmpFolder,"brain-mask_intersected-reg-bs.nrrd"), "-o", os.path.join(tmpFolder,"mask-up-int-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"mask-down.nrrd"), "-m", os.path.join(tmpFolder,"brain-mask_intersected-reg-bs.nrrd"), "-o", os.path.join(tmpFolder,"mask-down-int-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"mask.nrrd"), "-m",  os.path.join(tmpFolder,"brain-mask_intersected-reg-bs.nrrd"), "-o", os.path.join(tmpFolder,"mask-int-bs.nrrd")]
    call(command)

    #Provide masks for post processing
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"mask-up.nrrd"), "-m",
             os.path.join(tmpFolder,"brain-mask_intersected-reg.nrrd"), "-o", os.path.join(tmpFolder,"mask-up.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"mask-down.nrrd"), "-m",
             os.path.join(tmpFolder,"brain-mask_intersected-reg.nrrd"), "-o", os.path.join(tmpFolder,"mask-down.nrrd")]
    call(command)
    command = [animaMaskImage, "-i", os.path.join(tmpFolder, "mask.nrrd"), "-m",
               os.path.join(tmpFolder, "brainstemMask-reg.nrrd"), "-o", os.path.join(tmpFolder, "mask-bs.nrrd")]
    call(command)

    #Apply transform to reference images for normalization
    command=[animaApplyTransformSerie,"-i", os.path.join(uspioAtlasDir_FLAIR, "FLAIR_1.nrrd"),"-t",os.path.join(tmpFolder,"avg_nl_tr.xml"),"-g",os.path.join(tmpFolder,"FLAIR_preprocessed.nrrd"),"-o", os.path.join(tmpFolder, "FLAIR_1_reg.nrrd"),"-p", nbThreads]
    call(command)
    command = [animaApplyTransformSerie,"-i", os.path.join(uspioAtlasDir_T1, "T1_1.nrrd"),"-t",os.path.join(tmpFolder,"avg_nl_tr.xml"),"-g",os.path.join(tmpFolder,"FLAIR_preprocessed.nrrd"),"-o", os.path.join(tmpFolder, "T1_1_reg.nrrd"),"-p", nbThreads]
    call(command)
    command = [animaApplyTransformSerie,"-i", os.path.join(uspioAtlasDir_T2, "T2_1.nrrd"),"-t",os.path.join(tmpFolder,"avg_nl_tr.xml"),"-g",os.path.join(tmpFolder,"FLAIR_preprocessed.nrrd"),"-o", os.path.join(tmpFolder, "T2_1_reg.nrrd"),"-p", nbThreads]
    call(command)

    # normalize up
    command=[animaKMeansStandardization, "-r", os.path.join(tmpFolder, "FLAIR_1_reg.nrrd"), "-m", flairImage, "-R", os.path.join(tmpFolder, "mask-up-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "FLAIR-up-normed.nrrd")]
    call(command)
    command=[animaKMeansStandardization, "-r", os.path.join(tmpFolder, "T2_1_reg.nrrd"), "-m", t2Image, "-R", os.path.join(tmpFolder, "mask-up-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "T2-up-normed.nrrd")]
    call(command)
    command=[animaKMeansStandardization, "-r", os.path.join(tmpFolder, "T1_1_reg.nrrd"), "-m", t1Image, "-R", os.path.join(tmpFolder, "mask-up-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "T1-up-normed.nrrd")]
    call(command)
    # normalize down
    command=[animaKMeansStandardization, "-r", os.path.join(tmpFolder, "FLAIR_1_reg.nrrd"), "-m", flairImage, "-R", os.path.join(tmpFolder, "mask-down-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "FLAIR-down-normed.nrrd")]
    call(command)
    command=[animaKMeansStandardization, "-r", os.path.join(tmpFolder, "T2_1_reg.nrrd"), "-m", t2Image, "-R", os.path.join(tmpFolder, "mask-down-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "T2-down-normed.nrrd")]
    call(command)
    command=[animaKMeansStandardization, "-r", os.path.join(tmpFolder, "T1_1_reg.nrrd"), "-m", t1Image, "-R", os.path.join(tmpFolder, "mask-down-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "T1-down-normed.nrrd")]
    call(command)

    # Compute flair squared image for down part
    command=[animaImageArithmetic, "-i", os.path.join(tmpFolder,"FLAIR-down-normed.nrrd"), "-m", os.path.join(tmpFolder, "FLAIR-down-normed.nrrd"), "-o", os.path.join(tmpFolder,"FLAIR2-normed-down.nrrd")]
    call(command)

    # Mask atlas
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"ATLAS-wm_masked-reg.nrrd"), "-m", os.path.join(tmpFolder,"mask-up-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "ATLAS-wm_masked_up-reg-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"ATLAS-gm_masked-reg.nrrd"), "-m", os.path.join(tmpFolder,"mask-up-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "ATLAS-gm_masked_up-reg-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"ATLAS-csf_masked-reg.nrrd"), "-m", os.path.join(tmpFolder,"mask-up-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "ATLAS-csf_masked_up-reg-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"prob_map-reg.nrrd"), "-m", os.path.join(tmpFolder,"mask-up-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "prob_map_up-reg-bs.nrrd")]
    call(command)

    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"ATLAS-wm_masked-reg.nrrd"), "-m", os.path.join(tmpFolder,"mask-down-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "ATLAS-wm_masked_down-reg-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"ATLAS-gm_masked-reg.nrrd"), "-m", os.path.join(tmpFolder,"mask-down-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "ATLAS-gm_masked_down-reg-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"ATLAS-csf_masked-reg.nrrd"), "-m", os.path.join(tmpFolder,"mask-down-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "ATLAS-csf_masked_down-reg-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"prob_map-reg.nrrd"), "-m", os.path.join(tmpFolder,"mask-down-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "prob_map_down-reg-bs.nrrd")]
    call(command)

    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"FLAIR-up-normed.nrrd"), "-m", os.path.join(tmpFolder,"mask-up-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "FLAIR-up-normed-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"FLAIR-down-normed.nrrd"), "-m", os.path.join(tmpFolder,"mask-down-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "FLAIR-down-normed-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"T2-up-normed.nrrd"), "-m", os.path.join(tmpFolder,"mask-up-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "T2-up-normed-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"T2-down-normed.nrrd"), "-m", os.path.join(tmpFolder,"mask-down-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "T2-down-normed-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"T1-up-normed.nrrd"), "-m", os.path.join(tmpFolder,"mask-up-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "T1-up-normed-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"T1-down-normed.nrrd"), "-m", os.path.join(tmpFolder,"mask-down-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "T1-down-normed-bs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"FLAIR2-normed-down.nrrd"), "-m", os.path.join(tmpFolder,"mask-down-int-bs.nrrd"), "-o", os.path.join(tmpFolder, "FLAIR2-normed-down-bs.nrrd")]
    call(command)

    command = [animaMaskImage, "-i", os.path.join(tmpFolder, "FLAIR2-normed-down.nrrd"), "-m",
               os.path.join(tmpFolder, "mask-bs.nrrd"), "-o", os.path.join(tmpFolder, "FLAIR2-norm-down-wbs.nrrd")]
    call(command)
    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"ATLAS-csf_masked-reg.nrrd"), "-m",
             os.path.join(tmpFolder,"mask-bs.nrrd"), "-o", os.path.join(tmpFolder, "ATLAS-csf_masked-down-wbs.nrrd")]
    call(command)

    # Compute normed images sums for TLL estimation
    command=[animaImageArithmetic, "-i", os.path.join(tmpFolder,"FLAIR-up-normed-bs.nrrd"), "-a", os.path.join(tmpFolder, "FLAIR-down-normed.nrrd"), "-o", os.path.join(tmpFolder,"FLAIR-normed.nrrd")]
    call(command)
    command=[animaImageArithmetic, "-i", os.path.join(tmpFolder,"T2-up-normed-bs.nrrd"), "-a", os.path.join(tmpFolder, "T2-down-normed.nrrd"), "-o", os.path.join(tmpFolder,"T2-normed.nrrd")]
    call(command)
    command=[animaImageArithmetic, "-i", os.path.join(tmpFolder,"T1-up-normed-bs.nrrd"), "-a", os.path.join(tmpFolder, "T1-down-normed.nrrd"), "-o", os.path.join(tmpFolder,"T1-normed.nrrd")]
    call(command)

