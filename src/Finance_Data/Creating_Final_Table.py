import pandas as pd
import numpy as np

from Finance_Data import Extracting_Data as ED
from Finance_Data import Final_Table_Formatting_Functions as FTFF
from Finance_Data import Final_Table_Functions as FTF

def get_finance_data_single_table(data, csv_file_name, save_csv=True):

    finance_data = []

    rows_list = [
        'StartDateForPeriodCoveredByReport', 'EndDateForPeriodCoveredByReport',
        'UKCompaniesHouseRegisteredNumber', 'BalanceSheetDate',
        'FixedAssets', 'CurrentAssets', 'PropertyPlantEquipment',
        'Creditors', 'NetCurrentAssetsLiabilities',
        'TotalAssetsLessCurrentLiabilities', 'NetAssetsLiabilities',
        'Equity', 'AverageNumberEmployeesDuringPeriod', 'TotalInventories', 'Debtors', 'CashBankOnHand'

    ]

    data = data[data['has_ixbrl'] == True]
    data = data[data['ixbrl_reader'].apply(callable)]

    for i in range(len(data)):
        row = data.iloc[i]

        account_date = row['date']
        action_date = row['action_date']
        company_number = row['Company Number']

        reader = row.get('ixbrl_reader')
        if not callable(reader):
            None
    
        try:
            html = reader()
        except Exception as e:
            print(f"Failed reader at row {i}: {e}")
            None
    
        result_ixbrl = ED.parse_ixbrl(html)

        ix_data = result_ixbrl.copy()  

        if ix_data is None or ix_data.empty:
            continue

        if 'name' not in ix_data.columns:
            print(f"Missing 'name' column at row {i}")
            continue

        split_cols = ix_data['name'].astype(str).str.split(':', n=1, expand=True)
        ix_data['New_Name'] = split_cols[1].fillna(split_cols[0]).astype(str)

        if 'context' not in ix_data.columns:
            continue
        
        ix_data = ix_data.drop(columns=['tag', 'prefix', 'id', 'scale', 'decimals'], errors='ignore')

        finance = ix_data[ix_data['New_Name'].isin(rows_list)].copy()

        if finance.empty:
            continue

        finance['Company_Number'] = company_number

        finance[['period_type', 'period_end', 'period_date', 'segment']] = finance['context'].apply(FTF.parse_context)

        finance = finance[(finance['period_end'] == 'END') | (finance['period_end'].isna())]

        finance['period_date_parsed'] = finance['period_date'].apply(FTF.parse_date_safe)
        
        finance['creditor_type'] = finance.apply(lambda row: FTF.extract_creditor_type(row['context'], row['name']), axis=1)
        finance['equity_type'] = finance.apply(lambda row: FTF.extract_equity_type(row['context'], row['name'], row['format']), axis = 1)
        finance['period_mapped'] = finance['period_type'].map(FTF.period_mapping())

        finance = FTF.map_period(df = finance, mask_col = 'period_mapped', group_col = 'New_Name', name_col = 'period_date_parsed', rank_col = 'period_rank')
        
        finance['has_segment'] = finance['context'].str.contains('segment', na=False)
        
        finance = (finance.sort_values('has_segment').drop_duplicates(subset=['New_Name', 'period_mapped', 'creditor_type', 'value'], keep='first')
                                                     .drop(columns='has_segment')
                                                     .reset_index(drop = True))

        finance = FTF.equity_creditor_debitors_checks(df = finance)
        finance = FTF.update_period_mapping(df = finance)
        finance = FTF.remove_segments(df = finance)
        
        finance['metric_name'] = finance['New_Name']

        finance = FTF.formatting_with_masks(df = finance)

        finance['value'] = (finance['value'].astype(str).str.replace(',', '', regex=False).str.strip())   

        finance['Final_Name'] = finance['metric_name'] + '_' + finance['period_mapped']

        # finance.to_csv(f'Column_Testing/UpdatedColumns_{company_number}_{i}.csv', sep = ',', index = False)
        
        finance = finance.groupby("Final_Name", group_keys=False, as_index=False).apply(FTF.filter_group, include_groups=False).reset_index(drop = True)      
        
        finance['Final_Name'] = finance['metric_name'] + '_' + finance['period_mapped']

        finance = FTF.account_for_duplicate_names(df = finance)

        prev_to_curr = ['EndDateForPeriodCoveredByReport_Previous', 'BalanceSheetDate_Previous', 'StartDateForPeriodCoveredByReport_Previous',
                'UKCompaniesHouseRegisteredNumber_Previous']

        mapping = {x: x.replace('_Previous', '_Current') for x in prev_to_curr}

        finance["Final_Name"] = finance["Final_Name"].replace(mapping)

        finance["idx"] = finance.groupby("Final_Name").cumcount()
        
        finance["Final_Name"] = np.where(finance["idx"] == 0, finance["Final_Name"], finance["Final_Name"] + "_" + finance["idx"].astype(str))

        finance['value_num'] = pd.to_numeric(finance['value'], errors='coerce')
        
        finance = (finance.groupby(['Company_Number', 'Final_Name', 'period_mapped', 'context'], as_index=False)
                          .agg({'value_num': 'max', 'value': 'first'}))

        finance['Value_Final'] = finance['value'].fillna(finance['value_num'])

        if len(finance) < 20:

            finance_html = FTF.switch_to_html_method(html = html, df = finance)

            if finance_html is not None:
        
                if len(finance_html) > len(finance):
                    finance = finance_html

                finance = FTF.reformat_html_df(df=finance)

        finance_clean = finance[["Final_Name", "Value_Final"]]
        
        out = finance_clean.set_index(['Final_Name']).T 
        
        out = out.reindex(columns=finance_clean['Final_Name'])
        
        out['Company_Number'] = company_number
        out['Account_Date'] = account_date
        out['Action_Date'] = action_date
        
        finance_data.append(out)

    if not finance_data:
        return pd.DataFrame()

    final = pd.concat(finance_data, ignore_index=True)

    final = final.reset_index(drop = True)

    if save_csv:
        final.to_csv(csv_file_name, sep=',', index=False)

    return final