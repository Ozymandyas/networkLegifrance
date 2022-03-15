# -*- coding: utf-8 -*-
import json
import pandas as pd
import numpy as np
import math
import os
import matplotlib.pyplot as plt

df = pd.read_json("CGI_v.json", encoding='utf-8')

df['len'] = df.content.str.len()

df = df[df['len']>50]

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.models import Model
from keras.layers import LSTM, Dense, Input, Embedding, Dropout
from keras.optimizers import RMSprop
from keras.layers import Bidirectional, GlobalMaxPool1D
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping

X = df.content
Y = pd.get_dummies(df.year)
del df

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.33, random_state=42)

max_words = 10000
max_len = 150 
tok = Tokenizer(num_words=max_words)
tok.fit_on_texts(X_train)


sequences = tok.texts_to_sequences(X_train)
sequences_matrix = sequence.pad_sequences(sequences,maxlen=max_len)

test_sequences = tok.texts_to_sequences(X_test)
test_sequences_matrix = sequence.pad_sequences(test_sequences,maxlen=max_len)

# len(set(list(Y))) == 43 therefore 43 classesto predict

def RNN():
    inputs = Input(name='inputs',shape=[max_len])
    layer = Embedding(max_words,128,input_length=max_len)(inputs)
    layer = Bidirectional(LSTM(32, return_sequences = False))(layer)
    layer = Dense(20, activation="relu")(layer)
    layer = Dropout(0.05)(layer)
    layer = Dense(43,activation = "sigmoid", name='out_layer')(layer)
    model = Model(inputs=inputs,outputs=layer)
    return model

model = RNN()
model.summary()
model.compile(loss='categorical_crossentropy',optimizer=RMSprop(),metrics=['accuracy'])

### attention très long :
#model.fit(sequences_matrix,Y_train,batch_size=100,epochs=8,validation_split=0.2)

accr = model.evaluate(test_sequences_matrix,Y_test)

print('Test set accuracy: {:0.3f}'.format(accr[1]), ', random would be: {:0.3f}'.format(1/43))
#Test set accuracy: 0.052 , random would be: 0.023

