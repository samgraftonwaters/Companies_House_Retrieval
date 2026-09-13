import pandas as pd
import numpy as np
import time
import warnings
pd.set_option('display.max_colwidth', None)

from Finance_Data import Extracting_Data as ED
from Finance_Data import Final_Table_Formatting_Functions as FTFF
from Finance_Data import Creating_Final_Table as CFT

import configparser
import ast
config = configparser.ConfigParser()
config.read("src/config.ini")

def get_company_finances(companies, url, api_key, number_of_years, save_file = False):

    data = ED.pull_finance_data_from_api(company_house_numbers = companies, url = url, api_key = api_key)

    accounts_update = ED.get_accounts_data(data = data, number_of_years = number_of_years, api_key = api_key)

    accounts_update['ixbrl_reader'] = accounts_update.apply(
        lambda r: ED.make_ixbrl_reader(content_url = r['content_url'], api_key = api_key) if r['has_ixbrl'] else None,
        axis=1
    )

    finance_data_single_table = CFT.get_finance_data_single_table(data = accounts_update, csv_file_name = 'test_data_output.csv', save_csv = False)

    print(finance_data_single_table.head(20))
    print(finance_data_single_table.info())
    finance_data = finance_data_single_table.copy()

    finance_data = FTFF.final_table_formatting(dataframe = finance_data, save_file = save_file)

    print('Finance Analysis Complete')

if __name__ == '__main__':

    if config['INPUT']['input_filename'] != 'None':
        data = pd.read_csv(f'src/input_data_tables/{config['INPUT']['input_filename']}.csv')
        companies_number_col_name = config['INPUT']['column_name_company_number']
        companies = data[companies_number_col_name].astype("string")

    else:
        companies = ast.literal_eval(config['INPUT']['companies_list'])

    url = config['LINKS']['url']
    api_key = config['LINKS']['api_key']
    save_file = config.getboolean('SAVEFILES', 'save_file')
    number_of_years = config.getint('FINANCES', 'number_of_years')

    get_company_finances(companies = companies, url = url, api_key = api_key, 
                         number_of_years = number_of_years, save_file = save_file)