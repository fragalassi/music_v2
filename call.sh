#!/bin/bash
#SCRIPTDIR0=Anima-Scripts-Public/ms_lesion_segmentation
#echo "$SCRIPTDIR"

DATADIR=../testing

for patient in $DATADIR/*; do	

    if [ -d "$patient" ]; then
	 patientID=$(basename "$patient")
	 echo "$patientID"	

	#PREPROCESSING	
	#training/testing MICCAI16
	FLAIR=$DATADIR/"$patientID"/3DFLAIR.nii.gz
	T1=$DATADIR/"$patientID"/3DT1.nii.gz
	T1gd=$DATADIR/"$patientID"/3DT1GADO.nii.gz
	T2=$DATADIR/"$patientID"/T2.nii.gz

	python3 animaMSExamPreparation.py -r $FLAIR -f $FLAIR -t $T1 -g $T1g -T $T2 -o $DATADIR/"$patientID"/ 

	#SEGMENTATION
	#training/testing MICCAI16
	FLAIR=$DATADIR/"$patientID"/3DFLAIR_preprocessed.nrrd
	T1=$DATADIR/"$patientID"/3DT1_preprocessed.nrrd
	T2=$DATADIR/"$patientID"/T2_preprocessed.nrrd
	MASK=$DATADIR/"$patientID"/3DFLAIR_brainMask.nrrd
	C=$DATADIR/"$patientID"/Consensus.nii.gz

	#python3 $SCRIPTDIR/animaMusicLesionSegmentation.py -f $FLAIR -t $T1 -T $T2 -m $MASK -o $DATADIR/"$patientID"


    fi
done




