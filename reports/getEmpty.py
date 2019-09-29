#!/usr/bin/env python
import pickle
import pandas as pd
#from copy import deepcopy

with open('neuro_selection.pkl', 'r') as fh:
    df = pickle.load(fh)

def getEmpty(df):
    df_empty = df
    for col in df_empty.columns[5:]:
        if ('___' in col): # if checkbox
            df_empty = df_empty.loc[(df_empty[col].isin(['NA', '', '0', 0])), :]
        else:
            df_empty = df_empty.loc[(df_empty[col].isin(['NA', ''])), :]
    return df_empty

print df
df_empty = getEmpty(df)
print df.loc[~df.index.isin(df_empty.index), :]
for col in df.columns:
    if (type(df.loc[2933, col]) != str):
        print col
        print type(df.loc[2933, col]) 

