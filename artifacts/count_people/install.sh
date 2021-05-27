#!/bin/bash

echo "start install"
# as root
# chmod -R o+w /home/ggc_user

pip3 install virtualenv
echo "venv ready"

virtualenv gcv
echo "venv created"
source /home/ggc_user/gcv/bin/activate
echo "install reqs from $dist_home"
pip3 install -r $dist_home/requirements.txt

echo "pip'ed"