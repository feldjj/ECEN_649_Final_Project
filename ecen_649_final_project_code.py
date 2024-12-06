# -*- coding: utf-8 -*-
"""ECEN 649 Final Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/14viUPYMGsCY_VzCKTIdbXE7uf1qAU_Z_
"""

## File unzipping Changed for each zipped folder.
!tar -xzvf "/content/drive/MyDrive/%%zip_file.tar.gz" -C "/content/drive/MyDrive/Project_Images"

import csv

Pneumothorax_Images = []   ## X-Rays where the patient has Pneumonia
Other_Images = []       ## X-Rays where patient doesn't have Pneumonia
with open("/content/drive/MyDrive/Data_Entry_2017_v2020.csv", "r") as data:
  reader = csv.reader(data)
  for row in reader:
    if "Pneumothorax" in row[1]:         ## Sorting the images based on the Data_Entry folder.
      Pneumothorax_Images.append(row[0])
    else:
      Other_Images.append(row[0])

import os

img_path = "/content/drive/MyDrive/Project_Images/images/"
files = []
for filename in os.listdir(img_path):
  files.append(filename)

Pf = []
Of = []
for f in files:
  if f in Pneumothorax_Images:
    Pf.append(f)
  else:
    Of.append(f)

import random

random.seed(1358) ## A number for repeatability. No specific significance.
Of = random.sample(Of, len(Pf))   ## Random sample of images with no Pneumothorax detected.

relavent_files = Pf + Of

from PIL import Image

img_path = "/content/drive/MyDrive/Project_Images/images/"
save_path = "/content/drive/MyDrive/Project_Images/resized_images/"
new_size = (224, 224)  # Specify the new width and height

for filename in os.listdir(img_path):
    if filename in relavent_files:
      # Open the image
      image = Image.open(img_path + filename)

      # Resize the image
      resized_image = image.resize(new_size)

      # Save the resized image
      resized_image.save(save_path + filename)
    else:
      continue

import keras
from keras import Model
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input, VGG16
import numpy as np
import sklearn as sk

with open('/content/drive/MyDrive/Project_Images/feature_labels.txt', 'w') as labels:   ## Opening file for saving feature labels from VGG16

  for filename in os.listdir(save_path):
    labels.write(filename+',')    ## Including file name before the start of each set for identification

    img = image.load_img(save_path + filename)      ## Loading image
    x = image.img_to_array(img)         ## Convert to array for processing with VGG16
    x = np.expand_dims(x, axis = 0)
    x = preprocess_input(x)

    base_model = VGG16(weights = 'imagenet', include_top = False)
    model = Model(inputs = base_model.input, outputs = base_model.get_layer('block1_pool').output)
    xb = model.predict(x)              ## Generating feature labels with VGG16

    F = np.mean(xb, axis=(0,1,2))
    Fs = ','.join(str(f) for f in F)
    labels.write(Fs + '\n')            ## Writing to a file so that this step doesn't need to be repeated.

flP = []
flO = []

## Generating arrays of the feature vectors sorted by classification.
with open('/content/drive/MyDrive/Project_Images/feature_labels.txt', 'r') as labels:
  for line in labels:
    line = line.strip('\n')
    line_array = line.split(',')
    if line_array[0] in Pf:
      flP.append(line_array[1:])
    else:
      flO.append(line_array[1:])

for i in range(len(flP)):
  flP[i] = [float(x) for x in flP[i]]
for i in range(len(flO)):
  flO[i] = [float(x) for x in flO[i]]

train_len = int(len(flP)*.7)
## Assumption that images aren't ordered, so can split them without randomness.
## Seperated into training and testing data for classification.

flP_train = flP[:train_len]
flP_test = flP[train_len:]
flO_train = flO[:train_len]
flO_test = flO[train_len:]

train_data = flP_train + flO_train
test_data = flP_test + flO_test

train_labels = [0]*len(flP_train) + [1]*len(flO_train)
test_labels = [0]*len(flP_test) + [1]*len(flO_test)

from sklearn.svm import SVC                           ## SVC rbf classifier
from sklearn.metrics import roc_auc_score

clf_svc = SVC(kernel = 'rbf', C = 1, gamma = 'scale')
clf_svc.fit(train_data, train_labels)

