import pandas as pd
import numpy as np
from datetime import datetime

def updating_missing_columns(df):

    """
    In some cases, certain columns may be missing data, but they are either stored in another column with a different name 
    to what is usually present, or other columns need to be summed to get the desired value. This function
    accounts for these.

    Parameters:
    -----------
        df (DataFrame): Financial dataframe

    Returns:
    --------
        DataFrame with corrected and updated columns

    """

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

    """
    In some cases, the number of employess at a Company is returns as a decimal. e.g. 0.45, this function converts
    this value to an integer (e.g. 45). Alternatively, some employee numbers are in the millions, but the true value maybe 
    in the 100s or 1000s. The function accounts for those as well

    Parameters:
    -----------
        df (DataFrame): Financial dataframe
    
    Returns:
    --------
        DataFrame with the correct Company employee numbers
    """

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

    """
    Changes the column to their correct type - e.g. date, int or float

    Parameters:
    -----------
        df (DataFrame): Financial dataframe
        columns_to_change (list | str): column names to change the type on. Columns added here must only be included
                                        if they should all have the final type change
        to_type (str): what type should the column(s) be changed to? Options: 'float', 'date' or 'int'
        date_first (str): if date is the desired type, then this sets the 'day' or 'year' first depending on
                            input. Default = None

    Returns:
    --------
        Changes the types of specified columns in the datatable.
    """

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


def update_columns_if_similar_values(df):

    """
    In some cases, data is saved in a column with a different name. This function takes this column and fills in 
    the correct column with its information.

    Parameters:
    ----------
        df (DataFrame): Financial dataframe
    
    Returns:
    --------
        DataFrame with all columns filled in correctly if there is data.
    
    """

    df[f'Equity_ShareCapital_Previous'] = np.where(df[f'Equity_ShareCapital_Previous'].isna() == True, 
                                                            df[f'Equity_ShareCapital_Current'], 
                                                            df[f'Equity_ShareCapital_Previous'])

    df['UKCompaniesHouseRegisteredNumber_Current'] = np.where(df['UKCompaniesHouseRegisteredNumber_Current'].isna() == True, 
                                                                        df['Company_Number'],
                                                                        df['UKCompaniesHouseRegisteredNumber_Current'])
    df = df.drop('Company_Number', axis = 1)

    return(df) 


def reoreder_rename_cols(df):

    """
    Renames the columns and reorders them

    Parameters:
    ----------
        df (DataFrame): Financial dataframe
    
    Returns:
    --------
        DataFrame with renamed and reordered columns
    
    """

    reorder_cols = ['UKCompaniesHouseRegisteredNumber_Current', 'Account_Date', 'Action_Date',  
                    'StartDateForPeriodCoveredByReport_Current', 'EndDateForPeriodCoveredByReport_Current', 'BalanceSheetDate_Current', 
                    'AverageNumberEmployeesDuringPeriod_Current', 'AverageNumberEmployeesDuringPeriod_Previous', 'FixedAssets_Current', 
                    'FixedAssets_Previous', 'CurrentAssets_Current', 'CurrentAssets_Previous', 'CashBankOnHand_Current', 'CashBankOnHand_Previous', 
                    'Creditors_Within1Y_Current', 'Creditors_Within1Y_Previous', 'Creditors_After1Y_Current', 'Creditors_After1Y_Previous',
                    'Debtors_Current', 'Debtors_Previous', 'Equity_TotalEquity_Current', 
                    'Equity_TotalEquity_Previous', 'NetAssetsLiabilities_Current', 'NetAssetsLiabilities_Previous', 'NetCurrentAssetsLiabilities_Current', 
                    'NetCurrentAssetsLiabilities_Previous', 'TotalAssetsLessCurrentLiabilities_Current', 'TotalAssetsLessCurrentLiabilities_Previous']

    df = df.loc[:, reorder_cols]

    rename_cols = ['Companies House Number', 'Account Date', 'Action Date', 'Period Start Date', 'Period End Date', 
                'Balance Sheet Date', 'Average Number Employees Current', 'Average Number Employees Previous', 'Fixed Assets Current', 
                'Fixed Assets Previous', 'Current Assets Current', 'Current Assets Previous', 'Cash Bank On Hand Current', 'Cash Bank On Hand Previous', 
                'Creditors Within 1Y Current', 'Creditors Within 1Y Previous', 'Creditors After 1Y Current', 'Creditors After 1Y Previous',  
                'Debtors Current', 'Debtors Previous', 'Total Equity Current', 'Total Equity Previous', 'Net Assets Current', 
                'Net Assets Previous', 'Net Current Assets Current', 'NetCurrent Assets Previous', 
                'Total Assets Less Liabilities Current', 'Total Assets Less Liabilities Previous']

    df.columns = rename_cols

    return(df)

