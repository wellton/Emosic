from keras.preprocessing import image
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Activation, Dropout, Flatten, Dense
from math import floor
import csv
import numpy as np

def load_images(paths, labels, batch_size=32):
    while True:
        batch_n = 0
        batch_d = []
        batch_l = []
        for i in range(batch_size):
            if batch_n*batch_size + i > len(paths):
                batch_n = 0
                break
            path = paths[batch_n*batch_size + i]
            img = image.load_img(path, target_size=(256, 256))
            x = image.img_to_array(img)
            y = labels[batch_n*batch_size + i]
            batch_d.append(x)
            batch_l.append(y)
        batch_d = np.array(batch_d).reshape(batch_size, 256, 256, 3)
        batch_l = np.array(batch_l).reshape(batch_size, 2)
        yield (batch_d, batch_l)
        batch_n += 1

def load_paths(p):
    labels = []
    paths = []
    with open(p, 'r') as csvfile:
        r = csv.reader(csvfile, delimiter=',')
        count = 0
        for row in r:
            if 'sub' in row[0]:
                continue
            valence = float(row[-2])
            arousal = float(row[-1])
            if arousal == -2 or valence == -2:
                continue
            # emotion = int(row[-3])
            path =  'data_p/' + row[0]
            paths.append(path)
            labels.append([valence, arousal])
    return paths, labels

model = Sequential()

# TODO define model here
model.add(Conv2D(16, (9, 9), activation='relu', input_shape=(256,256,3)))
model.add(Conv2D(16, (9, 9), activation='relu', input_shape=(256,256,3)))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(32, (5, 5), activation='relu'))
model.add(Conv2D(32, (5, 5), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())
model.add(Dense(1024, activation='relu'))
model.add(Dropout(0.4))
model.add(Dense(1024, activation='relu'))
model.add(Dropout(0.4))
model.add(Dense(2, activation='linear'))

model.compile(loss='mean_squared_error', optimizer='adam')

t_paths, t_labels = load_paths('training.csv')
v_paths, v_labels = load_paths('validation.csv')
batch_size = 32

model.fit_generator(
        load_images(t_paths,t_labels, batch_size),
        steps_per_epoch=2000 // batch_size,
        epochs=50,
        validation_data=load_images(v_paths,v_labels, batch_size),
        validation_steps=800 // batch_size)

model.save_weights('aff_net.h5')
