import pandas as pd
import numpy as np
import glob
import os, zipfile
import matplotlib.pyplot as plt
import datetime
import pickle


# In[ ]:

''''dir_name = 'C:/Users/laptop/Documents/Data/2016'
extension = ".zip"

os.chdir(dir_name) # change directory from working dir to dir with files

for item in os.listdir(dir_name): # loop through items in dir
    if item.endswith(extension): # check for ".zip" extension
        file_name = os.path.abspath(item) # get full path of files
        zip_ref = zipfile.ZipFile(file_name) # create zipfile object
        zip_ref.extractall(dir_name) # extract file to dir
        zip_ref.close() # close file
        os.remove(file_name) # delete zipped file''''


# In[42]:

tdf = pd.DataFrame()
for x in glob.glob("C:/Users/laptop/Documents/Data/all/cbs_ah_product_referentie*.txt"):
    for y in glob.glob("C:/Users/laptop/Documents/Data/all/cbs_ah_regulier*.txt"):
        if x[-8:-4] == y[-8:-4]:
            i =  pd.read_table(x, sep = ';', encoding='latin-1', header=None)
            j = pd.read_table(y, sep = ';', encoding='latin-1', header=None)
            j['Date'] =  datetime.datetime.strptime(y[-10:-4], "%y%m%d")
            m = pd.merge(j, i, how='left', left_on=4, right_on=0, left_index=False, right_index=False)
            tdf = tdf.append(m, ignore_index=True)

tdf.columns = ['EAN', 'Week', 'Year', 'Storecode', 'Storekind', 'EAN2', 'Sale', 'Turnover', 'Amount', 'Empty', 'Date', 'EAN3', 'ID', 'Description', 'Contentamount', 'Contentsort', 'Group1', 'Description1', 'Group2', 'Description2', 'Group3', 'Description3', 'Group4', 'Description4']
tdf.Turnover = tdf.Turnover / 100
tdf['Price'] = tdf.Turnover / tdf.Amount
totalreturn = tdf.Turnover.sum()
totalamount = tdf.Amount.sum()

tdf['wReturn'] = tdf['Turnover'] / totalreturn
tdf['wAmount'] = tdf['Amount'] / totalamount
tdf['Quarter'] = tdf['Date'].dt.quarter
tdf['Month'] = tdf['Date'].dt.month

#Select only rows where product is not on sale.
tdfs = tdf[tdf.Sale != 'J']
#tdfs = tdfs[(tdfs.Storecode == 4) | (tdfs.Storecode == 5)]
tdfs = tdfs.drop(['EAN2', 'EAN3', 'Storekind', 'Sale', 'Contentamount', 'Contentsort'], axis=1)

tdf.to_pickle('tdf.pickle')
tdfs.to_pickle('tdfs.pickle')
# In[17]:

tdf = pd.read_pickle('tdf.pickle')
tdfs = pd.read_pickle('tdfs.pickle')


def createdataframe(groupA, groupB, groupC): 
    df = pd.DataFrame()
    df['AvgPrice']= tdfs.groupby([groupA, groupB, groupC])['Price'].mean()
    df = df.reset_index()
    df['Change'] = df.groupby([groupA])['AvgPrice'].pct_change()
    df = df.replace([np.inf, -np.inf], np.nan)
    return df;

EW = createdataframe('EAN', 'Year', 'Week')
EM = createdataframe('EAN', 'Year', 'Month')
EQ = createdataframe('EAN', 'Year', 'Quarter')

# In[24]:

def createdataframey(groupA, groupB): 
    df = pd.DataFrame()
    df['AvgPrice']= tdfs.groupby([groupA, groupB])['Price'].mean()
    df = df.reset_index()
    df['Change'] = df.groupby([groupA])['AvgPrice'].pct_change()
    df = df.replace([np.inf, -np.inf], np.nan)
    return df;

EY = createdataframey('EAN', 'Year')
# In[26]:

