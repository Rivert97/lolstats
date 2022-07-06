import sys
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
import sklearn.model_selection

datafile = "/datos/lolstats/datasets/final.csv"
truthfile = "/datos/lolstats/datasets/final_truth.csv"

# Model / data parameters
num_classes = 2
input_shape = (80,)

# Get the data
print("Loading dataset...")
x = np.genfromtxt(datafile, delimiter=',')
y = np.genfromtxt(truthfile, delimiter=',')

# split between train and test sets
print("Splitting dataset...")
x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(x, y, test_size=0.20)

print("x_train shape:", x_train.shape)
print(x_train.shape[0], "train samples")
print(x_test.shape[0], "test samples")

# convert class vectors to binary class matrices
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)
print("y_train shape:", y_train.shape)

# Create the model
model = keras.Sequential(
    [
        keras.Input(shape=input_shape),
        layers.Dense(160, activation="relu"),
        layers.Dense(160, activation="relu"),
        layers.Dense(80, activation="relu"),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation="sigmoid"),
    ]
)

model.summary()


# Train the model
print("Training model...")
batch_size = 128
epochs = 100

model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_split=0.1)

# Evaluate the model
print("Evaluating model...")

score = model.evaluate(x_test, y_test, verbose=0)
print("Test loss:", score[0])
print("Test accuracy:", score[1])

