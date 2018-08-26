#!/bin/bash
DIR=$( dirname "$(readlink -f "$0")" )

conda env update -n gridwm -f $DIR/environment.yml

cat>$DIR/gridwm <<EOT
#!/bin/bash

source activate gridwm
python ${DIR}/gridwm.py
source deactivate

EOT

sudo chmod u+x $DIR/gridwm
sudo mv $DIR/gridwm /usr/local/bin/gridwm