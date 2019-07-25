#!/bin/bash
SCRIPTDIR=Anima-Scripts/ms_lesion_segmentation/music_lesion_pipeline
SCRIPTDIR=.

DATADIR=testing

for patient in $DATADIR/*; do	

    if [ -d "$patient" ]; then
	 patientID=$(basename "$patient")
	 echo "$patientID"	
 
: '
	#PREPROCESSING	
	#training/testing MICCAI16
	FLAIR=$DATADIR/"$patientID"/3DFLAIR.nii.gz
	T1=$DATADIR/"$patientID"/3DT1.nii.gz
	T1gd=$DATADIR/"$patientID"/3DT1GADO.nii.gz

	python3 $SCRIPTDIR/animaMSExamPreparation.py -r $FLAIR -f $FLAIR -t $T1  -o $DATADIR/"$patientID"/ 
'
	#SEGMENTATION		
	#training/testing MICCAI16
	FLAIR=$DATADIR/"$patientID"/3DFLAIR_preprocessed.nrrd
	T1=$DATADIR/"$patientID"/3DT1_preprocessed.nrrd
	MASK=$DATADIR/"$patientID"/3DFLAIR_brainMask.nrrd
	C=$DATADIR/"$patientID"/Consensus.nii.gz

	PYTHONHASHSEED=0 python3 $SCRIPTDIR/animaMusicLesionSegmentation.py -f $FLAIR -t $T1 -m $MASK -n 6 -o $DATADIR/"$patientID"/

    fi
done
