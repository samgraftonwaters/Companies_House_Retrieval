from Finance_Data import Finance_Data_Analysis as FDA
from General_Company_Info import Company_Info_Analysis as CIA

import pandas as pd
import ast
import configparser
import os
config = configparser.ConfigParser()
config.read("config.ini")

if config.getboolean('COMPANIES', 'list') == True:
    companies = ast.literal_eval(config['COMPANIES']['companies'])
else:
    data = pd.read_csv(f'input_data_tables/{config['INPUT']['input_filename']}.csv')
    companies_number_col_name = config['INPUT']['column_name_company_number']
    companies = data[companies_number_col_name]

url = config['LINKS']['url']
api_key = config['LINKS']['api_key']
save_file = config['SAVEFILES']['save_file']

if __name__ == 'main':
    FDA.get_company_finances(companies = companies, url = url, api_key = api_key, save_file = save_file)
    CIA.get_company_info(companies = companies, url = url, api_key = api_key, save_file = save_file)