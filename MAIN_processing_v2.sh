#!/bin/bash

SCRIPTDIR=/temp_dd/igrida-fs1/fgalassi/music_v2
echo "$SCRIPTDIR"

chmod +x $SCRIPTDIR/bypass_preprocessing_v2.sh

oarsub -t besteffort -t idempotent -p "dedicated='none' or dedicated = 'serpico' or dedicated = 'linkmedia' or dedicated = 'sirocco' or dedicated = 'intuidoc'" -l walltime=03:00:0 "$SCRIPTDIR/bypass_preprocessing_v2.sh"


