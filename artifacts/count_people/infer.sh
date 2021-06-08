#!/bin/bash

echo "hostname $AWS_GG_NUCLEUS_DOMAIN_SOCKET_FILEPATH_FOR_COMPONENT"
fullcmd="$(realpath $0)" 
thispath="$(dirname $fullcmd)"
echo "thispath: $thispath"

source ~/gcv/bin/activate

python3 $thispath/infer.py -c person -m ssd_512_resnet50_v1_voc -r 0.1 -s /tmp/data/frame.jpg -t demo/topic -z 0.75
