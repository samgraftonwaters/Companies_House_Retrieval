from Finance_Data import Finance_Data_Analysis as FDA
from General_Company_Info import Company_Info_Analysis as CIA

import pandas as pd
import ast
import configparser

print(configparser.__version__)
print(ast.__version__)
print(pd.__version__)

config = configparser.ConfigParser()
config.read("src/config.ini")

if config.getboolean('COMPANIES', 'list') == True:
    companies = ast.literal_eval(config['COMPANIES']['companies'])
else:
    data = pd.read_csv(f'input_data_tables/{config['INPUT']['input_filename']}.csv')
    companies_number_col_name = config['INPUT']['column_name_company_number']
    companies = data[companies_number_col_name]

url = config['LINKS']['url']
api_key = config['LINKS']['api_key']
save_file = config.getboolean('SAVEFILES', 'save_file')

print(url)
if __name__ == '__main__':
    FDA.get_company_finances(companies = companies, url = url, api_key = api_key, save_file = save_file)
    CIA.get_company_info(companies = companies, url = url, api_key = api_key, save_file = save_file)