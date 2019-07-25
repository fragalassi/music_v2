#!/bin/bash
SCRIPTDIR=/temp_dd/igrida-fs1/fgalassi/music_v2
SCRIPTDIR=/udd/fgalassi/music_v2
echo "$SCRIPTDIR"

#DATADIR=/temp_dd/igrida-fs1/fgalassi/training
DATADIR=/temp_dd/igrida-fs1/fgalassi/testing_FG_rev2

# Load modules in cluster
. /etc/profile.d/modules.sh
set -xv

module load cuDNN/v7.0.4
module load cuda/9.0.176

# Activate the py virtual environnement
. /udd/fgalassi/myVE/bin/activate

chmod +x $SCRIPTDIR/*.py

for patient in $DATADIR/*; do	

    if [ -d "$patient" ]; then
	 patientID=$(basename "$patient")
	 echo "$patientID"	

	#if [ "$patientID" == "01045BRPO" ];then
	if [ ! -f $DATADIR/"$patientID"/segm_music_v2.nii.gz ]; then
    	
	echo "File not found!"
 	
: '
	#PREPROCESSING	
	#training/testing MICCAI16
	FLAIR=$DATADIR/"$patientID"/Raw/3DFLAIR.nii.gz
	T1=$DATADIR/"$patientID"/Raw/3DT1.nii.gz
	T1g=$DATADIR/"$patientID"/Raw/3DT1GADO.nii.gz
	T2=$DATADIR/"$patientID"/Raw/T2.nii.gz

	python3 $SCRIPTDIR/animaMSExamPreparation.py -r $FLAIR -f $FLAIR -t $T1 -g $T1g -T $T2 -o $DATADIR/"$patientID"/ 
'

	#ADDITIONAL PREPROCESSING
	#training/testing MICCAI16

	FLAIR=$DATADIR/"$patientID"/Raw/3DFLAIR_preprocessed.nrrd
	T1=$DATADIR/"$patientID"/Raw/3DT1_preprocessed.nrrd
	T2=$DATADIR/"$patientID"/Raw/T2_preprocessed.nrrd
	MASK=$DATADIR/"$patientID"/Raw/3DFLAIR_brainMask.nrrd
	C=$DATADIR/"$patientID"/ManualSegmentation/Consensus.nii.gz

	PYTHONHASHSEED=0 python3 $SCRIPTDIR/animaMusicLesionSegmentation.py -f $FLAIR -t $T1 -T $T2 -m $MASK -o $DATADIR/"$patientID" -n 6

	#fi
        fi
    fi
done



