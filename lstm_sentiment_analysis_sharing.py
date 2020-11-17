# -*- coding: utf-8 -*-
"""lstm_sentiment_analysis_sharing.ipynb

Automatically generated by Colaboratory.

"""

!pip install -q tfds-nightly
!pip install -q tensorflow-hub

import os
import re
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_datasets as tfds
from tensorflow import keras
from tensorflow.keras import layers

# Load compressed models from tensorflow_hub
os.environ["TFHUB_MODEL_LOAD_FORMAT"] = "COMPRESSED"

print("Version: ", tf.__version__)
print("Eager mode: ", tf.executing_eagerly())
print("Hub version: ", hub.__version__)
print("GPU is", "available" if tf.config.experimental.list_physical_devices("GPU") else "NOT AVAILABLE")

train_data, validation_data, test_data = tfds.load(
    name="imdb_reviews", 
    split=('train[:80%]', 'train[80%:]', 'test'),
    as_supervised=True)

#embedding = "https://tfhub.dev/google/Wiki-words-500-with-normalization/2"
embedding = "https://tfhub.dev/google/Wiki-words-250-with-normalization/2"
#embedding = "https://tfhub.dev/google/Wiki-words-500/2"
#embedding = "https://tfhub.dev/google/Wiki-words-250/2"

#experiment with trainable=True and trainable=False

hub_layer = hub.KerasLayer(embedding, input_shape=[], dtype=tf.string, trainable=True)
#hub_layer = hub.KerasLayer(embedding, input_shape=[], dtype=tf.string, trainable=False) # unstable training

train_examples_batch, train_labels_batch = next(iter(train_data.batch(10)))
trial_embeddings = hub_layer(np.array(['actor', 'boy', 'actress', 'girl']))
#train_examples_batch[:3]
trial_vector = trial_embeddings[0] - trial_embeddings[1] + trial_embeddings[3]
actual_vector = trial_embeddings[2]

dist = np.sum((trial_vector-actual_vector)**2)
actual_vec_length = np.sum(actual_vector**2)

print('distance L2 norm : ', dist)
print('actual vector L2 norm : ', actual_vec_length)

#original model
#unstable with non trainable embeddings

#model = keras.Sequential()
#model.add(layers.Input((None, 250)))
#model.add(layers.LSTM(64))
#model.add(layers.Dense(128, activation='relu'))
#model.add(layers.Dense(1))
#model.summary()

#Fewer LSTM cells - very slow start, but similar to original model

#model = keras.Sequential()
#model.add(layers.Input((None, 250)))
#model.add(layers.LSTM(32))
#model.add(layers.Dense(128, activation='relu'))
#model.add(layers.Dense(1))
#model.summary()

#More LSTM cells, less Fully connected neurons - did not work

#model = keras.Sequential()
#model.add(layers.Input((None, 250)))
#model.add(layers.LSTM(128))
#model.add(layers.Dense(64, activation='relu'))
#model.add(layers.Dense(1))
#model.summary()

#two LSTM layers - best results so far

model = keras.Sequential()
model.add(layers.Input((None, 250)))
model.add(layers.LSTM(32, return_sequences=True))
model.add(layers.LSTM(64))
model.add(layers.Dense(128, activation='relu'))
model.add(layers.Dense(1))
model.summary()

#two LSTM layers more units in first LSTM layer

#model = keras.Sequential()
#model.add(layers.Input((None, 250)))
#model.add(layers.LSTM(64, return_sequences=True))
#model.add(layers.LSTM(64))
#model.add(layers.Dense(128, activation='relu'))
#model.add(layers.Dense(1))
#model.summary()

#train_batch, train_labels_batch = next(iter(train_data.batch(1)))
size = 350
train_embeddings = np.zeros((len(train_data), size, 250), dtype=np.float32)
train_labels = np.zeros(len(train_data), dtype=np.float32)
bg_embedding = np.zeros((size, 250), dtype=np.float32)
i = 0
for train_sample, train_label in train_data:
  #text_preproc = keras.preprocessing.text.text_to_word_sequence()(train_sample)
  punc_strip = re.sub(r'[^\w\s]', '', str(train_sample))
  punc_strip = punc_strip.lower()
  train_embedding = hub_layer(punc_strip.split(' '))
  padded_embedding = np.copy(bg_embedding)
  padded_embedding[:np.minimum(size, train_embedding.shape[0]), :] = train_embedding[:np.minimum(size, train_embedding.shape[0]), :]
  #train_embedding = np.expand_dims(train_embedding, axis=0)
  #train_embeddings.append(train_embedding)
  train_embeddings[i, :, :] = padded_embedding
  train_labels[i] = float(train_label)
  i = i+1

print(train_embeddings.shape)
print(train_labels.shape)

val_embeddings = np.zeros((len(validation_data), size, 250), dtype=np.float32)
val_labels = np.zeros(len(validation_data), dtype=np.float32)
bg_embedding = np.zeros((size, 250), dtype=np.float32)
i = 0
for val_sample, val_label in validation_data:
  #text_preproc = keras.preprocessing.text.text_to_word_sequence()(train_sample)
  punc_strip = re.sub(r'[^\w\s]', '', str(val_sample))
  punc_strip = punc_strip.lower()
  val_embedding = hub_layer(punc_strip.split(' '))
  padded_embedding = np.copy(bg_embedding)
  padded_embedding[:np.minimum(size, val_embedding.shape[0]), :] = val_embedding[:np.minimum(size, val_embedding.shape[0]), :]
  #train_embedding = np.expand_dims(train_embedding, axis=0)
  #train_embeddings.append(train_embedding)
  val_embeddings[i, :, :] = padded_embedding
  val_labels[i] = float(val_label)
  i = i+1

print(val_embeddings.shape)
print(val_labels.shape)
model.compile(optimizer='Adam', loss=tf.keras.losses.BinaryCrossentropy(from_logits=True), metrics=['accuracy'])

for i in range(6):
  print('epoch set : ', i+1)
  model.fit(train_embeddings, train_labels, 10, epochs=5, validation_data=(val_embeddings, val_labels))