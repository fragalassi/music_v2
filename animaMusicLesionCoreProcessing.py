#!/usr/bin/python

import os
from subprocess import call


def music_lesion_core_processing(animaDir,outputImage,t1Image,t2Image,flairImage,maskImage,atlasWM,atlasGM,atlasCSF,
                                 msPriors,total_lesion_load,nbThreads):

    # Anima
    animaGcStremMsLesionsSegmentation = os.path.join(animaDir,"animaGcStremMsLesionsSegmentation")

    thr = 4000
    if float(total_lesion_load) < thr:
        h = "0.35"
        fmin = "2"
        fmax = "5"
        wm = "0.1"
        l = "10"
        s = "1"
    else:
        h = "0.35"
        fmin = "3"
        fmax = "5"
        wm = "0.1"
        l = "10"
        s = "0.8"

    # GC segmentation
    command = [animaGcStremMsLesionsSegmentation,"--lesion-prior",msPriors,"-m", maskImage, "-a", "1", "--rej", h, "--min-fuzzy", fmin, "--max-fuzzy", fmax, "--alpha", l, "--sigma", s, "-i",
               t1Image, "-j", t2Image, "-l", flairImage, "--ini", "0", "-o", outputImage, "--WMratio", wm, "-z",atlasWM,"-y",atlasGM,"-x",atlasCSF,"-T",nbThreads]
    call(command)
