from gluoncv import model_zoo, data, utils
import json
import mxnet as mx
from mxnet import image
import numpy as np
import os
import time


max_frame_rate = 30
source_file = '/tmp/data/frame.jpg'


# load model
ctx = mx.cpu()
net = model_zoo.get_model('ssd_512_resnet50_v1_voc', pretrained=True, ctx=ctx)


def capture_file(src_file, timeout=1):
    start = time.time()
    while not os.path.exists(source_file):
        time.sleep(1/max_frame_rate)
        if time.time() > start + timeout:
            raise Exception("source file doesn't exist within timeout") 

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

def make_message(label, boxes):
    d = { "Label": label,
          "Bounding_Boxes": boxes }

    return json.dumps(d)

def send_message(msg):
    print(msg)

start = time.time()
frame_cnt = 0
filename = ""
while True:
    try:
        filename = capture_file(source_file)      
        class_IDs, scores, bounding_boxes = predict(filename, net)
        os.remove(filename)

        ppl_boxes = get_object_boxes(net, class_IDs, scores, bounding_boxes, "person")
        send_message(make_message("person", ppl_boxes.tolist()))

        frame_cnt += 1

        dur = time.time() - start
        # print(f"\r{frame_cnt/dur:05.3f} FPS -- {num_ppl} Persons", end="", flush=True)
        print(f"\r{frame_cnt/dur:05.3f} FPS -- {ppl_boxes.shape[0]} Persons") 
        

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
