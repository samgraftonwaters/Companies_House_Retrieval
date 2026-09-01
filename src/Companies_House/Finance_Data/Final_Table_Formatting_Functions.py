import pandas as pd
import numpy as np
import re
import time

def updating_missing_columns(df):

    df = df.copy()
    time_period = ['Current', 'Previous']

    for time in time_period:
    
        df[f'FixedAssets_{time}'] = np.where(df[f'FixedAssets_{time}'].isna() == True, 
                                                                df[f'PropertyPlantEquipment_{time}'], 
                                                                df[f'FixedAssets_{time}'])

        inventory = df[f'TotalInventories_{time}'].fillna(0) if f'TotalInventories_{time}' in df.columns else 0
        debtors = df[f'Debtors_{time}'].fillna(0) if f'Debtors_{time}' in df.columns else 0
        cash_bank = df[f'CashBankOnHand_{time}'].fillna(0) if f'CashBankOnHand_{time}' in df.columns else 0
        
        df[f'CurrentAssets_{time}'] = np.where(df[f'CurrentAssets_{time}'].isna() == True, 
                                                   (cash_bank + inventory + debtors), 
                                                   df[f'CurrentAssets_{time}'])
        
        df[f'Equity_TotalEquity_{time}'] = np.where(df[f'Equity_TotalEquity_{time}'].isna() == True,
                                                    df[f'NetAssetsLiabilities_{time}'],
                                                    df[f'Equity_TotalEquity_{time}'])                  

        df[f'CurrentAssets_{time}'] = df[f'CurrentAssets_{time}'].astype('Int64')
    
        df = df.drop([f'TotalInventories_{time}', f'Equity_Other_{time}', f'Equity_RevaluationReserve_{time}', f'Equity_RetainedEarnings_{time}',
                      f'Equity_ShareCapital_Current_{time}', f'PropertyPlantEquipment_{time}'], 
                     axis = 1,  errors='ignore')

    return(df)


def correct_number_employers(df):

    df = df.copy()
    
    time_period = ['Current', 'Previous']
    
    for time in time_period: #isinstance(, float)

        df[f'AverageNumberEmployeesDuringPeriod_{time}'] = np.where(df[f'AverageNumberEmployeesDuringPeriod_{time}']% 1 != 0, 
                                                                    df[f'AverageNumberEmployeesDuringPeriod_{time}'] * 100,
                                                                    df[f'AverageNumberEmployeesDuringPeriod_{time}'])

        df[f'AverageNumberEmployeesDuringPeriod_{time}'] = np.where(df[f'AverageNumberEmployeesDuringPeriod_{time}'] > 10000, 
                                                                    df[f'AverageNumberEmployeesDuringPeriod_{time}'] / 1000,
                                                                    df[f'AverageNumberEmployeesDuringPeriod_{time}'])
    return(df)


def change_data_types(df, columns_to_change : list | str, to_type : str, date_first : str = None):

    columns_to_change = [col for col in columns_to_change if col in df.columns]
    
    if to_type == 'int':
        df[columns_to_change] = df[columns_to_change].replace(',', '', regex=True).apply(pd.to_numeric, errors='coerce').round().astype('Int64')
        return(df)
    if to_type == 'float':
        df[columns_to_change] = df[columns_to_change].replace(',', '', regex=True).apply(pd.to_numeric, errors='coerce').astype(float)
        return(df)
    if to_type == 'date':
        if date_first == 'day':
            df[columns_to_change] = df[columns_to_change].apply(pd.to_datetime, errors='coerce', dayfirst=True)
            return(df)
        if date_first == 'year':
            df[columns_to_change] = df[columns_to_change].apply(pd.to_datetime, errors='coerce', yearfirst=True)
            return(df)