accuracy = clf_svc.score(test_data, test_labels)
auc = roc_auc_score(test_labels, clf_svc.predict(test_data))
print(f"Accuracy of rbf classifier: {accuracy}")
print(f"AUC of rbf classifier: {auc}")

from sklearn.neighbors import KNeighborsClassifier   ## KNN classifier

clf_knn = KNeighborsClassifier(n_neighbors = 3)
clf_knn.fit(train_data, train_labels)

accuracy = clf_knn.score(test_data, test_labels)
auc = roc_auc_score(test_labels, clf_knn.predict(test_data))
print(f"Accuracy of 5NN classifier: {accuracy}")
print(f"AUC of 5NN classifier: {auc}")

from sklearn.naive_bayes import GaussianNB          ## Naive Bayes classifier
gnb = GaussianNB()
gnb.fit(train_data, train_labels)

accuracy = gnb.score(test_data, test_labels)
auc = roc_auc_score(test_labels, gnb.predict(test_data))
print(f"Accuracy of Naive Bayes Classifier: {accuracy}")
print(f"AUC of Naive Bayes Classifier: {auc}")

## Start DenseNet121 related code

import keras
from keras import Model
from keras.preprocessing import image
from keras.applications.densenet import preprocess_input, DenseNet121
import numpy as np
import sklearn as sk

img_path = "/content/drive/MyDrive/Project_Images/resized_images/"

with open('/content/drive/MyDrive/Project_Images/feature_labels_densenet.txt', 'w') as labels:   ## Opening file for saving feature labels from DenseNet121

  for filename in os.listdir(img_path):
    labels.write(filename+',')    ## Including file name before the start of each set for identification

    img = image.load_img(img_path + filename)      ## Loading image
    x = image.img_to_array(img)         ## Convert to array for processing with DenseNet121
    x = np.expand_dims(x, axis = 0)
    x = preprocess_input(x)

    base_model = DenseNet121(weights = 'imagenet', include_top = False, input_shape = (224, 224, 3))
    model = Model(inputs = base_model.input, outputs = base_model.output)
    xb = model.predict(x)              ## Generating feature labels with DenseNet121

    F = np.mean(xb, axis=(0,1,2))
    Fs = ','.join(str(f) for f in F)
    labels.write(Fs + '\n')            ## Writing to a file so that this step doesn't need to be repeated.

dnP = []
dnO = []

## Generating arrays of the feature vectors sorted by classification.
with open('/content/drive/MyDrive/Project_Images/feature_labels_densenet.txt', 'r') as labels:
  for line in labels:
    line = line.strip('\n')
    line_array = line.split(',')
    if line_array[0] in Pf:
      dnP.append(line_array[1:])
    else:
      dnO.append(line_array[1:])

for i in range(len(dnP)):
  dnP[i] = [float(x) for x in dnP[i]]
for i in range(len(dnO)):
  dnO[i] = [float(x) for x in dnO[i]]

DNtrain_len = int(len(dnP)*.7)

dnP_train = dnP[:DNtrain_len]
dnP_test = dnP[DNtrain_len:]
dnO_train = dnO[:DNtrain_len]
dnO_test = dnO[DNtrain_len:]

DNtrain_data = dnP_train + dnO_train
DNtest_data = dnP_test + dnO_test

DNtrain_labels = [0]*len(dnP_train) + [1]*len(dnO_train)
DNtest_labels = [0]*len(dnP_test) + [1]*len(dnO_test)

from sklearn.svm import SVC                           ## SVC rbf classifier

clf_svc = SVC(kernel = 'rbf', C = 1, gamma = 'scale')
clf_svc.fit(DNtrain_data, DNtrain_labels)

accuracy = clf_svc.score(DNtest_data, DNtest_labels)
print(f"Accuracy of rbf classifier: {accuracy}")

from sklearn.neighbors import KNeighborsClassifier   ## KNN classifier

clf_knn = KNeighborsClassifier(n_neighbors = 3)
clf_knn.fit(DNtrain_data, DNtrain_labels)

accuracy = clf_knn.score(DNtest_data, DNtest_labels)
print(f"Accuracy of 5NN classifier: {accuracy}")

from sklearn.naive_bayes import GaussianNB          ## Naive Bayes classifier
gnb = GaussianNB()
gnb.fit(DNtrain_data, DNtrain_labels)

accuracy = gnb.score(DNtest_data, DNtest_labels)
print(f"Accuracy of Naive Bayes Classifier: {accuracy}")