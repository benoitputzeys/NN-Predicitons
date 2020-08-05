from sklearn.tree import DecisionTreeRegressor
import numpy as np
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import datetime
from pandas import DataFrame
import pickle

def create_dates(features_df, y_values):

    date_list = [datetime.datetime(year=int(features_df[i, -1]),
                                   month=int(features_df[i, -2]),
                                   day=int(features_df[i, -3]),
                                   hour=int((features_df[i, -4] - 1) / 2),
                                   minute=int(((round(features_df[i, -4])-1) % 2 ) * 30)) for i in range(len(features_df))]
    df_dates = DataFrame(date_list, columns=['Date'])
    df_dates = df_dates.set_index(['Date'])
    df_dates['Load'] = y_values

    return df_dates

########################################################################################################################
# Get data and data preprocessing.
########################################################################################################################

from numpy import genfromtxt

# Get the X (containing the features) and y (containing the labels) values
X = genfromtxt('Data_Entsoe/Data_Preprocessing/X.csv', delimiter=',')
y = genfromtxt('Data_Entsoe/Data_Preprocessing/y.csv', delimiter=',')
y = np.reshape(y, (len(y), 1))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0, shuffle = False)
# Save the unscaled data for later for data representation.
X_test_unscaled = X_test
X_train_unscaled = X_train

# Feature Scaling
x_scaler = StandardScaler()
y_scaler = StandardScaler()
X_train = x_scaler.fit_transform(X_train)
X_test = x_scaler.transform(X_test)
y_train = y_scaler.fit_transform(y_train)
y_test = y_scaler.transform(y_test)

########################################################################################################################
# Create the model.
########################################################################################################################

# Fit the Decision Tree to our data
regressor = DecisionTreeRegressor(random_state = 0)
regressor.fit(X_train, y_train)

filename = 'Electricity_Generation_Prediction/Decision_Tree/my_model.sav'
pickle.dump(regressor, open(filename, 'wb'))

result_test = y_scaler.inverse_transform(regressor.predict(X_test))
result_train = y_scaler.inverse_transform(regressor.predict(X_train))

result_test = result_test.reshape((len(result_test), 1))
result_train = result_train.reshape((len(result_train), 1))

########################################################################################################################
# Data processing for plotting curves and printing the errors.
########################################################################################################################

print("-"*200)
error_train = result_train - y_scaler.inverse_transform(y_train)
print("The mean absolute error of the training set is %0.2f" % mean_absolute_error(y_scaler.inverse_transform(y_train),result_train))
print("The mean squared error of the training set is %0.2f" % mean_squared_error(y_scaler.inverse_transform(y_train),result_train))
print("The root mean squared error of the training set is %0.2f" % np.sqrt(mean_squared_error(y_scaler.inverse_transform(y_train),result_train)))

print("-"*200)
error_test = result_test - y_scaler.inverse_transform(y_test)
print("The mean absolute error of the training set is %0.2f" % mean_absolute_error(y_scaler.inverse_transform(y_test),result_test))
print("The mean squared error of the training set is %0.2f" % mean_squared_error(y_scaler.inverse_transform(y_test),result_test))
print("The root mean squared error of the training set is %0.2f" % np.sqrt(mean_squared_error(y_scaler.inverse_transform(y_test),result_test)))
print("-"*200)

########################################################################################################################
# Visualising the results
########################################################################################################################

y_values_dates = create_dates(X, y)
figure1 = plt.figure(1)
plt.plot(y_values_dates, linewidth=0.5)
plt.title('Training + Test Set (Decision Tree)')
plt.xlabel('Settlement Period')
plt.ylabel('Actual Value (Training + Test Set)')
plt.show()

y_values_dates = create_dates(X_train_unscaled, X_train_unscaled[:,0])
fig2, ax2 = plt.subplots(3)
fig2.suptitle('Decision Tree: Training Set', fontsize=16)
ax2[0].plot(y_values_dates,linewidth=0.5)
ax2[0].set_xlabel('Settlement Period')
ax2[0].set_ylabel('Actual Value: Training Set')

y_values_dates = create_dates(X[:len(result_train)], result_train)
ax2[1].plot(y_values_dates, linewidth=0.5)
ax2[1].set_xlabel('Settlement Period')
ax2[1].set_ylabel('Prediction on training set')

y_values_dates = create_dates(X[:len(error_train)], abs(error_train))
ax2[2].plot(y_values_dates, linewidth=0.5)
ax2[2].set_xlabel('Settlement Period')
ax2[2].set_ylabel('Absolute error: Training set')
plt.show()

y_values_dates = create_dates(X_test_unscaled, X_test_unscaled[:,0])
fig3, ax3 = plt.subplots(3)
fig3.suptitle('Decision Tree: Testing Set', fontsize=16)
ax3[0].plot(y_values_dates, linewidth=0.5)
ax3[0].set_xlabel('Settlement Period')
ax3[0].set_ylabel('Actual Value: Test Set')

y_values_dates = create_dates(X_test_unscaled, result_test)
ax3[1].plot(y_values_dates,linewidth=0.5)
ax3[1].set_xlabel('Settlement Period')
ax3[1].set_ylabel('Prediction on test set')

y_values_dates = create_dates(X_test_unscaled, abs(error_test))
ax3[2].plot(y_values_dates, linewidth=0.5)
ax3[2].set_xlabel('Settlement Period')
ax3[2].set_ylabel('Absolute error: Test set.')
plt.show()

########################################################################################################################
# Save the results in a csv file.
########################################################################################################################

import csv
with open('Compare_Models/Single_Step_Results/Decision_Tree_result.csv', 'w', newline='', ) as file:
    writer = csv.writer(file)
    writer.writerow(["Method","MSE","MAE","RMSE"])
    writer.writerow(["Decision_Tree",
                     str(mean_squared_error(y_scaler.inverse_transform(y_test),result_test)),
                     str(mean_absolute_error(y_scaler.inverse_transform(y_test),result_test)),
                     str(np.sqrt(mean_squared_error(y_scaler.inverse_transform(y_test),result_test)))
                     ])