import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers
from matplotlib import pyplot as plt
import keras

def plot_the_loss_curve(epochs, mse):
    """Plot a curve of loss vs. epoch."""

    plt.figure()
    plt.xlabel("Epoch")
    plt.ylabel("Mean Squared Error")

    plt.plot(epochs, mse, label="Loss")
    plt.legend()
    plt.show()

print("Defined the plot_the_loss_curve function.")


def create_model(shapeinput, learning_rate):
    # Create the model.
    my_model = keras.Sequential()

    # Input shape corresponds to the number of columns (the features day, month and year) of the dataframe,
    # excpet for the output label, the temperature.

    my_model.add(keras.layers.Dense(50, kernel_initializer='uniform', activation='relu', input_shape=shapeinput))
    #my_model.add(keras.layers.Dense(85, kernel_initializer='uniform', activation='relu'))
    #my_model.add(keras.layers.Dense(85, kernel_initializer='uniform', activation='relu'))
    my_model.add(keras.layers.Dense(50, kernel_initializer='uniform', activation='relu'))
    my_model.add(keras.layers.Dense(50, kernel_initializer='uniform', activation='relu'))
    my_model.add(keras.layers.Dense(1, kernel_initializer='uniform', activation='relu'))

    opt = keras.optimizers.Adam(learning_rate)
    my_model.compile(loss='mean_squared_error', optimizer=opt)

    return my_model


def train_model(model, xvalues, yvalues, epochs, batch_size=None):
    """Train the model by feeding it data."""

    history = model.fit(xvalues, yvalues, batch_size=batch_size, epochs=epochs, shuffle=False)

    # The list of epochs is stored separately from the rest of history.
    epochs = history.epoch

    # To track the progression of training, gather a snapshot
    # of the model's mean squared error at each epoch.
    hist = pd.DataFrame(history.history)

    loss = hist["loss"]
    return epochs, loss

def previousday(df):

    df['Temp']=df['Temp'].shift(periods=1,fill_value=0)
    return df

def nested_sum(lst):
    total = 0  # don't use `sum` as a variable name
    for i in lst:
        if isinstance(i, list):  # checks if `i` is a list
            total += nested_sum(i)
        else:
            total += i
    return total


def plot_actual_generation(ax, y_values, string):
    ax[0].plot(y_values, linewidth=0.5)
    ax[0].set_xlabel("Time")
    ax[0].set_ylabel(string)
    plt.show()

def plot_predicted_generation(ax,  yvalues, string):

    ax[1].plot( yvalues, linewidth=0.5)
    ax[1].set_xlabel("Time")
    ax[1].set_ylabel(string)
    plt.show()

def plot_error(ax, error, string):
    ax[2].plot( error, linewidth=0.5)
    ax[2].set_xlabel("Time")
    ax[2].set_ylabel(string)
    plt.show()

def plot_prediction_zoomed_in(yvalues1, yvalues2, yvalues3, string1, string2, string3):
    plt.figure(4)
    plt.xlabel("Time")
    plt.ylabel("Genration")
    plt.plot( yvalues1 , label=string1)
    plt.plot( yvalues2 , label=string2)
    plt.plot( yvalues3 , label=string3)
    plt.legend()
    plt.show()