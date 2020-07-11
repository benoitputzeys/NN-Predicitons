import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import datetime as dt

# This csv data has missing values for the last 152 days of the year as they lie in the future. (Get rid of them)
df = pd.read_csv("Data_Preprocessing/Load_GB_Processed_Data")
df = df.rename(columns={"Unnamed: 0": "Timestamp", "0": "Load"}, errors="raise")

df["Timestamp"] = [dt.datetime.strptime(df.iloc[i,0][0:16], '%Y-%m-%d %H:%M') for i in range(len(df))]

fig1, axs1=plt.subplots(1,1,figsize=(12,6))
axs1.plot(df.iloc[:,0], df.iloc[:,1])
axs1.set_ylabel("Load in UK [MW]")
axs1.set_xlabel("Date")
axs1.grid(True)
fig1.suptitle("Electricity Load in the UK from January 2016 to July 2020",fontsize=15)
fig1.show()

# Determine the Features.
df_features = pd.DataFrame()
df_features["Load_Past"] = df["Load"].shift(+48*7)

# Create artificial features.
rolling_mean_10 = df_features["Load_Past"].rolling(window=10).mean()
rolling_mean_50 = df_features["Load_Past"].rolling(window=50).mean()
exp_20 = df_features["Load_Past"].ewm(span=20, adjust=False).mean()
exp_50 = df_features["Load_Past"].ewm(span=50, adjust=False).mean()

df_features["Simple_Moving_Average_10_D"] = rolling_mean_10
df_features["Simple_Moving_Average_50_D"] = rolling_mean_50
df_features["Exp_Moving_Average_20_D"] = exp_20
df_features["Exp_Moving_Average_50_D"] = exp_50

# Create date relevant features.
df_features["Settlement Period"] = df['Timestamp'].dt.hour*2+1+df['Timestamp'].dt.minute/30
df_features["Day of Week"] = df['Timestamp'].dt.weekday
df_features['Day'] = df['Timestamp'].dt.day
df_features['Month'] = df['Timestamp'].dt.month
df_features['Year'] = df['Timestamp'].dt.year

df["Timestamp"]  = [pd.to_datetime(df.iloc[i,0]).strftime("%Y:%m:%d %H:%M") for i in range(len(df))]
df_features["Time_At_Delivery"] = df["Timestamp"]

X = df_features
# After having shifted the data, the nan values have to be replaced in order to have good predictions.
replace_nan = SimpleImputer(missing_values=np.nan, strategy='mean')
replace_nan.fit(X.iloc[:,:-1])
X.iloc[:,:-1] = replace_nan.transform(X.iloc[:,:-1])

y = df

X.to_csv("Data_Preprocessing/For_Multi_Step_Prediction/X.csv")
y.to_csv("Data_Preprocessing/For_Multi_Step_Prediction/y.csv")
#
# plt.plot(X[:,0], label='Electricity Generation 2 SP ago', linewidth=0.5 )
# plt.xlabel("Actual Settlement Period")
# plt.ylabel("Electricity Generation [MW]")
# #plt.plot(y[-48*3:,0], label='Total Generation Actual', linewidth=0.5 )
# plt.plot(X[:,1], label='10 Day MA', color='black' , linewidth=0.5 )
# #plt.plot(X[-48*3:,2], label='50 Day SMA', color='black',  linewidth=0.5 )
# #plt.plot(X[-48*3:,3], label='10 Day Exp MA', color='red',  linewidth=0.5 )
# #plt.plot(X[-48*3:,4], label='50 Day Exp MA', color='red',  linewidth=0.5 )
# #axs1.grid(True)
# plt.legend()
# plt.show()
