import numpy as np
import os
import re
import fnmatch
from PIL import Image

def readJPGFile(filename):
    # read in the image and convert it to grayscale
    img = Image.open(filename).convert('L')
    # return the numpy array of the image
    return np.asarray(img).reshape(160,300,1)

def read_images_from_directory(directory):
    files = sorted([f for f in os.listdir(directory) if fnmatch.fnmatch(f, '*.jpg')])
    images = [readJPGFile('{}/{}'.format(directory,f)) for f in files]
    return np.array(images, dtype=np.float32)

def get_data(base_dir, train_percent, val_percent):
    pos = read_images_from_directory('{}/{}'.format(base_dir,'yes'))
    neg = read_images_from_directory('{}/{}'.format(base_dir,'no'))
    pos_len = len(pos)
    neg_len = len(neg)
    pos_indices = [int(train_percent*pos_len)]
    neg_indices = [int(train_percent*neg_len)]
    np.random.shuffle(pos)
    np.random.shuffle(neg)
    train_pos, val_pos = np.split(pos, pos_indices)
    train_neg, val_neg = np.split(neg, neg_indices)
    
    print(train_pos.shape)
    print(train_neg.shape)
    
    ins_train = np.concatenate((train_pos, train_neg))
    
    outs_train_pos = np.append(np.ones((train_pos.shape[0],1)), np.zeros((train_pos.shape[0],1)), axis=1)
    outs_train_neg = np.append(np.zeros((train_neg.shape[0],1)), np.ones((train_neg.shape[0],1)), axis=1)
    outs_train = np.append(outs_train_pos, outs_train_neg, axis=0)
    
    ins_val = np.concatenate((val_pos, val_neg))

    outs_val_pos = np.append(np.ones((val_pos.shape[0],1)), np.zeros((val_pos.shape[0],1)), axis=1)
    outs_val_neg = np.append(np.zeros((val_neg.shape[0],1)), np.ones((val_neg.shape[0],1)), axis=1)
    outs_val = np.append(outs_val_pos, outs_val_neg, axis=0)
    
    return ins_train, outs_train, ins_val, outs_val


if __name__ == '__main__':
    ins_train, outs_train, ins_val, outs_val = get_data('data', .9, .1)
    np.save('data/ins_train', ins_train)
    np.save('data/outs_train', outs_train)
    np.save('data/ins_val', ins_val)
    np.save('data/outs_val', outs_val)
