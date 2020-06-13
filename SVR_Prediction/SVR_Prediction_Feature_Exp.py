import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers
from matplotlib import pyplot as plt
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split


# Import the timeseries data
df = pd.read_csv("/Users/benoitputzeys/Desktop/Master Thesis/Data/SPI_2020/SPI_202005.csv")
#df = df.iloc[:500,:]
print(df.head())
df_label = df["Total_Generation"]
df_features = pd.DataFrame()
df_features["Total_Generation"] = df["Total_Generation"].shift(-2)
df_features["System_Buy_Price"] = df["System_Buy_Price"].shift(-2)
df_features["System_Total_Accepted_Bid_Volume"] = df["System_Total_Accepted_Bid_Volume"].shift(-2)
#df_features["Total_System_Accepted_Offer_Volume"] = df["Total_System_Accepted_Offer_Volume"].shift(-2)
df_features["Settlement_Period"] = df["Settlement_Period"]

# Create your input variable
x = df_features.values
y = df_label.values
y = np.reshape(y,(len(y),1))

# After having shifted the data, the nan values have to be replaces in order to have good predictions.
replace_nan = SimpleImputer(missing_values = np.nan, strategy='mean')
replace_nan.fit(x)
x = replace_nan.transform(x)

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 0, shuffle = False)
X_test_unscaled = X_test
X_train_unscaled = X_train


# Feature Scaling
x_scaler = StandardScaler()
y_scaler = StandardScaler()
X_train = x_scaler.fit_transform(X_train)
X_test = x_scaler.transform(X_test)
y_train = y_scaler.fit_transform(y_train)
y_test = y_scaler.transform(y_test)

# Fit the SVR to our data
regressor = SVR(kernel = 'rbf')
regressor.fit(X_train, y_train)

# Compute the prediction and rescale
intermediate_result_test_prediction = regressor.predict(X_test)
intermediate_result_train_prediction = regressor.predict(X_train)

#print(intermediate_result)
result_test = y_scaler.inverse_transform(intermediate_result_test_prediction)
result_train = y_scaler.inverse_transform(intermediate_result_train_prediction)

#print(result)
result_test = result_test.reshape((len(result_test), 1))
result_train = result_train.reshape((len(result_train), 1))

# Visualising the results
X_vals = []
for i in range(len(df)):
    X_vals = np.append(X_vals, i)
X_vals = np.reshape(X_vals,(len(X_vals),1))

figure1 = plt.figure(1)
plt.plot(X_vals, y, color = 'red')
plt.title('SVR')
plt.xlabel('Settlement Period')
plt.ylabel('Actual Value')

fig, ax = plt.subplots(3)

ax[0].plot(X_vals[:len(X_train)], X_train_unscaled[:,0], color = 'blue')
ax[0].set_xlabel('Settlement Period')
ax[0].set_ylabel('Actual Train')

ax[1].plot(X_vals[:len(result_train)], result_train, color = 'blue')
ax[1].set_xlabel('Settlement Period')
ax[1].set_ylabel('Train Prediction')

error_train = result_train - y_scaler.inverse_transform(y_train)
print("The mean absolute error of the training set is %0.2f" %np.mean(abs(error_train)))
print("The mean squarred error of the training set is %0.2f" %np.mean(error_train*error_train))

ax[2].plot(abs(error_train), color = 'blue')
ax[2].set_xlabel('Settlement Period')
ax[2].set_ylabel('Train Error')
plt.show()

fig2, ax2 = plt.subplots(3)

ax2[0].plot(X_vals[-len(X_test):], X_test_unscaled[:,0], color = 'blue')
ax2[0].set_xlabel('Settlement Period')
ax2[0].set_ylabel('Actual Test')

ax2[1].plot(X_vals[len(result_train):], result_test, color = 'blue')
ax2[1].set_xlabel('Settlement Period')
ax2[1].set_ylabel('Test Prediction')

error_test = result_test - y_scaler.inverse_transform(y_test)
print("The mean absolute error of the test set is %0.2f" %np.mean(abs(error_test)))
print("The mean squarred error of the test set is %0.2f" %np.mean(error_test*error_test))

ax2[2].plot(abs(error_test), color = 'blue')
ax2[2].set_xlabel('Settlement Period')
ax2[2].set_ylabel('Test Error')
plt.show()