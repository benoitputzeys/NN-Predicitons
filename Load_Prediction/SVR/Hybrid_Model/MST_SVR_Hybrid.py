import numpy as np
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import datetime
from pandas import DataFrame
import pandas as pd
from sklearn.svm import SVR

def create_dates(features_df, y_values):

    date_list = [datetime.datetime(year=int(round(features_df[i, -1])),
                                   month=int(round(features_df[i, -2])),
                                   day=int(round(features_df[i, -3])),
                                   hour=int((round(features_df[i, -4])-1) / 2),
                                   minute=int(((round(features_df[i, -4])-1) % 2 ) * 30))  for i in range(len(features_df))]

    df_dates = DataFrame(date_list, columns=['Date'])
    df_dates = df_dates.set_index(['Date'])
    df_dates['Load'] = y_values

    return df_dates

########################################################################################################################
# Get data and data preprocessing.
########################################################################################################################

from numpy import genfromtxt

# Get the X (containing the features) and y (containing the labels) values
X = genfromtxt('Data_Entsoe/Data_Preprocessing/For_336_SP_Step_Prediction/X.csv', delimiter=',')
y = genfromtxt('Data_Entsoe/Data_Preprocessing/For_336_SP_Step_Prediction/y.csv', delimiter=',')
y = np.reshape(y, (len(y), 1))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0, shuffle = False)
X_train_1, X_train_2, y_train_1, y_train_2 = train_test_split(X_train, y_train, test_size = 0.2, random_state = 0, shuffle = False)
# Save the unscaled data for later for data representation.
X_test_unscaled = X_test
X_train_unscaled_1 = X_train_1

# Feature Scaling
x_scaler = StandardScaler()
y_scaler = StandardScaler()
X_train_1 = x_scaler.fit_transform(X_train_1)
X_train_2 = x_scaler.transform(X_train_2)
X_test = x_scaler.transform(X_test)
y_train_1 = y_scaler.fit_transform(y_train_1)

########################################################################################################################
# Create the model.
########################################################################################################################

# Fit the SVR to our data
regressor = SVR(kernel = 'rbf')
regressor.fit(X_train_1, y_train_1)

result_train_1 = y_scaler.inverse_transform(regressor.predict(X_train_1))
result_train_2 = y_scaler.inverse_transform(regressor.predict(X_train_2))
result_test = y_scaler.inverse_transform(regressor.predict(X_test))

X_train_1 = x_scaler.inverse_transform(X_train_1)
X_train_2 = x_scaler.inverse_transform(X_train_2)
X_test = x_scaler.inverse_transform(X_test)
y_train_1 = y_scaler.inverse_transform(y_train_1)

result_train_1 = result_train_1.reshape((len(result_train_1), 1))
result_train_2 = result_train_2.reshape((len(result_train_2), 1))
result_test = result_test.reshape((len(result_test), 1))

########################################################################################################################
# Data processing for plotting curves and printing the errors.
########################################################################################################################

print("-"*200)
error_train_1 = result_train_1 - y_train_1
print("The mean absolute error of the training set 1 is %0.2f" % mean_absolute_error(y_train_1,result_train_1))
print("The mean squared error of the training set 1 is %0.2f" % mean_squared_error(y_train_1,result_train_1))
print("The root mean squared error of the training set 1 is %0.2f" % np.sqrt(mean_squared_error(y_train_1,result_train_1)))

print("-"*200)
error_train_2 = result_train_2 - y_train_2
print("The mean absolute error of the training set 2 is %0.2f" % mean_absolute_error(y_train_2,result_train_2))
print("The mean squared error of the training set 2 is %0.2f" % mean_squared_error(y_train_2,result_train_2))
print("The root mean squared error of the training 2 set is %0.2f" % np.sqrt(mean_squared_error(y_train_2,result_train_2)))

print("-"*200)
error_test = result_test - y_test
print("The mean absolute error of the test set  is %0.2f" % mean_absolute_error(y_test,result_test))
print("The mean squared error of the test set is %0.2f" % mean_squared_error(y_test,result_test))
print("The root mean squared error of the test set is %0.2f" % np.sqrt(mean_squared_error(y_test,result_test)))
print("-"*200)

########################################################################################################################
# Visualising the results
########################################################################################################################

# y_values_dates = create_dates(X, y)
# figure1 = plt.figure(1)
# plt.plot(y_values_dates, linewidth=0.5)
# plt.title('Training + Test Set (SVR)')
# plt.xlabel('Settlement Period')
# plt.ylabel('Actual Value (Training + Test Set)')

y_values_dates = create_dates(X_train_unscaled_1, X_train_unscaled_1[:,0])
fig1, ax1 = plt.subplots(3)
fig1.suptitle('SVR: Training Set 1', fontsize=16)
ax1[0].plot(y_values_dates,linewidth=0.5)
ax1[0].set_xlabel('Settlement Period')
ax1[0].set_ylabel('Actual Value: Training Set 1')

