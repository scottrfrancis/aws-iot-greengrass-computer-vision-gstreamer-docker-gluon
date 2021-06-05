#!/bin/bash

echo "hostname $AWS_GG_NUCLEUS_DOMAIN_SOCKET_FILEPATH_FOR_COMPONENT"
fullcmd="$(realpath $0)" 
thispath="$(dirname $fullcmd)"
echo "thispath: $thispath"

source ~/gcv/bin/activate

# [[ -z "${"AWS_GG_NUCLEUS_DOMAIN_SOCKET_FILEPATH_FOR_COMPONENT"}" ]] && export AWS_GG_NUCLEUS_DOMAIN_SOCKET_FILEPATH_FOR_COMPONENT="/greengrass/v2/ipc.socket"
# echo "hostname: $AWS_GG_NUCLEUS_DOMAIN_SOCKET_FILEPATH_FOR_COMPONENT"

python3 $thispath/infer.py
