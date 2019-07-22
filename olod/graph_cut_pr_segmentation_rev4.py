# -*- coding: utf-8 -*-
"""
Created on Tue May 29 21:55:08 2018

@author: fgalassi
"""

#!/usr/bin/python

import argparse
import sys
import os
from subprocess import call
import textwrap

import totalLesionLoadEstimator

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
atlasDir=os.path.join(animaExtraDataDir,"olivier-atlas") 
atlasDir = "/temp_dd/igrida-fs1/fgalassi/Anima-Scripts_data/olivier-atlas"

animaApplyTransformSerie=os.path.join(animaDir,"animaApplyTransformSerie")

parser = argparse.ArgumentParser(
    prog='GC_segmentation_priors',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('Detection of lesions by graph cut using priors'))

# Input images
parser.add_argument('-i','--inputT1',required=True,help='path to the MS patient T1 image')
parser.add_argument('-j','--inputT2',required=True,help='path to the MS patient T2 image')
parser.add_argument('-k','--inputFLAIR',required=True,help='path to the MS patient FLAIR image')
parser.add_argument('-m','--maskImage',required=True,help='path to the MS patient brain mask image')
parser.add_argument('-x','--atlaswm',required=True,help='path to wm atals image')
parser.add_argument('-y','--atlasgm',required=True,help='path to gm atlas image')
parser.add_argument('-z','--atlascsf',required=True,help='path to csf atlas image')
parser.add_argument('-p','--mspriors',required=True,help='path to MS prior map')
# Input parameters
#parser.add_argument('-r','--rej',required=True,type=float,help='h value')   	
#parser.add_argument('-f','--fmin',required=True,type=int,help='fmin value')	
#parser.add_argument('-g','--fmax',required=True,type=int,help='fmax value')	
#parser.add_argument('-w','--wm',required=True,type=float,help='wm') 
#parser.add_argument('-l','--alpha',required=True,type=int,help='alpha') 
#parser.add_argument('-s','--sigma',required=True,type=int,help='sigma')
# Output
parser.add_argument('-o','--outputImage',required=True,help='path to output image')
parser.add_argument('-t','--outputFile',required=True,help='path to output parameters file (check only)') 
parser.add_argument('-a','--wmImg',required=True,help='path to output wm image')
parser.add_argument('-b','--gmImg',required=True,help='path to output gm image')
parser.add_argument('-c','--csfImg',required=True,help='path to output csf image')
parser.add_argument('-d','--mahaImgMax',required=True,help='path to Mahalanobis image')
parser.add_argument('-e','--mahaImgMin',required=True,help='path to Mahalanobis image')

parser.add_argument('-T','--nbThreads',required=False,type=int,help='Number of execution threads (default: 0 = all cores)',default=0)

args=parser.parse_args()
# Parse Input images
t1Image=args.inputT1
t2Image=args.inputT2
flairImage=args.inputFLAIR
maskImage=args.maskImage
atlaswm=args.atlaswm
atlasgm=args.atlasgm
atlascsf=args.atlascsf
msprior=args.mspriors
outputImage=args.outputImage
nbThreads=str(args.nbThreads)
# Parse Input parameters
#h=str(args.rej)     		        
#fmin=str(args.fmin)	        	
#fmax=str(args.fmax)
#wm=str(args.wm)	   
#l=str(args.alpha)	
#s=str(args.sigma)
# Parse Output
outputFile=args.outputFile       	
wmImg=args.wmImg
gmImg=args.gmImg
csfImg=args.csfImg
outputFolder=os.path.dirname(outputImage)
mahaImgMax=args.mahaImgMax
mahaImgMin=args.mahaImgMin


# Anima
animaTotalLesionLoad=os.path.join(animaDir,"animaTotalLesionLoad")
animaGcStremMsLesionsSegmentation=os.path.join(animaDir,"animaGcStremMsLesionsSegmentation")

# Estimation of the TLL to determine the best parameter set
# These parameter sets are the ones which provide the best segmentation results on the FLI 2016 MSSEG Challenge with priors
tllE=totalLesionLoadEstimator.lesionLoadEstimation(animaDir,atlasDir,outputFolder,t1Image,t2Image,flairImage,maskImage,nbThreads)

thr=5000;
if( float(tllE) < thr ):
    h="0.35"
    fmin="3"
    fmax="5"
    wm="0.2"
    l="10"
    s="1"
if( float(tllE) > thr ):
    h="0.35" #good for flair pr, falir2 pr
    fmin="3"
    fmax="5"
    wm="0.1"
    l="10"
    s="0.8"
   

# GC segmentation
command=[animaGcStremMsLesionsSegmentation,"--lesion-prior",msprior,"-m", maskImage, "-a", "1", "--rej", h, "--min-fuzzy", fmin, "--max-fuzzy", fmax, "--alpha", l, "--sigma", s, "-i", t1Image, "-j", t2Image, "-l", flairImage, "--ini", "0", "-o", outputImage, "--WMratio", wm, "-z",atlaswm,"-y",atlasgm,"-x",atlascsf,"-T",nbThreads, "--out-wm", wmImg, "--out-gm", gmImg, "--out-csf", csfImg, "--out-maha-maxi", mahaImgMax, "--out-maha-mini", mahaImgMin]
call(command)


# Print to file
full_path = os.path.join(outputFolder, outputFile)
f = open(outputFile, 'w')	
					  				 
l=[]
l.append(h+"\n")
l.append(fmin+"\n")
l.append(fmax+"\n")
l.append(wm+"\n")
l.append(str(tllE)+"\n")
#l.append(l+"\n")
#l.append(s+"\n")

for line in l:
    f.write(line)

f.close()

