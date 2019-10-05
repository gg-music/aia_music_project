import os
import argparse
from datetime import datetime
from collections import OrderedDict

# Disable TF warnings about speed up and future warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Disable warnings from h5py
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# Audio processing and DL frameworks
import librosa
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import load_model

from gtzan import *

# Constants
song_samples = 660000
genres = {'classical': 0, 'hiphop': 1, 'jazz': 2, 'blues': 3, 'rock': 4}
num_genres = len(genres)


def main(args):
    exec_mode = ['train', 'test']
    exec_time = datetime.now().strftime('%Y%m%d%H%M%S')

    # Validate arguments
    if args.type not in exec_mode:
        raise ValueError("Invalid type parameter. Should be 'train' or 'test'.")

    # Start
    if args.type == 'train':
        # Check if the directory path to GTZAN files was inputed
        if not args.directory:
            raise ValueError("File path to model should be passed in test mode.")

        # Create directory to save logs
        try:
            os.mkdir('logs/{}'.format(exec_time))
        except FileExistsError:
            # If the directory already exists
            pass

        # Read the files to memory and split into train test
        X, y = preprocessing(args.directory, genres, song_samples)

        # Transform to a 3-channel image
        X_stack = np.squeeze(np.stack((X,) * 3, -1))
        X_train, X_test, y_train, y_test = train_test_split(X_stack, y, test_size=0.3, random_state=42, stratify=y)

        # Histogram for train and test
        values, count = np.unique(np.argmax(y_train, axis=1), return_counts=True)
        plt.bar(values, count)

        values, count = np.unique(np.argmax(y_test, axis=1), return_counts=True)
        plt.bar(values, count)
        plt.savefig('logs/{}/histogram.png'.format(exec_time),
                    format='png', bbox_inches='tight')

        # Training step
        input_shape = X_train[0].shape
        cnn = build_model(input_shape, num_genres)
        cnn.compile(loss='categorical_crossentropy',
                    optimizer=Adam(),
                    metrics=['accuracy'])

        hist = cnn.fit(X_train, y_train,
                       batch_size=2048,
                       epochs=20,
                       verbose=1,
                       validation_data=(X_test, y_test))

        # Evaluate
        score = cnn.evaluate(X_test, y_test, verbose=0)
        print("val_loss = {:.3f} and val_acc = {:.3f}".format(score[0], score[1]))

        # Plot graphs
        save_history(hist, 'logs/{}/evaluate.png'.format(exec_time))

        # Save the confusion Matrix
        preds = np.argmax(cnn.predict(X_test), axis=1)
        y_orig = np.argmax(y_test, axis=1)
        cm = confusion_matrix(preds, y_orig)

        keys = OrderedDict(sorted(genres.items(), key=lambda t: t[1])).keys()
        plot_confusion_matrix('logs/{}/cm.png'.format(exec_time), cm, keys, normalize=True)

        # Save the model
        cnn.save('models/{}.h5'.format(exec_time))

    else:
        # Check if the file path to the model was passed
        if not args.model:
            raise ValueError("File path to model should be passed in test mode.")

        # Check if was passed the music file
        if not args.song:
            raise ValueError("Song path should be passed in test mode.")

        model = load_model(args.model)
        X = librosa.load(args.song)
