import numpy as np
import matplotlib.pyplot as plt
from Load_Prediction.ANN.Functions_ANN import  train_model, create_model
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.ticker as plticker
import keras

########################################################################################################################
# Get data and data preprocessing.
########################################################################################################################

# Get the X (containing the features) and y (containing the labels) values
X = pd.read_csv('Data_Preprocessing/For_336_SP_Step_Prediction/X.csv', delimiter=',')
X = X.set_index("Time")
dates = X.iloc[:,-1]
X = X.iloc[:,:-6]

X = pd.DataFrame(X)
X = X.drop(["Transmission_Past"], axis = 1)
X = np.array(X)

y = pd.read_csv('Data_Preprocessing/For_336_SP_Step_Prediction/y.csv', delimiter=',')
y = y.set_index("Time")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0, shuffle = False)

# Save the unscaled data for later for data representation.
X_test_unscaled = X_test
X_train_unscaled = X_train

X_train = X_train[int(len(X_train)*1/2):]
X_test = X_test[:int(len(X_test)*1/2)]
y_train = y_train[int(len(y_train)*1/2):]
y_test = y_test[:int(len(y_test)*1/2)]
dates = dates[-len(X_test)-len(X_test)*2:-len(X_test)]

# Feature Scaling
x_scaler = StandardScaler()
y_scaler = StandardScaler()
X_train = x_scaler.fit_transform(X_train)
X_test = x_scaler.transform(X_test)
y_train = y_scaler.fit_transform(y_train)

########################################################################################################################
# Create the model without transmission as input feature.
########################################################################################################################

# Define the hyperparameters.
learning_rate = 0.001
number_of_epochs = 100
batch_size = 29

# Create the model.
my_model = create_model(len(X_train[1]), learning_rate)

# Extract the loss per epoch to plot the learning progress.
hist_list = pd.DataFrame()

tscv = TimeSeriesSplit()
for train_index, test_index in tscv.split(X_train):
      X_train_split, X_test_split = X_train[train_index], X_train[test_index]
      y_train_split, y_test_split = y_train[train_index], y_train[test_index]
      hist_split = train_model(my_model, X_train_split, y_train_split, number_of_epochs, batch_size)
      hist_list = hist_list.append(hist_split)

# Plot the loss per epoch.
metric = "mean_absolute_error"
x_axis = np.linspace(1,len(hist_list),len(hist_list))

fig, axs = plt.subplots(1, 1, figsize=(10, 6))
axs.plot(x_axis, hist_list['mean_absolute_error'], color = "blue")
axs.set_xlabel('Epoch')
axs.set_ylabel('Loss')
axs.legend(['Training set'])
axs.grid(True)
fig.show()

my_model.save("Load_Prediction/ANN/Feature_Analysis/Models/DMSP_ANN_model_No_Transmission.h5")

## The model is already trained and can be loaded with:
#my_model = keras.models.load_model("Load_Prediction/ANN/Feature_Analysis/Models/DMSP_ANN_model_No_Transmission.h5")

########################################################################################################################
# Predicting the generation.
########################################################################################################################

result_train = y_scaler.inverse_transform(my_model.predict(X_train))
result_test = y_scaler.inverse_transform(my_model.predict(X_test))

X_train = x_scaler.inverse_transform(X_train)
X_test = x_scaler.inverse_transform(X_test)
y_train = y_scaler.inverse_transform(y_train)

########################################################################################################################
# Data processing for plotting curves and printing the errors.
########################################################################################################################

# Compute the error between the Actual Generation and the prediction from the NN

print("-"*200)
error_train = (result_train - y_train)
print("The mean absolute error of the train set is %0.2f" % mean_absolute_error(y_train,result_train))
print("The mean squared error of the train set is %0.2f" % mean_squared_error(y_train,result_train))
print("The root mean squared error of the train set is %0.2f" % np.sqrt(mean_squared_error(y_train,result_train)))
print("-"*200)

error_test = (result_test - y_test)
print("The mean absolute error of the test set is %0.2f" % mean_absolute_error(y_test,result_test))
print("The mean squared error of the test set is %0.2f" % mean_squared_error(y_test,result_test))
print("The root mean squared error of the test set is %0.2f" % np.sqrt(mean_squared_error(y_test,result_test)))
print("-"*200)

########################################################################################################################
# Save the results in a csv file.
########################################################################################################################

import csv
with open('Load_Prediction/ANN/Feature_Analysis/Transmission_vs_No_Transmission/F6_(No_Transmission).csv', 'w', newline='',) as file:
    writer = csv.writer(file)
    writer.writerow(["Method","MSE","MAE","RMSE"])
    writer.writerow(["F6_(No_Transmission)",
                     str(mean_squared_error(y_test,result_test)),
                     str(mean_absolute_error(y_test,result_test)),
                     str(np.sqrt(mean_squared_error(y_test,result_test)))
                     ])

