#! /usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/5/4 0012 10:45
# @Author  : jsz
# @Software: PyCharm

import tensorflow as tf
import numpy as np
import os
import matplotlib.pyplot as plt
import skimage.io as io
from scipy.misc import imread, imresize


def get_file(file_dir):
    cover = []
    label_cover = []
    stego = []
    label_stego = []
    # 打标签
    for file in os.listdir(file_dir):
        # if  file.endswith('0') or file.startswith('.'):
        #     continue  # Skip!
        name = file.split('_')
        if name[0] == 'C':
            cover.append(file_dir + file)
            label_cover.append(0)
        if name[0] == 'S':
            stego.append(file_dir + file)
            label_stego.append(1)
    print("这里有 %d cover \n这里有 %d stego"
          % (len(cover), len(stego)))
    # 打乱文件顺序shuffle
    image_list = np.hstack((cover, stego))
    label_list = np.hstack((label_cover, label_stego))
    temp = np.array([image_list, label_list])
    temp = temp.transpose()
    np.random.shuffle(temp)

    image_list = list(temp[:, 0])
    label_list = list(temp[:, 1])
    label_list = [int(i) for i in label_list]

    return image_list, label_list


# %%

def int64_feature(value):
    """Wrapper for inserting int64 features into Example proto."""
    if not isinstance(value, list):
        value = [value]
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))


def bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


# %%

def convert_to_tfrecord(images, labels, save_dir, name):
    '''convert all images and labels to one tfrecord file.
    Args:
        images: list of image directories, string type
        labels: list of labels, int type
        save_dir: the directory to save tfrecord file, e.g.: '/home/folder1/'
        name: the name of tfrecord file, string type, e.g.: 'train'
    Return:
        no return
    Note:
        converting needs some time, be patient...
    '''

    filename = os.path.join(save_dir, name + '.tfrecords')
    n_samples = len(labels)

    if np.shape(images)[0] != n_samples:
        raise ValueError('Images size %d does not match label size %d.' % (images.shape[0], n_samples))

    # wait some time here, transforming need some time based on the size of your data.
    writer = tf.python_io.TFRecordWriter(filename)
    print('\nTransform start......')
    for i in np.arange(0, n_samples):
        try:
            #            image = imread(image[i])

            image = io.imread(images[i])  # type(image) must be array!
            image = imresize(image, (256, 256))
            image_raw = image.tostring()
            label = int(labels[i])
            example = tf.train.Example(features=tf.train.Features(feature={
                'label': int64_feature(label),
                'image_raw': bytes_feature(image_raw)}))
            writer.write(example.SerializeToString())
        except IOError as e:
            print('Could not read:', images[i])
            print('error: %s' % e)
            print('Skip it!\n')
    writer.close()
    print('Transform done!')


# %%

def read_and_decode(tfrecords_file, batch_size):
    '''read and decode tfrecord file, generate (image, label) batches
    Args:
        tfrecords_file: the directory of tfrecord file
        batch_size: number of images in each batch
    Returns:
        image: 4D tensor - [batch_size, width, height, channel]
        label: 1D tensor - [batch_size]
    '''
    # make an input queue from the tfrecord file
    filename_queue = tf.train.string_input_producer([tfrecords_file])

    reader = tf.TFRecordReader()
    _, serialized_example = reader.read(filename_queue)
    img_features = tf.parse_single_example(
        serialized_example,
        features={

            'label': tf.FixedLenFeature([], tf.int64),
            'image_raw': tf.FixedLenFeature([], tf.string),
        })
    image = tf.decode_raw(img_features['image_raw'], tf.uint8)

    ##########################################################
    # you can put data augmentation here, I didn't use it
    ##########################################################
    # all the images of notMNIST are 28*28, you need to change the image size if you use other dataset.


    image = tf.reshape(image, [256, 256])
    label = tf.cast(img_features['label'], tf.int32)
    image_batch, label_batch = tf.train.shuffle_batch([image, label],
                                                      batch_size=batch_size,
                                                      num_threads=64,
                                                      capacity=2000,
                                                      min_after_dequeue=20)
    return image_batch, tf.reshape(label_batch, [batch_size])


# %% Convert data to TFRecord

#test_dir = 'F://CAE_CNN//data//catdogtest//'
test_dir = 'G:\\dataS-UNIWARD0.4\\val\\' 
#save_dir = 'F://CAE_CNN//data//'
save_dir = 'G:\\dataS-UNIWARD0.4\\'
BATCH_SIZE = 25

# Convert test data: you just need to run it ONCE !
name_test = 'S_UNIWARD0.4val'

#images, labels = get_file(test_dir)
#convert_to_tfrecord(images, labels, save_dir, name_test)

# %% TO test train.tfrecord file

def plot_images(images, labels):
    '''plot one batch size
    '''
    for i in np.arange(0, BATCH_SIZE):
        plt.subplot(5, 5, i + 1)
        plt.axis('off')
        plt.title(chr(ord('D') + labels[i] - 1), fontsize=14)
        plt.subplots_adjust(top=1.5)
        plt.imshow(images[i])
    plt.show()


# tfrecords_file = 'C://Users//Windows7//Documents//Python Scripts//notMNIST//test.tfrecords'
tfrecords_file = 'G:\\dataS-UNIWARD0.4\\S_UNIWARD0.4val.tfrecords'

image_batch, label_batch = read_and_decode(tfrecords_file, batch_size=BATCH_SIZE)

with tf.Session()  as sess:
    i = 0
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    try:
        while not coord.should_stop() and i < 1:
            # just plot one batch size
            image, label = sess.run([image_batch, label_batch])
            plot_images(image, label)
            i += 1

    except tf.errors.OutOfRangeError:
        print('done!')
    finally:
        coord.request_stop()
    coord.join(threads)


# %%




















