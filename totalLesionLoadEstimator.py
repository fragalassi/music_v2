#!/usr/bin/python

import os
from subprocess import call, check_output

# Script used to estimate the total lesion load of a MS patient, with the following steps:
#   - Non-linear registration of an atlas on the T1-w image. This atlas contains WM probability map plus a brain mask without the cerebellum and the brainstem
#   - Masking the T2-w and FLAIR images to keep only the WM in the two hemispheres, using the atlas WM probability map and the brain mask without the cerebellum and the brainstem
#   - Segmentation of the T2-w and FLAIR masked images whith the K-means algorithm. T2-w and FLAIR images are segmented respectively in 4 and 3 classes. This segmentation is performed to extract MS lesions, regrouped in one class in each image, from WM.
#   - Intersection of T2-w and FLAIR MS lesions classes.
#   - Computation of the volume from the resulting image, which corresponds to an approximation of the TLL.


def lesion_load_estimation(animaDir,atlasDir,tmpFolder,t1Image,t2Image,flairImage,nbThreads):
    #Anima commands
    animaApplyTransformSerie=os.path.join(animaDir,"animaApplyTransformSerie")
    animaDenseSVFBMRegistration=os.path.join(animaDir,"animaDenseSVFBMRegistration")
    animaKMeansClustering=os.path.join(animaDir,"animaKMeansClustering")
    animaMaskImage=os.path.join(animaDir,"animaMaskImage")
    animaThrImage=os.path.join(animaDir,"animaThrImage")
    animaTotalLesionLoad=os.path.join(animaDir,"animaTotalLesionLoad")
    animaTransformSerieXmlGenerator=os.path.join(animaDir,"animaTransformSerieXmlGenerator")
    animaPyramidalBMRegistration=os.path.join(animaDir,"animaPyramidalBMRegistration")
    animaConvertImage=os.path.join(animaDir,"animaConvertImage")

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

    # Process
    command=[animaPyramidalBMRegistration, "-r", t1Image, "-m", os.path.join(atlasDir,"ATLAS-masked.nrrd"), "-o",
             os.path.join(tmpFolder,"statAtlas_aff.nrrd"), "-O", os.path.join(tmpFolder,"statAtlas_aff_tr.txt"),
             "--ot", "2", "-T",nbThreads] + pyramidOptions
    call(command)

    command=[animaDenseSVFBMRegistration, "-r", t1Image, "-m", os.path.join(tmpFolder,"statAtlas_aff.nrrd"), "-o",
             os.path.join(tmpFolder,"statAtlas_nl.nrrd"), "-O", os.path.join(tmpFolder,"statAtlas_nl_tr.nrrd"),
             "-s", "15", "--sr", "1", "-T",nbThreads] + pyramidOptions
    call(command)

    command=[animaTransformSerieXmlGenerator, "-i", os.path.join(tmpFolder,"statAtlas_aff_tr.txt"),
             "-i", os.path.join(tmpFolder,"statAtlas_nl_tr.nrrd"), "-o", os.path.join(tmpFolder,"statAtlas_tr.xml")]
    
    call(command)

    command=[animaApplyTransformSerie, "-i", os.path.join(atlasDir,"ATLAS-wm-masked-cropped.nrrd"), "-t", os.path.join(tmpFolder,"statAtlas_tr.xml"), "-o", os.path.join(tmpFolder,"ATLAS-wm-masked-cropped_registered.nrrd"), "-g", t1Image,"-p",nbThreads]
    call(command)

    command=[animaThrImage, "-i", os.path.join(tmpFolder,"ATLAS-wm-masked-cropped_registered.nrrd"), "-t", "0.5", "-o", os.path.join(tmpFolder,"ATLAS-wm-masked-cropped_registered.nrrd")]
    call(command)
    
    command=[animaMaskImage, "-i", t2Image, "-m", os.path.join(tmpFolder,"ATLAS-wm-masked-cropped_registered.nrrd"), "-o", os.path.join(tmpFolder,"t2Masked.nrrd")]
    call(command)

    command=[animaMaskImage, "-i", flairImage, "-m", os.path.join(tmpFolder,"ATLAS-wm-masked-cropped_registered.nrrd"), "-o", os.path.join(tmpFolder,"flairMasked.nrrd")]
    call(command)
    
    command=[animaKMeansClustering, "-i", os.path.join(tmpFolder,"t2Masked.nrrd"), "-c", "4", "-k", "3", "-o", os.path.join(tmpFolder,"t2KMeans.nrrd"),"-n",nbThreads]
    call(command)

    command=[animaKMeansClustering, "-i", os.path.join(tmpFolder,"flairMasked.nrrd"), "-c", "3", "-k", "2", "-o", os.path.join(tmpFolder,"flairKMeans.nrrd"),"-n",nbThreads]
    call(command)

    command=[animaMaskImage, "-i", os.path.join(tmpFolder,"t2KMeans.nrrd"), "-m", os.path.join(tmpFolder,"flairKMeans.nrrd"), "-o", os.path.join(tmpFolder,"tllEstimation.nrrd")]
    call(command)
    
    command=[animaTotalLesionLoad, "-i", os.path.join(tmpFolder,"tllEstimation.nrrd")]
    return float(check_output(command))
