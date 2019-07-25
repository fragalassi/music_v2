#!/bin/bash

SCRIPTDIR=/temp_dd/igrida-fs1/fgalassi/music_v2
SCRIPTDIR=/udd/fgalassi/music_v2
echo "$SCRIPTDIR"

chmod +x $SCRIPTDIR/bypass_preprocessing_v2.sh

oarsub -p "dedicated='none'" -l /nodes=1,core=6,walltime=20:00:00 "$SCRIPTDIR/bypass_preprocessing_v2.sh"

#-t besteffort -t idempotent -p


