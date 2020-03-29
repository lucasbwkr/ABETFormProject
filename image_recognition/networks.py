import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import InputLayer
from tensorflow.keras.layers import Convolution2D, Dense, MaxPooling2D, Flatten, Dropout
import random


'''
Params:
  image_size: size of image
   nchannels: number of channels in the image
convolutions: a list of tuples specifiying the number of filters and the kernel size for each convolutional layer
     pooling: a list of pooling sizes after every convolutional layer; a 0 indicates there is no pooling
       dense: a list of dense layer sizes after the flatten layer
   n_classes: number of classes in the output
   lambda_L2: l2 regularizer
   p_dropout: dropout rate
       lrate: learning rate
''' 

def create_classifier_network(image_size, nchannels, convolutions, pooling, dense, n_classes=2, lambda_l2=.0001, p_dropout=0.5, lrate=.001):
    model = Sequential()
    model.add(InputLayer(input_shape=(image_size[0], image_size[1], nchannels),name='input'))
   
    ### Add convolutional layers
    for i, (n_filters, kernel_size) in enumerate(convolutions):
        name = 'C' + str(i)
        model.add(Convolution2D(filters=n_filters,
                               kernel_size=(kernel_size,kernel_size),
                               strides=2,
                               padding='valid',
                               use_bias=True,
                               kernel_initializer='random_uniform',
                               bias_initializer='zeros',
                               name=name,
                               activation='elu',
                               kernel_regularizer=tf.keras.regularizers.l2(lambda_l2)
    ))
        # Adding pooling layer if specified
        if pooling[i] != 0:
            model.add(MaxPooling2D(pool_size=(pooling[i],pooling[i]),
                           strides=(pooling[i],pooling[i]),
                           padding='valid'))
        
    
    model.add(Flatten()) # Turn the model into a 2d tensor
    
    # Add dense layers
    for i,d in enumerate(dense): 
        name = 'D' + str(i)
        model.add(Dense(units=d,
                       activation='elu',
                       use_bias=True,
                       kernel_initializer='truncated_normal',
                       bias_initializer='zeros',
                       name=name,
                       kernel_regularizer=tf.keras.regularizers.l2(lambda_l2)))
    
        model.add(Dropout(p_dropout))
    
    # Add output layer with softmax activation
    model.add(Dense(units=n_classes,
                   activation='softmax',
                   use_bias=True,
                   bias_initializer='zeros',
                   name='output',
                   kernel_initializer='truncated_normal',
                   kernel_regularizer=tf.keras.regularizers.l2(lambda_l2)))
    
    opt = tf.keras.optimizers.Adam(lr=lrate, beta_1=.9, beta_2=0.999,
                                 epsilon=None, decay=0.0, amsgrad=False)
    
    model.compile(loss='binary_crossentropy', optimizer=opt,
                 metrics=['accuracy'])
    
    print(model.summary())
    
    return model


def training_set_generator_images(ins, outs, batch_size=10,
                          input_name='input', 
                        output_name='output'):
    '''
    Generator for producing random mini-batches of image training samples.
    
    @param ins Full set of training set inputs (examples x row x col x chan)
    @param outs Corresponding set of sample (examples x nclasses)
    @param batch_size Number of samples for each minibatch
    @param input_name Name of the model layer that is used for the input of the model
    @param output_name Name of the model layer that is used for the output of the model
    '''
    
    while True:
        # Randomly select a set of example indices
        example_indices = random.choices(range(ins.shape[0]), k=batch_size)
        
        # The generator will produce a pair of return values: one for inputs and one for outputs
        yield({input_name: ins[example_indices,:,:,:]},
             {output_name: outs[example_indices,:]})
