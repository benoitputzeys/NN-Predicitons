import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from Load_Prediction.LSTM.Functions_LSTM import  train_model, create_model
from sklearn.preprocessing import StandardScaler
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.ticker as plticker
import keras

########################################################################################################################
# Get data and data preprocessing.
########################################################################################################################

# Get the X (containing the features) and y (containing the labels) values
X = pd.read_csv('Data_Preprocessing/For_1_SP_Step_Prediction/X.csv', delimiter=',')
X = X.set_index("Time")
dates = X.iloc[:,-1]
X = X.iloc[:,:-5]
y = pd.read_csv('Data_Preprocessing/For_1_SP_Step_Prediction/y.csv', delimiter=',')
y = y.set_index("Time")

# Partition the data into 80% training data and 20% test data.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0, shuffle = False)

# Only take half the training set according to the findings from the thesis.
X_train = X_train[int(len(X_train)*1/2):]
X_test = X_test[:int(len(X_test)*1/2)]
y_train = y_train[int(len(y_train)*1/2):]
y_test = y_test[:int(len(y_test)*1/2)]
dates = dates[-len(X_train)-len(X_test)*2:-len(X_test)]

# Feature Scaling
x_scaler = StandardScaler()
y_scaler = StandardScaler()
X_train = x_scaler.fit_transform(X_train)
X_test = x_scaler.transform(X_test)
y_train = y_scaler.fit_transform(y_train)

########################################################################################################################
# Create the model.
########################################################################################################################

# Define the hyperparameters.
learning_rate = 0.005
number_of_epochs = 40
batch_size = 19

# Create the model.
my_model = create_model(X_train, learning_rate)

# Create a dataframe to extract the loss per epoch to plot the learning progress.
hist_list = pd.DataFrame()

# Perform 5-fold cross validation
tscv = TimeSeriesSplit()
for train_index, test_index in tscv.split(X_train):
     X_train_split, X_test_split = X_train[train_index], X_train[test_index]
     y_train_split, y_test_split = y_train[train_index], y_train[test_index]
     X_train_split = np.reshape(X_train_split, (X_train_split.shape[0],X_train_split.shape[1],1))
     hist_split = train_model(my_model, X_train_split, y_train_split, number_of_epochs, batch_size)
     hist_list = hist_list.append(hist_split)


# Plot the loss during training.
x_axis = np.linspace(1,len(hist_list),len(hist_list))
fig, axs = plt.subplots(1, 1, figsize=(10, 6))
axs.plot(x_axis, hist_list['mean_absolute_error'], color = "blue")
axs.set_xlabel('Epoch')
axs.set_ylabel('Loss')
axs.grid(True)
fig.show()

# Save or load the model.
my_model.save("Load_Prediction/LSTM/Single_Step_Prediction/Single_Step_LSTM_Model.h5")
#my_model = keras.models.load_model("SST_No_Trans_No_Date.h5")

########################################################################################################################
# Predicting the load and divide by 1000 to express everything in GW.
########################################################################################################################

pred_train = y_scaler.inverse_transform(my_model.predict(np.reshape(X_train, (X_train.shape[0],X_train.shape[1],1))))/1000
pred_train = pred_train.reshape(-1,)
pred_test = y_scaler.inverse_transform(my_model.predict(np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))))/1000
pred_test = pred_test.reshape(-1,)

X_train = x_scaler.inverse_transform(X_train)
X_test = x_scaler.inverse_transform(X_test)
y_train = (y_scaler.inverse_transform(y_train)/1000).reshape(-1,)
y_test = np.array(y_test.iloc[:,-1]/1000).reshape(-1,)

########################################################################################################################
# Data processing for plotting curves and printing the errors.
########################################################################################################################

# Compute the error between the actual load and the prediction from the LSTM
print("-"*200)
error_train = pred_train - y_train
print("The mean absolute error of the train set is %0.2f" % mean_absolute_error(y_train,pred_train))
print("The mean squared error of the train set is %0.2f" % mean_squared_error(y_train,pred_train))
print("The root mean squared error of the train set is %0.2f" % np.sqrt(mean_squared_error(y_train,pred_train)))
print("-"*200)

error_test = pred_test - y_test
print("The mean absolute error of the test set is %0.2f" % mean_absolute_error(y_test,pred_test))
print("The mean squared error of the test set is %0.2f" % mean_squared_error(y_test,pred_test))
print("The root mean squared error of the test set is %0.2f" % np.sqrt(mean_squared_error(y_test,pred_test)))
print("-"*200)

########################################################################################################################
# Plotting curves.
########################################################################################################################

# Create a vector that contains the error between the prediction and the test set values.
error_test_plot = np.zeros((48*3+48*7,1))
error_test_plot[-336:] = error_test[:48*7].reshape(-1,1)

# Plot the result with the training values in blue and the test values in black and the predictions in orange.
fig2, axs2=plt.subplots(2,1,figsize=(12,6))
axs2[0].plot(dates.iloc[-len(X_test)-48*3:-len(X_test)],
             y_train[-48*3:],
             label = "Training Set", alpha = 1, color = "blue")
axs2[0].plot(dates.iloc[-len(X_test):-len(X_test)+48*7],
             pred_test[:48*7],
             label = "LSTM Prediction", color = "orange")
axs2[0].plot(dates.iloc[-len(X_test):-len(X_test)+48*7],
             y_test[:48*7],
             label = "Test Set", alpha = 1, color = "black")
axs2[0].axvline(dates.iloc[-len(X_test)], linestyle="--", color = "black")
axs2[0].set_ylabel('Load, GW',size = 14)
axs2[0].plot(30,30,label = "Error", color = "red")

axs2[1].plot(dates.iloc[-len(X_test)-48*3:-len(X_test)+48*7],
             error_test_plot,
             label = "Error", alpha = 1, color = "red")
axs2[1].axvline(dates.iloc[-len(X_test)], linestyle="--", color = "black")
axs2[1].set_xlabel('Date',size = 14)
axs2[1].set_ylabel('Error, GW',size = 14)

# Include additional details such as tick intervals, rotation, legend positioning and grid on.
axs2[1].grid(True), axs2[0].grid(True)
loc = plticker.MultipleLocator(base=47) # Put ticks at regular intervals
axs2[0].xaxis.set_major_locator(loc), axs2[1].xaxis.set_major_locator(loc)
axs2[0].legend()
fig2.autofmt_xdate(rotation=0)
plt.xticks(np.arange(1,482, 48), ["14:00\n07/22","14:00\n07/23","14:00\n07/24",
                                  "14:00\n07/25","14:00\n07/26","14:00\n07/27",
                                  "14:00\n07/28","14:00\n07/29","14:00\n07/30",
                                  "14:00\n07/31","14:00\n08/01"])
axs2[0].legend(loc=(1.02,0.6))

fig2.show()

########################################################################################################################
# Save the results in a csv file.
########################################################################################################################

df_errors = pd.DataFrame({"MSE_Train": [mean_squared_error(y_train,pred_train)],
                          "MAE_Train": [mean_absolute_error(y_train,pred_train)],
                          "RMSE_Train": [np.sqrt(mean_squared_error(y_train,pred_train))],
                          "MSE_Test": [mean_squared_error(y_test, pred_test)],
                          "MAE_Test": [mean_absolute_error(y_test, pred_test)],
                          "RMSE_Test": [np.sqrt(mean_squared_error(y_test, pred_test))],
                          })

df_errors.to_csv("Compare_Models/Single_Step_Results/LSTM_result.csv")
