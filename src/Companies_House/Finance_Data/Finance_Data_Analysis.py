import pandas as pd
import numpy as np
import time
import warnings
pd.set_option('display.max_colwidth', None)

from Companies_House import Extracting_Data as ED
from Companies_House import Final_Table_Formatting_Functions as FTFF
from Companies_House import Creating_Final_Table as CFT

api_key = None
url = "https://api.company-information.service.gov.uk/company/"

companies = ['12773942', '11481000', '09752181', '05035690', '03712506', '02516363', '04860838', '11210637', '06987042', '01588942', '02740580', '02582268', '10921663', '10623473', '03864182',
             '02404983', '08313240', '10622354', '12043446', '11558635', '05852516', '06976037', '05167623', '08445134', '11452512', '05714286', '05271676', '07883905', '12299608', '03053472']

number_of_years = 5
number_iterations = len(companies)

data = ED.pull_finance_data_from_api(iterative_range = number_iterations, company_data = companies, 
                                  number_col_name = 'OrganisationCompaniesHouseNumber')


accounts_update = ED.get_accounts_data(data = data, number_of_years = number_of_years)


accounts_update['ixbrl_reader'] = accounts_update.apply(
    lambda r: ED.make_ixbrl_reader(r['content_url']) if r['has_ixbrl'] else None,
    axis=1
)
print(len(accounts_update))
accounts_update.head(2)


finance_data_single_table = CFT.get_finance_data_single_table(data = accounts_update, csv_file_name = 'test_data_output.csv', save_csv = False)

print(finance_data_single_table.head(20))
print(finance_data_single_table.info())
finance_data = finance_data_single_table.copy()

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

finance_data = FTFF.change_data_types(df = finance_data, columns_to_change = int_cols, to_type = 'int')
finance_data = FTFF.change_data_types(df = finance_data, columns_to_change = float_cols, to_type = 'float')
finance_data.info()

# finance_data.to_csv('intermediate_test.csv', sep = ',', index = False)

finance_data = FTFF.updating_missing_columns(df = finance_data) 
finance_data = FTFF.correct_number_employers(df = finance_data) 

finance_data[f'Equity_ShareCapital_Previous'] = np.where(finance_data[f'Equity_ShareCapital_Previous'].isna() == True, 
                                                        finance_data[f'Equity_ShareCapital_Current'], 
                                                        finance_data[f'Equity_ShareCapital_Previous'])

finance_data['UKCompaniesHouseRegisteredNumber_Current'] = np.where(finance_data['UKCompaniesHouseRegisteredNumber_Current'].isna() == True, 
                                                                    finance_data['Company_Number'],
                                                                    finance_data['UKCompaniesHouseRegisteredNumber_Current'])
finance_data = finance_data.drop('Company_Number', axis = 1)
print(finance_data.head(20))
print(finance_data.info())

reorder_cols = ['UKCompaniesHouseRegisteredNumber_Current', 'Account_Date', 'Action_Date',  
                'StartDateForPeriodCoveredByReport_Current', 'EndDateForPeriodCoveredByReport_Current', 'BalanceSheetDate_Current', 
                'AverageNumberEmployeesDuringPeriod_Current', 'AverageNumberEmployeesDuringPeriod_Previous', 'FixedAssets_Current', 
                'FixedAssets_Previous', 'CurrentAssets_Current', 'CurrentAssets_Previous', 'CashBankOnHand_Current', 'CashBankOnHand_Previous', 
                'Creditors_Within1Y_Current', 'Creditors_Within1Y_Previous', 'Creditors_After1Y_Current', 'Creditors_After1Y_Previous',
                'Debtors_Current', 'Debtors_Previous', 'Equity_TotalEquity_Current', 
                'Equity_TotalEquity_Previous', 'NetAssetsLiabilities_Current', 'NetAssetsLiabilities_Previous', 'NetCurrentAssetsLiabilities_Current', 
                'NetCurrentAssetsLiabilities_Previous', 'TotalAssetsLessCurrentLiabilities_Current', 'TotalAssetsLessCurrentLiabilities_Previous']

finance_data = finance_data.loc[:, reorder_cols]

rename_cols = ['Companies House Number', 'Account Date', 'Action Date', 'Period Start Date', 'Period End Date', 
               'Balance Sheet Date', 'Average Number Employees Current', 'Average Number Employees Previous', 'Fixed Assets Current', 
               'Fixed Assets Previous', 'Current Assets Current', 'Current Assets Previous', 'Cash Bank On Hand Current', 'Cash Bank On Hand Previous', 
               'Creditors Within 1Y Current', 'Creditors Within 1Y Previous', 'Creditors After 1Y Current', 'Creditors After 1Y Previous',  
               'Debtors Current', 'Debtors Previous', 'Total Equity Current', 'Total Equity Previous', 'Net Assets Liabilities Current', 
               'Net Assets Liabilities Previous', 'Net Current Assets Liabilities Current', 'NetCurrent Assets Liabilities Previous', 
               'Total Assets Less Liabilities Current', 'Total Assets Less Liabilities Previous']

finance_data.columns = rename_cols

date_cols_year = ['Account Date', 'Action Date']
date_cols_day = ['Period Start Date', 'Period End Date', 'Balance Sheet Date']

int_cols = ['Average Number Employees Current', 'Average Number Employees Previous', 'Fixed Assets Current', 'Fixed Assets Previous', 
            'Current Assets Current', 'Current Assets Previous', 'Cash Bank On Hand Current', 'Cash Bank On Hand Previous', 
            'Creditors Within 1Y Current', 'Creditors Within 1Y Previous', 'Creditors After 1Y Current', 'Creditors After 1Y Previous',  
            'Debtors Current', 'Debtors Previous', 'Total Equity Current', 'Total Equity Previous', 'Net Assets Liabilities Current', 
            'Net Assets Liabilities Previous', 'Net Current Assets Liabilities Current', 'NetCurrent Assets Liabilities Previous', 
            'Total Assets Less Liabilities Current', 'Total Assets Less Liabilities Previous']

finance_data = FTFF.change_data_types(df = finance_data, columns_to_change = date_cols_year, to_type = 'date', date_first = 'year')
finance_data = FTFF.change_data_types(df = finance_data, columns_to_change = date_cols_day, to_type = 'date', date_first = 'day')
finance_data = FTFF.change_data_types(df = finance_data, columns_to_change = int_cols, to_type = 'int')


finance_data['Total Assets Current'] = (np.where(finance_data['Fixed Assets Current'].isna() == False, finance_data['Fixed Assets Current'], 0)
                                        + np.where(finance_data['Current Assets Current'].isna() == False, finance_data['Current Assets Current'], 0))
finance_data['Total Assets Previous'] = (np.where(finance_data['Fixed Assets Previous'] .isna() == False, finance_data['Fixed Assets Previous'], 0)
                                         + np.where(finance_data['Current Assets Previous'].isna() == False, finance_data['Current Assets Previous'], 0))

finance_data["Period Current Year"] = np.where(finance_data["Period End Date"].isna() == False, finance_data["Period End Date"].dt.year,
                                               finance_data["Action Date"].dt.year)
finance_data["Period Previous Year"] = np.where(finance_data["Period End Date"].isna() == False, finance_data["Period End Date"].dt.year - 1,
                                                finance_data["Action Date"].dt.year - 1)

print(finance_data.head(20))
print(finance_data.info())
finance_data.to_csv('Cleaned_Output_test_newOrgs_11.csv', sep = ',', index = False)