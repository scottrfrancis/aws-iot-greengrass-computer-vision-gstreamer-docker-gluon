from gluoncv import model_zoo, data, utils
import json
import mxnet as mx
from mxnet import image
import numpy as np
import os
import time


# debug harness
# if os.getenv("AWS_GG_NUCLEUS_DOMAIN_SOCKET_FILEPATH_FOR_COMPONENT") == None:
#     print("setting socket for debug")
#     os.environ["AWS_GG_NUCLEUS_DOMAIN_SOCKET_FILEPATH_FOR_COMPONENT"] = "/greengrass/v2/ipc.socket"

import IPCUtils as ipcutil
# from labels import labels
from awscrt.io import (
    ClientBootstrap,
    DefaultHostResolver,
    EventLoopGroup,
    SocketDomain,
    SocketOptions,
)
from awsiot.eventstreamrpc import Connection, LifecycleHandler, MessageAmendment
from awsiot.greengrasscoreipc.model import PublishToIoTCoreRequest
import awsiot.greengrasscoreipc.client as client


print("loading the IPC Client")
ipc_utils = ipcutil.IPCUtils()
connection = ipc_utils.connect()
ipc_client = client.GreengrassCoreIPCClient(connection)
print("loaded")

max_frame_rate = 30
source_file = '/tmp/data/frame.jpg'
# source_file = '/tmp/data/save.jpg'

topic = "demo/topic"


# load model
ctx = mx.cpu()
net = model_zoo.get_model('ssd_512_resnet50_v1_voc', pretrained=True, ctx=ctx)


def capture_file(src_file, timeout=1):
    start = time.time()
    while not os.path.exists(source_file):
        time.sleep(1/max_frame_rate)
        if time.time() > start + timeout:
            raise Exception(f"source {src_file} doesn't exist within timeout") 

    ms_count = int((time.time() %1)*1000)
    path_parts = list(os.path.split(source_file))
    file_parts = path_parts[-1].split('.')

    file_parts[-2] += str(ms_count)
    path_parts[-1] = ".".join(file_parts)

    new_file = os.path.join(*path_parts)
    os.rename(source_file, new_file)

    return new_file


def predict(filename, network):
    x, img = data.transforms.presets.ssd.load_test(filename, short=512)
    class_IDs, scores, bounding_boxes = net(x)

    return class_IDs, scores, bounding_boxes


def get_object_boxes(network, class_ids, scores, bounding_boxes, object_label, threshold=0.75):
    good_scores = (scores[0,:,0] > threshold)
    good_classes = (class_ids[0,:,0] == network.classes.index(object_label))

    boxes = bounding_boxes[0,:,:].asnumpy()[(good_scores.asnumpy()*good_classes.asnumpy()) > 0]

    return boxes

def make_message(label, boxes, frame_rate):
    d = { "Label": label,
          "Count": len(boxes),
          "Bounding_Boxes": boxes,
          "Frame_Rate": frame_rate }

    return json.dumps(d)

def send_message(msg):
    print(msg)
    ipc_client.new_publish_to_iot_core().activate(
               request=PublishToIoTCoreRequest(topic_name=topic, qos='0',
                                            payload=msg.encode()))

start = time.time()
frame_cnt = 0
filename = ""
while True:
    try:
        filename = capture_file(source_file)      
        class_IDs, scores, bounding_boxes = predict(filename, net)
        os.remove(filename)

        ppl_boxes = get_object_boxes(net, class_IDs, scores, bounding_boxes, "person")
        frame_cnt += 1
        frame_rate = frame_cnt/(time.time() - start)

        send_message(make_message("person", ppl_boxes.tolist(), frame_rate))
        # print(f"\r{frame_cnt/dur:05.3f} FPS -- {num_ppl} Persons", end="", flush=True)
        print(f"\r{frame_rate:05.3f} FPS -- {ppl_boxes.shape[0]} Persons") 
        

    except Exception as e:
        print(e)

    finally: 
        try:
            os.remove(filename)
        except Exception as e:
            pass

try:
    os.remove(filename)
except Exception as e:
    pass
