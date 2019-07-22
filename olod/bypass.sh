#!/bin/bash
SCRIPTDIR=/temp_dd/igrida-fs1/fgalassi/music-scripts

. /etc/profile.d/modules.sh
set -xv

module load nibabel #needed in python scripts

while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --dir_subj)
    dir_subj="$2"
    shift # past argument
    ;;
    --dir_out)
    dir_out="$2"
    shift # past argument
    ;;
    --th)
    th="$2"
    shift # past argument
    ;;
    *)

    ;;
esac
shift # past argument or value
done

python $SCRIPTDIR/postprocessing_GC_rev3.py -i $dir_subj -o $dir_out -T $th

