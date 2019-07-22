#!/bin/bash
SCRIPTDIR=/temp_dd/igrida-fs1/fgalassi/music-scripts
DATADIR=/temp_dd/igrida-fs1/fgalassi/images_set_for_autoseg

chmod +x $SCRIPTDIR/preprocessing.py
chmod +x $SCRIPTDIR/normalize.py
chmod +x $SCRIPTDIR/graph_cut_pr_segmentation_rev4.py
chmod +x $SCRIPTDIR/postprocessing_GC_rev3.py
chmod +x $SCRIPTDIR/bypass.sh

for patient in $DATADIR/*; do	

   if [ -d "$patient" ]; then
	 patientID=$(basename "$patient")
	 echo "$patientID"	

	 ## uncomment for preprocessing only (replace names)
	 #FLAIR=$DATADIR/$patientID/FLAIR.nii.gz
	 #T1=$DATADIR/$patientID/3DT1.nii.gz
	 #T2=$DATADIR/$patientID/T2ECHO2.nii.gz
	
	 #oarsub -l core=12,walltime=01:00:00 -t besteffort -t idempotent -p "dedicated = 'none' or dedicated = 'serpico'" "python $SCRIPTDIR/preprocessing.py -r $T1 -f $FLAIR -i $T1 -j $T2 -o $DATADIR/$patientID -T 12"

	 #oarsub -l core=6,walltime=02:15:00 -t besteffort -t idempotent -p "dedicated = 'none' or dedicated = 'serpico'" "python $SCRIPTDIR/normalize_voxwisecomparison.py --dir_subj_r $DATADIR/"$patientID" -T 6"

	 oarsub -l core=12,walltime=02:50:00 -t besteffort -t idempotent -p "dedicated = 'none' or dedicated = 'serpico'"  "./bypass.sh --dir_subj $DATADIR/"$patientID" --dir_out $DATADIR/"$patientID" --th 12"

   fi
done



: '

DATADIRM=/temp_dd/igrida-fs1/fgalassi/images_set_for_autoseg

for patient in $DATADIRM/*; do	

   if [ -d "$patient" ]; then
	 patientID=$(basename "$patient")
	 echo "$patientID"

	 FLAIR=$DATADIRM/"$patientID"/FLAIR-down-notsu-bs.nii.gz
	 FLAIR2=$DATADIRM/"$patientID"/flair2-notsu-down-bs.nii.gz
	 T2=$DATADIRM/"$patientID"/T2-down-notsu-bs.nii.gz
	 T1=$DATADIRM/"$patientID"/T1-down-notsu-bs.nii.gz
	 brainMask=$DATADIRM/"$patientID"/mask-down-int-bs.nii.gz
	 atlaswm=$DATADIRM/"$patientID"/ATLAS-wm_masked_down-reg-bs.nii.gz
	 atlasgm=$DATADIRM/"$patientID"/ATLAS-gm_masked_down-reg-bs.nii.gz
	 atlascsf=$DATADIRM/"$patientID"/ATLAS-csf_masked_down-reg-bs.nii.gz
	 mspriors=$DATADIRM/"$patientID"/prob_map_down-reg-bs.nii.gz


	 oarsub -l core=6,nodes=1,walltime=02:00:00 -t besteffort -t idempotent -p "dedicated = 'none' or dedicated = 'serpico'" "python $SCRIPTDIR/graph_cut_pr_segmentation_rev4.py -i $T1 -j $T2 -k $FLAIR -m $brainMask -x $atlaswm -y $atlasgm -z $atlascsf -p $mspriors -o $DATADIRM/"$patientID"/segm-ini0-pr-flair-down.nii.gz -a $DATADIRM/"$patientID"/wm_ini0-pr-up.nii.gz -b $DATADIRM/"$patientID"/gm_ini0-pr-up.nii.gz -c $DATADIRM/"$patientID"/csf_ini0-pr-up.nii.gz -d $DATADIRM/"$patientID"/mahamaxi_ini0-pr.nii.gz -e $DATADIRM/"$patientID"/mahamin_ini0-pr-up.nii.gz -t $DATADIRM/"$patientID"/parameters_up_ini0-pr-down.csv -T 6"

	 sleep 60
	

	 FLAIR=$DATADIRM/"$patientID"/FLAIR-up-notsu-bs.nii.gz
	 FLAIR2=$DATADIRM/"$patientID"/flair2-notsu-up-bs.nii.gz
	 T2=$DATADIRM/"$patientID"/T2-up-notsu-bs.nii.gz
	 T1=$DATADIRM/"$patientID"/T1-up-notsu-bs.nii.gz
	 brainMask=$DATADIRM/"$patientID"/mask-up-int-bs.nii.gz
	 atlaswm=$DATADIRM/"$patientID"/ATLAS-wm_masked_up-reg-bs.nii.gz
	 atlasgm=$DATADIRM/"$patientID"/ATLAS-gm_masked_up-reg-bs.nii.gz
	 atlascsf=$DATADIRM/"$patientID"/ATLAS-csf_masked_up-reg-bs.nii.gz
	 mspriors=$DATADIRM/"$patientID"/prob_map_up-reg-bs.nii.gz

	 oarsub -l core=6,nodes=1,walltime=02:60:00 -t besteffort -t idempotent -p "dedicated = 'none' or dedicated = 'serpico'" "python $SCRIPTDIR/graph_cut_pr_segmentation_rev4.py -i $T1 -j $T2 -k $FLAIR -m $brainMask -x $atlaswm -y $atlasgm -z $atlascsf -p $mspriors -o $DATADIRM/"$patientID"/segm-ini0-pr-flair-up.nii.gz -a $DATADIRM/"$patientID"/wm_ini0-pr-up.nii.gz -b $DATADIRM/"$patientID"/gm_ini0-pr-up.nii.gz -c $DATADIRM/"$patientID"/csf_ini0-pr-up.nii.gz -d $DATADIRM/"$patientID"/mahamaxi_ini0-pr.nii.gz -e $DATADIRM/"$patientID"/mahamin_ini0-pr-up.nii.gz -t $DATADIRM/"$patientID"/parameters_up_ini0-pr-up.csv -T 6"

	                  
         fi

done

'
