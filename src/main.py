from Finance_Data import Finance_Data_Analysis as FDA
from General_Company_Info import Company_Info_Analysis as CIA

import pandas as pd
import ast
import configparser

config = configparser.ConfigParser()
config.read("src/config.ini")

if config['INPUT']['input_filename'] != 'None':
    data = pd.read_csv(f'src/input_data_tables/{config['INPUT']['input_filename']}.csv')
    companies_number_col_name = config['INPUT']['column_name_company_number']
    companies = data[companies_number_col_name].astype("string")

else:
    companies = ast.literal_eval(config['INPUT']['companies_list'])

if __name__ == '__main__':

    url = config['LINKS']['url']
    api_key = config['LINKS']['api_key']
    save_file = config.getboolean('SAVEFILES', 'save_file')
    number_of_years = config.getint('FINANCES', 'number_of_years')
    
    FDA.get_company_finances(companies = companies, url = url, api_key = api_key, 
                             number_of_years = number_of_years, save_file = save_file)
    CIA.get_company_info(companies = companies, url = url, api_key = api_key, save_file = save_file)