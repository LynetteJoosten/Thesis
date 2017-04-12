import pandas as pd
import numpy as np
import glob
import os, zipfile
import matplotlib.pyplot as plt

#dir_name = 'C:\\SomeDirectory'
#extension = ".zip"

#os.chdir(dir_name) # change directory from working dir to dir with files

#for item in os.listdir(dir_name): # loop through items in dir
#    if item.endswith(extension): # check for ".zip" extension
#        file_name = os.path.abspath(item) # get full path of files
#        zip_ref = zipfile.ZipFile(file_name) # create zipfile object
#        zip_ref.extractall(dir_name) # extract file to dir
#        zip_ref.close() # close file
#        os.remove(file_name) # delete zipped file

#all_data = pd.DataFrame()
#for f in glob.glob("../in/sales*.xlsx"):
#    df = pd.read_csv(f)
#	 date_name = f[15:-4]
#	 df['Date'] = date_name
#    all_data = all_data.append(df,ignore_index=True)
#	 

#path = ' '                      # use your path
#all_files = glob.glob(os.path.join(path, "*.csv"))     # advisable to use os.path.join as this makes concatenation OS independent
#df_from_each_file = (pd.read_csv(f) for f in all_files)
#concatenated_df   = pd.concat(df_from_each_file, ignore_index=True)


data = pd.read_csv('data.csv', sep=';')
data['Price'] = data.Omzet / data.Verkocht

# Calculate the total return and amount of sold items
totalreturn = data['Omzet'].sum()
totalamount = data['Verkocht'].sum()

# Create a new column with the weight of the item for the total return and amount
data['wReturn'] = data['Omzet'] / totalreturn
data['wAmount'] = data['Verkocht'] / totalamount

# Get amount of weeks in data
periods = data['Week'].nunique() - 1
# Calculate change (percentage) of EAN for each branch for last period to period 1
data['Change'] = data.groupby(['Filiaal', 'EAN'])['Price'].pct_change(periods=periods)



'''
# Calculate change (percentage) of EAN over all branches
# data['Change'] = data.groupby(['EAN'])['Price'].pct_change()

# Get total change of an item by EAN
print(data.groupby(['Week', 'EAN'])['Change'].mean() + 100)

# Get total change for all seperate branches
print(data.groupby(['Week', 'Filiaal'])['Change'].mean() + 100)

# Get total change over all branches and EANs
totalchange = data.groupby(['Week'])['Change'].mean() + 100
totalchange.fillna(100, inplace=True)

totalchange.plot(kind='line')
plt.show()'''

data.to_csv('output.csv')