def change(df, groupB, groupC):
    dfchange = df.groupby([groupB, groupC])['Change'].mean() * 100 + 100
    dfchange.fillna(100, inplace=True)
    return dfchange;
  
EWchange = change(EW, 'Year', 'Week')
EMchange = change(EM, 'Year', 'Month')
EQchange = change(EQ, 'Year', 'Quarter')

# In[28]:

def changey(df, groupB):
    dfchange = df.groupby(groupB)['Change'].mean() * 100 + 100
    dfchange.fillna(100, inplace=True)
    return dfchange;

EYchange = changey(EY, 'Year')


# In[30]:

def pickles(df, path):
    df.to_pickle(path)
    return;
  
pickles(EW, 'EW')
pickles(EM, 'EM')
pickles(EQ, 'EQ')
pickles(EY, 'EY')
pickles(EWchange, "EWchange")
pickles(EMchange, "EMchange")
pickles(EQchange, "EQchange")
pickles(EYchange, "EYchange")

EWchange = pd.read_pickle("EWchange")
EMchange = pd.read_pickle("EMchange")
EQchange = pd.read_pickle("EQchange")
EYchange = pd.read_pickle("EYchange")
EW = pd.read_pickle('EW')
EM = pd.read_pickle('EM')
EQ = pd.read_pickle('EQ')
EY = pd.read_pickle('EY')


# In[14]:

def createplot(df,filename):
    plot1 = df.plot()
    fig = plot1.get_figure()
    fig.savefig(filename+'.png')
    plt.close("all")


# In[16]:

createplot(EWchange, 'EW')
createplot(EMchange, 'EM')
createplot(EQchange, 'EQ')


# In[34]:

def basechange(df, groupA, groupB, groupC):
    df = df.groupby([groupA, groupB, groupC])['AvgPrice'].mean()
    df = df.reset_index()
    df = df.groupby([groupB, groupC])['AvgPrice'].mean()
    df = df.reset_index() 
    for index, row in df.iterrows():
        df.loc[index,'Change'] = (row.AvgPrice - df.AvgPrice.iloc[0])/row.AvgPrice
    df['Change2'] = df['Change'] * 100 + 100
    df = df.drop(['AvgPrice', 'Change'], axis=1)
    df['Week-year'] = df[groupC].astype(str) +'-' + df[groupB].astype(str)
    df.columns = ['Year', 'Week', 'Change', 'Week-year']
    return df;


# In[38]:

def basechangey(df, groupA, groupB):
    df = df.groupby([groupA, groupB])['AvgPrice'].mean()
    df = df.reset_index()
    df = df.groupby([groupB])['AvgPrice'].mean()
    df = df.reset_index() 
    for index, row in df.iterrows():
        df.loc[index,'Change'] = (row.AvgPrice - df.AvgPrice.iloc[0])/row.AvgPrice
    df['Change2'] = df['Change'] * 100 + 100
    df = df.drop(['AvgPrice', 'Change'], axis=1)
    #df['Week-year'] = df[groupC].astype(str) +'-' + df[groupB].astype(str)
    df.columns = ['Year', 'Change']
    return df;


# In[39]:

EWbasechange = basechange(EW, 'EAN', 'Year', 'Week')
EMbasechange = basechange(EM, 'EAN', 'Year', 'Month')
EQbasechange = basechange(EQ, 'EAN', 'Year', 'Quarter')
EYbasechange = basechangey(EY, 'EAN', 'Year')


# In[29]:

def createbaseplot(df,filename):
    plot1 = df.plot(y='Change', x='Week-year')
    fig = plot1.get_figure()
    fig.savefig(filename+'.png')
    plt.close("all")


# In[54]:

def createbaseploty(df,filename):
    plot1 = df.plot(y='Change', x='Year', kind ='scatter', xticks=range(2))
    
    fig = plot1.get_figure()
    fig.savefig(filename+'.png')
    plt.close("all")


# In[43]:

createbaseplot(EWbasechange, 'EWb')
createbaseplot(EMbasechange, 'EMb')
createbaseplot(EQbasechange, 'EQb')
