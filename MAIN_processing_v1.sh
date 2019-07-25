#!/bin/bash
SCRIPTDIR=/temp_dd/igrida-fs1/fgalassi/MUSIC_rev2

DATADIR=/temp_dd/igrida-fs1/fgalassi/testing
#DATADIR=/temp_dd/igrida-fs1/fgalassi/UNC_train_Part1
DATADIR=/temp_dd/igrida-fs1/fgalassi/export-music
DATADIR=/temp_dd/igrida-fs1/fgalassi/brainM24/set1
DATADIR=/temp_dd/igrida-fs1/fgalassi/brainM24/set2_includingSomeM0/

DATADIR=/temp_dd/igrida-fs1/fgalassi/training
DATADIR=/temp_dd/igrida-fs1/fgalassi/testing_FG_rev2
#DATADIR=/home/fgalassi/Downloads/UNC_train_Part1/
#DATADIR=/temp_dd/igrida-fs1/fgalassi/UNC_train_Part1/

chmod +x $SCRIPTDIR/*.py

counter=0

for patient in $DATADIR/*; do	

    if [ -d "$patient" ]; then
	 patientID=$(basename "$patient")
	 echo "$patientID"	
 	 
	if [ "$patientID" == "03010MARI" ];then

	 #testing MICCAI16
	 FLAIR=$DATADIR/"$patientID"/Raw/3DFLAIR.nii.gz
	 T1=$DATADIR/"$patientID"/Raw/3DT1.nii.gz
	 T2=$DATADIR/"$patientID"/Raw/T2.nii.gz

: '
	 #export-music 2019
	 FLAIR=$DATADIR/"$patientID"/flair.nrrd
	 T1=$DATADIR/"$patientID"/t1.nrrd

	 #MICCAI 2008
	 FLAIR=$DATADIR/"$patientID"/FLAIR.nii.gz
	 T1=$DATADIR/"$patientID"/T1.nii.gz

	 #brain_set_4
	 FLAIR=$DATADIR/"$patientID"/br-flair.nii.gz
	 T1=$DATADIR/"$patientID"/br-t1.nii.gz
'

	 oarsub -t besteffort -t idempotent -l /core=3,walltime=02:30:00 "python3 $SCRIPTDIR/animaMSExamPreparation.py -r $FLAIR -f $FLAIR -t $T1 -T $T2 -o $DATADIR/"$patientID"/ "
	 

	 FLAIR=$DATADIR/"$patientID"/3DFLAIR_preprocessed.nrrd
	 T1=$DATADIR/"$patientID"/3DT1_preprocessed.nrrd
	 MASK=$DATADIR/"$patientID"/3DFLAIR_brainMask.nrrd
	 C=$DATADIR/"$patientID"/Consensus.nii.gz
: '
	 FLAIR=$DATADIR/"$patientID"/flair_preprocessed.nrrd
	 T1=$DATADIR/"$patientID"/t1_preprocessed.nrrd
	 MASK=$DATADIR/"$patientID"/flair_brainMask.nrrd

	 FLAIR=$DATADIR/"$patientID"/FLAIR_preprocessed.nrrd
	 T1=$DATADIR/"$patientID"/T1_preprocessed.nrrd
	 MASK=$DATADIR/"$patientID"/FLAIR_brainMask.nrrd
	 C=$DATADIR/"$patientID"/UNC_train_lesion_byCHB.nii.gz
'

	 #oarsub -t besteffort -t idempotent -l /core=3,walltime=01:00:00 "python3 $SCRIPTDIR/animaMusicLesionSegmentationTraining_v3.py -f $FLAIR -t $T1 -m $MASK -n 6 -o $DATADIR/"$patientID"/ -c $C -n 6"

	fi
     fi

 	(( counter++ ))

done

