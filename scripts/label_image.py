# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys
import time

import numpy as np
import tensorflow as tf

import os
import pandas as pd

import urllib

def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.GraphDef()

  with open(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph

def read_tensor_from_image_file(file_name, input_height=299, input_width=299,
				input_mean=0, input_std=255, r=False):
  if not r:
    input_name = "file_reader"
    output_name = "normalized"
    file_reader = tf.read_file(file_name, input_name)
  else:
    # Open specified url and load image as a string
    file_reader = urllib.request.urlopen(file_name).read()
  if file_name.endswith(".png"):
    image_reader = tf.image.decode_png(file_reader, channels = 3,
                                       name='png_reader')
  elif file_name.endswith(".gif"):
    image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                  name='gif_reader'))
  elif file_name.endswith(".bmp"):
    image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
  else:
    image_reader = tf.image.decode_jpeg(file_reader, channels = 3,
                                        name='jpeg_reader')
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0);
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)

  return result

def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label

if __name__ == "__main__":
  file_name = "tf_files/flower_photos/daisy/3475870145_685a19116d.jpg"
  model_file = "tf_files/retrained_graph.pb"
  label_file = "tf_files/retrained_labels.txt"
  input_height = 224
  input_width = 224
  input_mean = 128
  input_std = 128
  input_layer = "input"
  output_layer = "final_result"

  parser = argparse.ArgumentParser()
  parser.add_argument("--image", help="image to be processed")
  parser.add_argument("--graph", help="graph/model to be executed")
  parser.add_argument("--labels", help="name of file containing labels")
  parser.add_argument("--input_height", type=int, help="input height")
  parser.add_argument("--input_width", type=int, help="input width")
  parser.add_argument("--input_mean", type=int, help="input mean")
  parser.add_argument("--input_std", type=int, help="input std")
  parser.add_argument("--input_layer", help="name of input layer")
  parser.add_argument("--output_layer", help="name of output layer")
  parser.add_argument("--dir", help="boolean, is directory")
  parser.add_argument("--r", help="boolean, is url")
  args = parser.parse_args()

  if args.graph:
    model_file = args.graph
  if args.image:
    file_name = args.image
  if args.labels:
    label_file = args.labels
  if args.input_height:
    input_height = args.input_height
  if args.input_width:
    input_width = args.input_width
  if args.input_mean:
    input_mean = args.input_mean
  if args.input_std:
    input_std = args.input_std
  if args.input_layer:
    input_layer = args.input_layer
  if args.output_layer:
    output_layer = args.output_layer
  if args.r:
    isURL = True
  else:
    isURL = False

  multiple_images = False
  files = []
  if args.dir:
    search_dir = args.dir
    multiple_images = True
    for filename in os.listdir(search_dir):
      files.append(search_dir + filename)

  ## single image classification
  if not files:
    graph = load_graph(model_file)
    t = read_tensor_from_image_file(file_name,
                                    input_height=input_height,
                                    input_width=input_width,
                                    input_mean=input_mean,
                                    input_std=input_std,
                                    r = isURL)

    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    input_operation = graph.get_operation_by_name(input_name);
    output_operation = graph.get_operation_by_name(output_name);

    with tf.Session(graph=graph) as sess:
      start = time.time()
      results = sess.run(output_operation.outputs[0],
                        {input_operation.outputs[0]: t})
      end=time.time()
    results = np.squeeze(results)

    top_k = results.argsort()[-5:][::-1]
    labels = load_labels(label_file)

    json_ret = {}
    res = {}
    for i in top_k:
      print(labels[i], results[i])
      res[labels[i]] = results[i]
    json_ret[file_name] = res

  else:
    jsonDict = []
    fname = []
    total = []
    partial = []
    none = []
    for f in files:
      if f.endswith('.jpg'): 
        graph = load_graph(model_file)
        t = read_tensor_from_image_file(f,
                                        input_height=input_height,
                                        input_width=input_width,
                                        input_mean=input_mean,
                                        input_std=input_std,
                                        r = isURL)

        input_name = "import/" + input_layer
        output_name = "import/" + output_layer
        input_operation = graph.get_operation_by_name(input_name);
        output_operation = graph.get_operation_by_name(output_name);

        with tf.Session(graph=graph) as sess:
          start = time.time()
          results = sess.run(output_operation.outputs[0],
                            {input_operation.outputs[0]: t})
          end=time.time()
        results = np.squeeze(results)

        top_k = results.argsort()[-5:][::-1]
        labels = load_labels(label_file)

        print('\nEvaluation time (1-image): {:.3f}s\n'.format(end-start))
        json_ret = {}
        res = {}
        for i in top_k:
          if labels[i] == 'partials':
            partial.append(results[i])
          elif labels[i] == 'total eclipses':
            total.append(results[i])
          elif labels[i] == 'not space':
            none.append(results[i])
          res[labels[i]] = results[i]
        json_ret[f] = res
        jsonDict.append(json_ret)
        fname.append(f)
  if multiple_images:
    df = pd.DataFrame({"file_name": fname, "total": total, 'partial': partial, 'none': none})
    df.to_csv("./eclipseClassif.csv")



