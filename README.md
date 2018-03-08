# Overview

This repo contains code adapted from the "TensorFlow for poets 2" series of codelabs.

The code is modified to accomodate running a directory with thousands of images and exporting the results to a csv. 

## eclipse_image_classification

(Re)Training the Model:

  Specify Architecture and Image Size:

  IMAGE_SIZE=224
  ARCHITECTURE="mobilenet_0.50_${IMAGE_SIZE}"

  Run training script:

  python -m scripts.retrain \
    --bottleneck_dir=tf_files/bottlenecks \
    --model_dir=tf_files/models/"${ARCHITECTURE}" \
    --summaries_dir=tf_files/training_summaries/"${ARCHITECTURE}" \
    --output_graph=tf_files/retrained_graph.pb \
    --output_labels=tf_files/retrained_labels.txt \
    --architecture="${ARCHITECTURE}" \
    --image_dir=[PATH/TO/TRAINING_DATA]

To run classification on directory for .jpg images use command:

python -m scripts.label_image \
    --graph=tf_files/retrained_graph.pb  \
    --dir=[PATH/TO/DIRECTORY]
   
Once the script receives the path to the directory, it will grab all images of the .jpg type and classify them accoring to the model.

Once all images in the directory are run, the program will export a .csv file to the current directory.