y_values_dates = create_dates(X[:len(result_train_1)], result_train_1)
ax1[1].plot(y_values_dates, linewidth=0.5)
ax1[1].set_xlabel('Settlement Period')
ax1[1].set_ylabel('Prediction on Training Set 1')

y_values_dates = create_dates(X[:len(error_train_1)], abs(error_train_1))
ax1[2].plot(y_values_dates, linewidth=0.5)
ax1[2].set_xlabel('Settlement Period')
ax1[2].set_ylabel('Absolute error: Training set 2')
plt.show()

y_values_dates = create_dates(X[len(X_train_1):(len(X_train_1)+len(X_train_2))], X_train_2[:,0])
fig2, ax2 = plt.subplots(3)
fig2.suptitle('SVR: Training Set 2', fontsize=16)
ax2[0].plot(y_values_dates, linewidth=0.5)
ax2[0].set_xlabel('Settlement Period')
ax2[0].set_ylabel('Actual Value: Training Set 2')

y_values_dates = create_dates(X[len(X_train_1):(len(X_train_1)+len(X_train_2))], result_train_2)
ax2[1].plot(y_values_dates,linewidth=0.5)
ax2[1].set_xlabel('Settlement Period')
ax2[1].set_ylabel('Prediction on Training Set 2')

y_values_dates = create_dates(X[len(X_train_1):(len(X_train_1)+len(X_train_2))], abs(error_train_2))
ax2[2].plot(y_values_dates, linewidth=0.5)
ax2[2].set_xlabel('Settlement Period')
ax2[2].set_ylabel('Absolute error: Training Set 2')
plt.show()

# Print the prediction of the training set 1.
y_values_dates = create_dates(X_train_1[-48*7:],result_train_1[-48*7:])
fig3, axes3 = plt.subplots(2)
axes3[0].plot(y_values_dates, label = "Prediction")
y_values_dates = create_dates(X_train_1[-48*7:],y_train_1[-48*7:])
axes3[0].plot(y_values_dates, label = "Actual")
axes3[0].set_xlabel("Settlement Periods Training Set 1")
axes3[0].set_ylabel("Electricity Load [MW]")
axes3[0].legend()

y_values_dates = create_dates(X_train_1[-48*7:],abs(result_train_1[-48*7:]-y_train_1[-48*7:]))
axes3[1].plot(y_values_dates, label = "Error")
axes3[1].set_xlabel("Settlement Periods Training Set 1")
axes3[1].set_ylabel("Electricity Load [MW]")
axes3[1].legend()

# Print the prediction of the training set 2.
fig4, axes4 = plt.subplots(2)
y_values_dates = create_dates(X_train_2[-48*7-1:],result_train_2[-48*7-1:])
axes4[0].plot(y_values_dates, label = "Prediction")
y_values_dates = create_dates(X_train_2[-48*7-1:],y_train_2[-48*7-1:])
axes4[0].plot(y_values_dates, label = "Actual")
axes4[0].set_xlabel("Settlement Periods Training Set 2")
axes4[0].set_ylabel("Electricity Load [MW]")
axes4[0].legend()

y_values_dates = create_dates(X_train_2[-48*7-1:],abs(result_train_2[-48*7-1:]-(y_train_2[-48*7-1:])))
axes4[1].plot(y_values_dates, label = "Error")
axes4[1].set_xlabel("Settlement Periods Training Set 2")
axes4[1].set_ylabel("Electricity Load [MW]")
axes4[1].legend()

# Print the prediction of the test set.
fig5, axes5 = plt.subplots(2)
y_values_dates = create_dates(X_test[-48*7:],result_test[-48*7:])
axes5[0].plot(y_values_dates, label = "Prediction")
y_values_dates = create_dates(X_test[-48*7:],y_test[-48*7:])
axes5[0].plot(y_values_dates, label = "Actual")
axes5[0].set_xlabel("Settlement Periods Test Set")
axes5[0].set_ylabel("Electricity Load [MW]")
axes5[0].legend()

y_values_dates = create_dates(X_test[-48*7:],abs(result_test[-48*7:]-(y_test[-48*7:])))
axes5[1].plot(y_values_dates, label = "Error")
axes5[1].set_xlabel("Settlement Periods Test Set")
axes5[1].set_ylabel("Error in [MW]")
axes5[1].legend()

########################################################################################################################
# Save the results in a csv file.
########################################################################################################################

pd.DataFrame(result_train_2).to_csv("Load_Prediction/Hybrid_Model/Pred_train2_other_metrics/SVR_prediction.csv")
pd.DataFrame(result_test).to_csv("Load_Prediction/Hybrid_Model/Pred_test_other_metrics/SVR_prediction.csv")

import csv
with open('Compare_Models/MST2_results/SVR_result.csv', 'w', newline='',) as file:
    writer = csv.writer(file)
    writer.writerow(["Method","MSE","MAE","RMSE"])
    writer.writerow(["SVR",
                     str(mean_squared_error(y_test,result_test)),
                     str(mean_absolute_error(y_test,result_test)),
                     str(np.sqrt(mean_squared_error(y_test,result_test)))
                     ])