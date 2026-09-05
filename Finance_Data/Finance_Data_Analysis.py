import pandas as pd
import numpy as np
import time
import warnings
pd.set_option('display.max_colwidth', None)

import Extracting_Data as ED
import Final_Table_Formatting_Functions as FTFF
import Creating_Final_Table as CFT

api_key = None
url = "https://api.company-information.service.gov.uk/company/"

companies = ['12773942', '11481000', '09752181', '05035690', '03712506', '02516363', '04860838', '11210637', '06987042', '01588942', '02740580', '02582268', '10921663', '10623473', '03864182',
             '02404983', '08313240', '10622354', '12043446', '11558635', '05852516', '06976037', '05167623', '08445134', '11452512', '05714286', '05271676', '07883905', '12299608', '03053472']

number_of_years = 5
number_iterations = len(companies)

def get_company_finances(companies, url, api_key, save_file = False):

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

    finance_data = FTFF.final_table_formatting(dataframe = finance_data, save_file = False)

if __name__ == '__main__':
    get_company_finances(companies = companies, url = url, api_key = api_key, save_file = False)