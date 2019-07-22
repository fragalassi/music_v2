#!/usr/bin/python

import os
from subprocess import call


def music_lesion_post_processing(animaDir, tmpFolder, outputImage, gcUpperImage, gcDownImage,
                                 flair2DownImage,flair2BSImage, atlasWMUpper, atlasGMUpper, atlasCSFUpper, atlasWMDown,
                                 atlasGMDown, atlasCSFDown, atlasCSFBS, maskUpImage, maskDownImage, maskBS, nbThreads):
    # anima tools - some not used
    animaThrImage = os.path.join(animaDir, "animaThrImage")
    animaMaskImage = os.path.join(animaDir, "animaMaskImage")
    animaConnectedComponents = os.path.join(animaDir, "animaConnectedComponents")
    animaInfluenceZones = os.path.join(animaDir, "animaInfluenceZones")
    animaRemoveTouchingBorder = os.path.join(animaDir, "animaRemoveTouchingBorder")
    animaFillHoleImage = os.path.join(animaDir, "animaFillHoleImage")
    animaImageArithmetic = os.path.join(animaDir, "animaImageArithmetic")
    animaOtsuThrImage = os.path.join(animaDir, "animaOtsuThrImage")

    # UP
    # thresh wm gm csf
    command = [animaThrImage, "-i", atlasWMUpper, "-t", "0.1", "-o", 
               os.path.join(tmpFolder, 'ATLAS-wm_mask_up-reg-bs-wm.nrrd')]
    call(command)
    command = [animaThrImage, "-i", atlasCSFUpper, "-t", "0.8", "-o",
               os.path.join(tmpFolder, 'ATLAS-csf_mask_up-reg-bs-wm.nrrd')]
    call(command)
    command = [animaThrImage, "-i", atlasGMUpper, "-t", "0.2", "-o",
               os.path.join(tmpFolder, 'ATLAS-gm_mask_up-reg-bs-wm.nrrd')]
    call(command)

    # remove les in csf and gm & keep wm lesions
    command = [animaThrImage, "-i", os.path.join(tmpFolder, "ATLAS-csf_mask_up-reg-bs-wm.nrrd"), "-o",
               os.path.join(tmpFolder, "ATLAS-csf_mask_up-reg-bs-wm-inv.nrrd"), "-t", "0", "-I"]
    call(command)
    command = [animaMaskImage, "-i", os.path.join(tmpFolder, "ATLAS-csf_mask_up-reg-bs-wm-inv.nrrd"), "-m",
               gcUpperImage, "-o", gcUpperImage]
    call(command)
    command = [animaThrImage, "-i", os.path.join(tmpFolder, "ATLAS-gm_mask_up-reg-bs-wm.nrrd"), "-o",
               os.path.join(tmpFolder, "ATLAS-gm_mask_up-reg-bs-wm-inv.nrrd"), "-t", "0", "-I"]
    call(command)
    command = [animaMaskImage, "-i", os.path.join(tmpFolder, "ATLAS-gm_mask_up-reg-bs-wm-inv.nrrd"), "-m",
               gcUpperImage, "-o", gcUpperImage]
    call(command)
    command = [animaMaskImage, "-i", os.path.join(tmpFolder, "ATLAS-wm_mask_up-reg-bs-wm.nrrd"), "-m",
               gcUpperImage, "-o", gcUpperImage]
    call(command)

    # remove les touching outer mask border
    command = [animaInfluenceZones, "-i", gcUpperImage, "-o", os.path.join(tmpFolder, 'segm-wm-les-label1.nrrd')]
    call(command)
    command = [animaRemoveTouchingBorder, "-i", os.path.join(tmpFolder, 'segm-wm-les-label1.nrrd'), "-m",
               maskUpImage, "-o", os.path.join(tmpFolder, 'segm-wm-les-label1.nrrd'), "-L", "-T", nbThreads]
    call(command)
    
    # remove small lesions
    command = [animaConnectedComponents, "-i", os.path.join(tmpFolder, 'segm-wm-les-label1.nrrd'), "-m", "12", "-o",
               os.path.join(tmpFolder, 'segm-wm-les-label-conn1.nrrd')]
    call(command)
    command = [animaThrImage, "-i", os.path.join(tmpFolder, 'segm-wm-les-label-conn1.nrrd'), "-t", "0", "-o",
               os.path.join(tmpFolder, 'segm-wm-les-label-conn-thr1.nrrd')]
    call(command)
    
    # fill lesions
    command = [animaFillHoleImage, "-i", os.path.join(tmpFolder, 'segm-wm-les-label-conn-thr1.nrrd'), "-o",
               os.path.join(tmpFolder, 'segm-wm-les-label-conn-thr-fh1.nrrd')]
    call(command)
    
    # final output
    command = [animaThrImage, "-i", os.path.join(tmpFolder, 'segm-wm-les-label-conn-thr-fh1.nrrd'), "-t", "0", "-o",
               gcUpperImage]
    call(command)

    # DOWN without brainstem
    # thresh wm gm csf
    command = [animaThrImage, "-i", atlasWMDown, "-t", "0.9", "-o",
               os.path.join(tmpFolder, 'ATLAS-wm_mask_down-reg-bs-wm-t.nrrd')]
    call(command)
    command = [animaThrImage, "-i", atlasCSFDown, "-t", "0.0001",
               "-o", os.path.join(tmpFolder, 'ATLAS-csf_mask_down-reg-bs-wm-t.nrrd')]
    call(command)
    command = [animaThrImage, "-i", atlasGMDown, "-t", "0.1", "-o",
               os.path.join(tmpFolder, 'ATLAS-gm_mask_down-reg-bs-wm-t.nrrd')]
    call(command)
    
    # otsu thresholding
    command = [animaOtsuThrImage, "-i", flair2DownImage, "-m", maskDownImage, "-n", "6",
               "-o", os.path.join(tmpFolder, "FLAIR2-normed-down-otsu.nrrd")]
    call(command)

    command = [animaThrImage, "-i", os.path.join(tmpFolder, "FLAIR2-normed-down-otsu.nrrd"),
               "-o", os.path.join(tmpFolder, "FLAIR2-normed-down-otsu-5.nrrd"), "-t", "5"]
    call(command)

    # add hyperintensities from flair2 otsu thr
    command = [animaImageArithmetic, "-i", gcDownImage, "-a", os.path.join(tmpFolder, 'FLAIR2-normed-down-otsu-5.nrrd'),
               "-o", os.path.join(tmpFolder, 'segm.nrrd')]
    call(command)
    command = [animaThrImage, "-i", os.path.join(tmpFolder, 'segm.nrrd'), "-o",
               os.path.join(tmpFolder, 'segm.nrrd'), "-t", "0"]
    call(command)

    # remove lesions in csf and gm - keep wm lesions
    command = [animaThrImage, "-i", os.path.join(tmpFolder, "ATLAS-csf_mask_down-reg-bs-wm-t.nrrd"), "-o",
               os.path.join(tmpFolder, "ATLAS-csf_mask_down-reg-bs-wm-t-inv.nrrd"), "-t", "0", "-I"]
    call(command)
    command = [animaMaskImage, "-i", os.path.join(tmpFolder, "ATLAS-csf_mask_down-reg-bs-wm-t-inv.nrrd"), "-m",
               os.path.join(tmpFolder, 'segm.nrrd'), "-o", os.path.join(tmpFolder, 'segm.nrrd')]
    call(command)
    command = [animaThrImage, "-i", os.path.join(tmpFolder, "ATLAS-gm_mask_down-reg-bs-wm-t.nrrd"), "-o",
               os.path.join(tmpFolder, "ATLAS-gm_mask_down-reg-bs-wm-t-inv.nrrd"), "-t", "0", "-I"]
    call(command)
    command = [animaMaskImage, "-i", os.path.join(tmpFolder, "ATLAS-gm_mask_down-reg-bs-wm-t-inv.nrrd"), "-m",
               os.path.join(tmpFolder, 'segm.nrrd'), "-o", os.path.join(tmpFolder, 'segm.nrrd')]
    call(command)
    command = [animaMaskImage, "-i", os.path.join(tmpFolder, "ATLAS-wm_mask_down-reg-bs-wm-t.nrrd"), "-m",
               os.path.join(tmpFolder, 'segm.nrrd'), "-o", os.path.join(tmpFolder, 'segm.nrrd')]
    call(command)

    # remove les touching outer wm mask border
    command = [animaInfluenceZones, "-i", os.path.join(tmpFolder, 'segm.nrrd'), "-o",
               os.path.join(tmpFolder, 'segm-wm-les-label1.nrrd')]
    call(command)
    command = [animaRemoveTouchingBorder, "-i", os.path.join(tmpFolder, 'segm-wm-les-label1.nrrd'), "-m",
               maskDownImage, "-o", os.path.join(tmpFolder, 'segm-wm-les-label1.nrrd'), "-L", "-T", nbThreads]
    call(command)
    
    # remove small lesions
    command = [animaConnectedComponents, "-i", os.path.join(tmpFolder, 'segm-wm-les-label1.nrrd'), "-m", "9", "-o",
               os.path.join(tmpFolder, 'segm-wm-les-label-conn1.nrrd')]
    call(command)
    command = [animaThrImage, "-i", os.path.join(tmpFolder, 'segm-wm-les-label-conn1.nrrd'), "-t", "0", "-o",
               os.path.join(tmpFolder, 'segm-wm-les-label-conn-thr1.nrrd')]
    call(command)
    
    # fill lesions
    command = [animaFillHoleImage, "-i", os.path.join(tmpFolder, 'segm-wm-les-label-conn-thr1.nrrd'), "-o",
               os.path.join(tmpFolder, 'segm-wm-les-label-conn-thr-fh1.nrrd')]
    call(command)
    
    # final output
    command = [animaThrImage, "-i", os.path.join(tmpFolder, 'segm-wm-les-label-conn-thr-fh1.nrrd'), "-t", "0", "-o",
               gcDownImage]
    call(command)

    # DOWN brainstem only
    command = [animaOtsuThrImage, "-i", flair2BSImage, "-o", os.path.join(tmpFolder, "FLAIR2-norm-down-otsu-wbs.nrrd"),
               "-m", maskBS, "-n", "6"]
    call(command)
    command = [animaThrImage, "-i", os.path.join(tmpFolder, "FLAIR2-norm-down-otsu-wbs.nrrd"), "-o",
               os.path.join(tmpFolder, "FLAIR2-norm-down-otsu-wbs-6.nrrd"), "-t", "6"]
    call(command)
    command = [animaThrImage, "-i", atlasCSFBS, "-t", "0.001", "-o",
               os.path.join(tmpFolder, 'ATLAS-csf_mask_down-bs-t-inv.nrrd'), "-I"]
    call(command)
    command = [animaMaskImage, "-i", os.path.join(tmpFolder, 'ATLAS-csf_mask_down-bs-t-inv.nrrd'), "-m",
               os.path.join(tmpFolder, "FLAIR2-norm-down-otsu-wbs-6.nrrd"), "-o",
               os.path.join(tmpFolder, "FLAIR2-norm-down-otsu-wbs-6-t.nrrd")]
    call(command)

    # remove small lesions
    command = [animaConnectedComponents, "-i", os.path.join(tmpFolder, 'FLAIR2-norm-down-otsu-wbs-6-t.nrrd'), "-m",
               "18", "-o", os.path.join(tmpFolder, 'FLAIR2-norm-down-otsu-wbs-6-t-conn1.nrrd')]
    call(command)
    command = [animaThrImage, "-i", os.path.join(tmpFolder, 'FLAIR2-norm-down-otsu-wbs-6-t-conn1.nrrd'), "-t", "0",
               "-o", os.path.join(tmpFolder, 'FLAIR2-norm-down-otsu-wbs-6-t-conn1.nrrd')]
    call(command)
    # fill lesions
    command = [animaFillHoleImage, "-i", os.path.join(tmpFolder, 'FLAIR2-norm-down-otsu-wbs-6-t-conn1.nrrd'), "-o",
               os.path.join(tmpFolder, 'FLAIR2-norm-down-otsu-wbs-6-t-conn1-fh.nrrd')]
    call(command)
    # final output
    command = [animaThrImage, "-i", os.path.join(tmpFolder, 'FLAIR2-norm-down-otsu-wbs-6-t-conn1-fh.nrrd'), "-t",
               "0", "-o", os.path.join(tmpFolder, 'segm-ini0-pr-flair-down-PP-bs.nrrd')]
    call(command)

    # add hyperintensities from flair2 otsu thr
    command = [animaImageArithmetic, "-i", gcDownImage, "-a",
               os.path.join(tmpFolder, 'segm-ini0-pr-flair-down-PP-bs.nrrd'), "-o", gcDownImage]
    call(command)

    # Finally merge the two segmentations
    command = [animaImageArithmetic, "-i", gcDownImage, "-a", gcUpperImage, "-o", outputImage]
    call(command)
    command = [animaThrImage, "-i", outputImage, "-o", outputImage, "-t", "0"]
    call(command)
