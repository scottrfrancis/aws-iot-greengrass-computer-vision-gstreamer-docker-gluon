#!/bin/bash

echo "hostname $AWS_GG_NUCLEUS_DOMAIN_SOCKET_FILEPATH_FOR_COMPONENT"
fullcmd="$(realpath $0)" 
thispath="$(dirname $fullcmd)"
echo "thispath: $thispath"

source ~/gcv/bin/activate

while getopts ":c:m:r:s:t:z:" o ; do
    case "${o}" in 
        c)
            class_name=${OPTARG}
            ;;
        m)
            model_name=${OPTARG}
            ;;
        r)
            frame_rate=${OPTARG}
            ;;
        s)
            source_file=${OPTARG}
            ;;
        t)
            topic_name=${OPTARG}
            ;;
        z)
            threshold=${OPTARG}
            ;;
    esac
done


python3 $thispath/infer.py -c $class_name -m $model_name -r $frame_rate -s $source_file -t $topic_name -z $threshold