def create_new_cols(df):

    """
    Creates new columns in the finance data table. 

    Parameters:
    -----------
        df (DataFrame): datatable with the financial data.

    Returns:
    --------
        dataframe with new columns for the financial data.

    """
    df['Total Assets Current'] = (np.where(df['Fixed Assets Current'].isna() == False, df['Fixed Assets Current'], 0)
                                            + np.where(df['Current Assets Current'].isna() == False, df['Current Assets Current'], 0))
    df['Total Assets Previous'] = (np.where(df['Fixed Assets Previous'] .isna() == False, df['Fixed Assets Previous'], 0)
                                            + np.where(df['Current Assets Previous'].isna() == False, df['Current Assets Previous'], 0))

    df["Period Current Year"] = np.where(df["Period End Date"].isna() == False, df["Period End Date"].dt.year,
                                                df["Action Date"].dt.year)
    df["Period Previous Year"] = np.where(df["Period End Date"].isna() == False, df["Period End Date"].dt.year - 1,
                                                    df["Action Date"].dt.year - 1)

    return(df)


def final_table_formatting(dataframe, save_file = False):

    """
    Updates and reformats the financial data table to get the final table to be saved.

    Parameters:
    -----------
        dataframe (DataFrame): the datatable with the financial data ready to be reformatted
        save_file (bool): determines whther the table should be saved. Default = False
    
    Returns:
    --------
        Final formatted financial data table. 
    
    """

    int_cols = ['FixedAssets_Current', 'FixedAssets_Previous',
                'CurrentAssets_Current', 'CurrentAssets_Previous', 'CashBankOnHand_Current', 'CashBankOnHand_Previous', 'Creditors_Within1Y_Current',
                'Creditors_Within1Y_Previous', 'Creditors_After1Y_Current', 'Creditors_After1Y_Previous', 'Debtors_Current', 'Debtors_Previous',
                'Equity_TotalEquity_Current', 'Equity_TotalEquity_Previous',  'NetAssetsLiabilities_Current', 'NetAssetsLiabilities_Previous',
                'NetCurrentAssetsLiabilities_Current', 'NetCurrentAssetsLiabilities_Previous', 'TotalAssetsLessCurrentLiabilities_Current', 
                'TotalAssetsLessCurrentLiabilities_Previous', 'TotalInventories_Current', 'TotalInventories_Previous', 'Equity_RetainedEarnings_Current',
                'Equity_RetainedEarnings_Previous', 'Equity_ShareCapital_Current', 'Equity_ShareCapital_Previous','Equity_Other_Current',
                'Equity_Other_Previous', 'Equity_RevaluationReserve_Current', 'Equity_RevaluationReserve_Previous', 'PropertyPlantEquipment_Current',
                'PropertyPlantEquipment_Previous']

    float_cols = ['AverageNumberEmployeesDuringPeriod_Current', 'AverageNumberEmployeesDuringPeriod_Previous']

    dataframe = change_data_types(df = dataframe, columns_to_change = int_cols, to_type = 'int')
    dataframe = change_data_types(df = dataframe, columns_to_change = float_cols, to_type = 'float')
    dataframe.info()

    dataframe = updating_missing_columns(df = dataframe) 
    dataframe = correct_number_employers(df = dataframe) 

    dataframe = update_columns_if_similar_values(df = dataframe)

    dataframe = reoreder_rename_cols(df = dataframe)

    date_cols_year = ['Account Date', 'Action Date']
    date_cols_day = ['Period Start Date', 'Period End Date', 'Balance Sheet Date']

    int_cols = ['Average Number Employees Current', 'Average Number Employees Previous', 'Fixed Assets Current', 'Fixed Assets Previous', 
                'Current Assets Current', 'Current Assets Previous', 'Cash Bank On Hand Current', 'Cash Bank On Hand Previous', 
                'Creditors Within 1Y Current', 'Creditors Within 1Y Previous', 'Creditors After 1Y Current', 'Creditors After 1Y Previous',  
                'Debtors Current', 'Debtors Previous', 'Total Equity Current', 'Total Equity Previous', 'Net Assets Current', 
                'Net Assets Previous', 'Net Current Assets Current', 'Net Current Assets Previous', 
                'Total Assets Less Liabilities Current', 'Total Assets Less Liabilities Previous']

    dataframe = change_data_types(df = dataframe, columns_to_change = date_cols_year, to_type = 'date', date_first = 'year')
    dataframe = change_data_types(df = dataframe, columns_to_change = date_cols_day, to_type = 'date', date_first = 'day')
    dataframe = change_data_types(df = dataframe, columns_to_change = int_cols, to_type = 'int')

    dataframe = create_new_cols(df = dataframe)

    if save_file == True:

        dataframe.to_csv(f'src/Finance_Data/saved_tables/Finance_Data_{datetime.now().strftime('%d-%b-%Y')}.csv', sep = ',', index = False)

    return(dataframe)