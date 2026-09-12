import pandas as pd
import numpy as np
import re
import time

from Finance_Data import Extracting_Data as ED

"""
Note, these functions were created with the help of MS CoPilot
"""

def map_period(df, mask_col = 'period_mapped', group_col = 'New_Name', name_col = 'period_date_parsed', rank_col = 'period_rank'):

    mask = df[mask_col].isna()
    
    df.loc[mask, rank_col] = (
        df.loc[mask]
        .groupby(group_col)['period_date_parsed']
        .rank(method='dense', ascending=False)
    )
    
    df.loc[df[rank_col] == 1, mask_col] = 'Current'
    df.loc[df[rank_col] == 2, mask_col] = 'Previous'
    
    return(df)


def equity_creditor_debitors_checks(df):

    filter_check = df.copy()
    
    creditors_check = filter_check[filter_check['name'].str.contains('Creditors')]
    if any(creditors_check['context'].str.contains('x-6')) == True:
        df['creditor_type'] = np.where((df['creditor_type'] == 'Within1Y') & (~df['context'].str.contains('x-6')), 'After1Y', 
                                            df['creditor_type'])

    equity_check = filter_check[filter_check['name'].str.contains('Equity')]
    if any(equity_check['context'].str.contains('x-6')) == True:
        df['equity_type'] = np.where((df['equity_type'] == 'ShareCapital') & (df['context'].str.contains('x-8')), 
                                          'TotalEquity', df['equity_type'])
        df['equity_type'] = np.where((df['name'].str.contains('Equity')) & (df['context'].str.contains('x-8')), 
                                          'TotalEquity', df['equity_type'])

    debitor_check = filter_check[filter_check['name'].str.contains('Debtors')]
    if any(debitor_check['context'].str.contains('Debtors_')) == True:
        df['segment'] = np.where(df['context'].str.contains('Debtors_'), 'REMOVE', df['segment'])
        
    return(df)


def update_period_mapping(df):

    filter_check = df.copy()
    
    property_plant_check = filter_check[filter_check['name'].str.contains('PropertyPlantEquipment')]
    if any(df['period_date_parsed'].isna() ==True) == True:
        df['period_mapped'] = np.where((df['name'].str.contains('PropertyPlantEquipment')) & 
                                            (df['context'].str.contains('company-BFwd-instant')), 
                                            None, df['period_mapped'])
        df['period_mapped'] = np.where((df['name'].str.contains('PropertyPlantEquipment')) & 
                                        (df['context'].str.contains('PPE-SegmentsHypercube')), 
                                        None, df['period_mapped'])

    return(df)


def remove_segments(df):
    df = df.copy()
    
    df = df[df['segment'] != 'bfwd']
    
    df['segment'] = np.where((df['New_Name'] == 'PropertyPlantEquipment') & (df['context'].str.contains('Current-instant-x-')),
                                  'REMOVE', df['segment'])

    df['segment'] = np.where((df['New_Name'] == 'Debtors') & (df['context'].str.contains('-instant-x-')), 'REMOVE',
                                  df['segment'])

    df['segment'] = np.where((df['New_Name'] == 'Debtors') & (df['context'].str.contains('Set5')), 'REMOVE',
                                  df['segment'])

    df = df[df['segment'] != 'REMOVE']

    return(df)



def formatting_with_masks(df):

    mask_creditors = df['New_Name'] == 'Creditors'

    df.loc[mask_creditors, 'metric_name'] = df.loc[mask_creditors, 'New_Name'] + '_' + df.loc[mask_creditors, 'creditor_type'].fillna('Within1Y')

    mask_equity = df['New_Name'] == 'Equity'
    
    df.loc[mask_equity, 'metric_name'] = df.loc[mask_equity, 'New_Name'] + '_' + df.loc[mask_equity, 'equity_type']

    date_fields = ['StartDateForPeriodCoveredByReport', 'EndDateForPeriodCoveredByReport', 'BalanceSheetDate']
    
    mask_date = df['New_Name'].isin(date_fields)
    
    df.loc[mask_date, 'value'] = normalise_dates(df.loc[mask_date, 'value'])

    return(df)


def parse_context(ctx):
    ctx = str(ctx)
    
    number_tokens = ['c222', 'c223', 'c224', 'c225', 'c273', 'c279', 'c604', 'c603', 'c587', 'c570', 'c571', 'c645', 'c874', 'c798', 
                     'c827', 'c831', 'c832', 'c798', 'c799', 'c349', 'c350', 'c366', 'c383', 'c424', 'c1', 'c2', 'c3', 'c4', 'c7', 'c643', 
                     'I0', 'I5', 'I6', 'I7', 'I8', 'I9', 'D0', 'D13', 'eFY1', 'yFY1', 'sFY1', 'eFY0', 'I2', 'I3', 'I4', 'c348', 'c376', 'c347', 'c375'] ##'E_', 'B_', 

    letter_tokens = ['cfwd', 'bfwd', 'CY', 'PY', 'cur', 'prev', 'TMinusZero', 'TMinusOne', 'Current', 'Comparative', 'companyA', 'withinoneyear',
                     'CURRENT', 'PREVIOUS', 'previous', 'company-BFwd-instant', 'CurrYearEnd', 'CurrYearStart', 'CompYear', 'companyA_prev',
                     'withinoneyear_prev', 'WithinOneYear_PeriodEnd_TMinusZero', 'WithinOneYear_PeriodEnd_TMinusOne']

    single_letter_pattern = r'\b(?:B|E|C|F)\b'

    number_token_pattern = '|'.join(map(re.escape, sorted(number_tokens, key=len, reverse=True)))
    letter_token_pattern = '|'.join(map(re.escape, sorted(letter_tokens, key=len, reverse=True)))

    pattern = (rf'{single_letter_pattern}'
               rf'|\b(FY\d+|{number_token_pattern})\b|{letter_token_pattern}')
    
    ctx_lower = str(ctx).lower()
    if ctx_lower.startswith('b_'):
        period_token = 'B_'
    elif ctx_lower.startswith('e_'):
        period_token = 'E_'
    elif 'icur' in ctx_lower:
        period_token = 'Current'
    elif 'iprev' in ctx_lower:
        period_token = 'Previous'
    else:
        period_match = re.search(pattern, ctx, flags=re.IGNORECASE)
        period_token = period_match.group(0) if period_match else None

    period_type = period_token #period_match.group(1) if period_match else Non

    period_end = 'END' if 'END' in ctx else 'START' if 'START' in ctx else None

    date_match = re.search(r'(\d{2}[./_-]\d{2}[./_-]\d{2,4})|(\d{8})', ctx)
    # period_date = date_match.group(1).replace('_', '/').replace('.', '/').replace('-', '/') if date_match else None

    period_date = None
    
    if date_match:
        if date_match.group(1):
            period_date = (date_match.group(1).replace('_', '/').replace('.', '/').replace('-', '/'))
        elif date_match.group(2):
            period_date = re.sub(r'(\d{4})(\d{2})(\d{2})', r'\1/\2/\3', date_match.group(2))

    segment = 'consolidated' if 'Consolidated' in ctx else None

    if re.search(r'-BFwd-instant-x-\d+', ctx, re.IGNORECASE):
        segment = 'bfwd'
    else:
        segment_match = re.search(r'-(Current|Comparative)-', ctx, re.IGNORECASE)
        segment = segment_match.group(1).lower() if segment_match else None

    return pd.Series([period_type, period_end, period_date, segment])



def extract_equity_type(ctx, name_col, format_col):
    ctx = str(ctx).lower()
    name_col = str(name_col).lower()

    if 'equity' in name_col:

        # Special rule discovered in the data:
        # NULL format + Set2/3/4 => ShareCapital
        if pd.isna(format_col) and any(s in ctx for s in ['set2', 'set3', 'set4']):
            return 'ShareCapital'

        rules = [

            # Other
            (['otherreservessubtotal'], 'Other'),

            # Share Capital
            (['sharecapital', 'c645', 'c643', 'amx_amy', 'zn_zo', 'xy_xz', 'qg_qh', 'ba_bb', 'ib_ic', 'ay_t_az', 'bc_bd', 'set3',
              'ajd_aje', 'kg_kh', 'i11', 'x-9', 'c424', 'dc_dd', 'x-5', 'x-4', 'c874', 'eo_ep', 'at_au', 'ap_aq', 'ef_eg', 'do_dp', 'ah_ai', 
              'avz_axl', 'aol_apx', 'yn_zz', 'iw_ix', 'ahm_ahn', 'xd_xf', 'lr_rt', 'ob_oc', 'bo_bp', 'cm_cn', 'gh_gi', 'ju_jv', 'ie_jf', 'ff_gl',
             'cgs_cgt', 'uu_uv', 'ac_ad', 'ju_jv', 'eu_hj'],
             'ShareCapital'),

            # Revaluation Reserve
            (['revaluationreserve', 'ba_bc', 'bc_be',
              'ib_id', 'qg_qi', 'zn_zp'],
             'RevaluationReserve'),

            # Retained Earnings
            (['retainedearnings', 'retainedearningsaccumulatedlosses', 'set4'],
             'RetainedEarnings'),

            # Total Equity
            (['bus-groupcompanydatadimension.bus-consolidated', 'cfwd', 'amx_amz', 'end', 'prev8', 'cur1', 'b', 'e', 'ag_ai', 'i0', 'i2', 'i5', 'c224', 
              'c225', 'x-10', 'periodend_tminus', 'c3', 'c4', 'c273', 'c279', 'dc_de', 'ap_ar', 'ef_eh', 'do_dq', 'ah_aj', 'avz_axm', 'x-7', 'x-6',
             'iw_iy', 'ahm_aho', 'xd_xe', 'lr_mn', 'i4', 'i3'],
             'TotalEquity'),
        ]

    else:
        rules = [
            (['set2', 'set4'], 'ShareCapital')
        ]

    for keywords, result in rules:
        matched = False

        for k in keywords:
            if k in ('b', 'e'):
                if re.search(rf'\b{k}\b', ctx):
                    matched = True
                    break
            elif k in ctx:
                matched = True
                break

        if matched:
            return result

    return None



def extract_creditor_type(ctx, name_col):
    ctx = str(ctx).lower()
    name_col = str(name_col).lower()

    rules = [
        (
            [
                'withinoneyear', 'alq_amv', 'b_wl_xu', 'ahs_aiz', 'bs', 'p_ay', 'c598', 'c570', 'c571', 'c751', 'i5', 'i6', 'i7', 
                'creditorswithinoneyear', 'gq_hx', 'pd_qc', 'ym_zl', 'prev9', 'prev10', 'icur9', 'wl_xu', 'jd_kc', 'd_ac', 'x-7', 'x-6', 
                'fy_end_current', 'c349', 'c350', 'cn_cy', 'c798', 'c827', 'z_ak', 'ee_em', 'dim003', 'dim004', 'cnc1', 'g_an', 'cy_ee', 'co_dn', 
                'h_ag', 'awc_ayf', 'aop_aqp', 'yr_zx', 'aiw_ajv', 'wb_xa', 'qr_rz', 'mr_ny', 'cas_cbz', 'kz_ly', 'ack_adj', 'dv_fe', 'me_nn',
                'o_an', 'lj_mi', 'du_eu_dy_ev', 'mr_oa', 'ag_bn', 'bm_cl', 'fq_gg', 'instant-x-3', 'kf_lo', 'vu_xb', 'agl_ahk', 'hv_iu', 's_ar',
                'qc_sk', 'f_q', 'c_aj', 'dk_ej', 'is_jr', 'core-withinoneyear', 'ia_jh', 'dw_ge', 'c375', 'c376', 's_bb', 'qa_rh', 'te_ul', 'ds_er',
                'set7', 'set8', 'ex_gf', 'bij_bjp', 'lw_mh', 'af_aq', 'anm_anx', 'Set3', 'c346', 'c347'

            ],
            'Within1Y'
        ),
        (
            [
                'afteroneyear', 'alq_amw', 'b_wl_xw', 'ahs_ahb', 'az', 'p_ba_t_bb', 'c599', 'c603', 'c604', 'i9', 'i8', 'creditorsafteroneyear',
                'gq_hz_gu_ia', 'pd_qe_ph_qf', 'wl_xw', 'jd_ke', 'd_ae_h_af', 'x-8', 'iprev12', 'icur11', 'c366', 'c383', 'cn_da_cr_db', 'c831', 
                'c832', 'z_ar', 'ee_en', 'dim005', 'dim006', 'awg_axk', 'qr_sa', 'mr_oa_mv_ob', 'cas_cbb_caw_ccc', 'kz_ma_ld_mb', 'ack_adk', 'df_fg',
                'me_np', 'o_ap', 'lj_mk_ln_ml', 'du_ew', 'instant-x-4', 'kj_lq', 'c_al_g_am', 'dk_el_do_em', 'is_jt_iw_ju', 'core-afteroneyear', 
                '_noncurrent', 'g_ap_k_aq', 's_bc', 'qa_ri', 'te_um', 'ds_es', 's_as', 'set9', 'set10', 'ex_gh_fb_gi', 'bij_bjr_bin_bjs', 
                'lw_mo_ma_mp', 'af_ax_aj_ay', 'anm_aoe_anq_aof', 'Set4'
                
            ],
            'After1Y'
        )
    ]

    # Handle moving Set values
    if 'creditors' in name_col:
        if 'set1' in ctx:
            return 'Within1Y'
        # if 'CreditorsHypercube' and 'set2' in ctx:
        #     return 'Within1Y'
        if 'set2' in ctx:
            return 'After1Y'

    for keywords, result in rules:
        if any(k in ctx for k in keywords):
            return result

    return None


def parse_date_safe(x):
    try:
        return pd.to_datetime(x, dayfirst=True, errors='coerce')
    except:
        return pd.NaT



def filter_group(g):
    if len(g) == 1:
        return g

    be = g[~g["context"].str.contains(r"_|START|END", regex = True)]
    return be if not be.empty else g.head(1)



def period_mapping():
    current = ['FY1', 'CY', 'B', 'C', 'B_', 'c222', 'c224', 'c604', 'c570', 'c645', 'cur', 'I0', 'I6', 'I8', 'D0', 'TMinusZero', 
               'Current', 'current', 'company-BFwd-instant', 'CURRENT', 'CUR', 'CurrYearEnd', 'CompYearEnd', 'Cur', 'c3', 'c349', 'c366', 'c424', 
               'c1', 'c273', 'c798', 'c831', 'c798', 'c874', 'b_dc_dd', 'b_ee_em', 'dim003', 'dim005', 'eFY1', 'sFY1', 'yFY1', 'I3', 'yearend_dim003',
              'c347', 'c375', 'companyA', 'withinoneyear', 'WithinOneYear_PeriodEnd_TMinusZero', 'c346']
    
    previous = ['FY2', 'PY', 'E', 'F', 'E_', 'c223', 'c225', 'c587', 'c571', 'c643', 'c603', 'I5', 'I7', 'I9', 'D13', 'TMinusOne', 'D12',
                'Comparative', 'PREVIOUS', 'PREV', 'prev', 'previous', 'Previous', 'CurrYearStart', 'c4', 'c350', 'c383', 'c2', 'c279', 'c7', 'c827', 
                'c832', 'I4', 'c799', 'e_ee_em', 'dim004', 'dim006', 'eFY0', 'I2', 'yearend_dim004', 'CompYear', 'CompYearDuration', 'c348', 'c376', 
                'companyA_prev', 'withinoneyear_prev', 'WithinOneYear_PeriodEnd_TMinusOne', 'c0', 'c347']
        
    mapping = {k: 'Current' for k in current}
    mapping.update({k: 'Previous' for k in previous})
    return(mapping)



def account_for_duplicate_names(df):
    current_contexts = {"I0", "I4"}
    previous_contexts = {"I3", "I5"}
    
    # Create a temporary base name just for identifying duplicates
    base_name = df["Final_Name"].str.replace(r"_(Current|Previous)$", "", regex=True)
    
    # Only rows belonging to duplicated names
    dup_mask = base_name.duplicated(keep=False)
    
    # Correct only duplicate groups
    df.loc[dup_mask & df["context"].isin(current_contexts), "Final_Name"] = (df.loc[dup_mask & df["context"].isin(current_contexts), "Final_Name"]
        .str.replace(r"_(Current|Previous)$", "_Current", regex=True))
    
    df.loc[dup_mask & df["context"].isin(previous_contexts), "Final_Name"] = (df.loc[dup_mask & df["context"].isin(previous_contexts),"Final_Name"]
        .str.replace(r"_(Current|Previous)$", "_Previous", regex=True))

    return(df)


def extract_rendered_financials(rendered_df):

    lines = rendered_df["row_text"].dropna().astype(str).str.strip().tolist()

    rows = []

    current_heading = None

    finance_info = ["Fixed assets", "Current assets", "Creditors: amounts falling due within one year", "Net current assets", 
                    "Total assets less current liabilities", "Net assets", "Capital and reserves"]

    for line in lines:

        if line in finance_info:
            current_heading = line
            continue

        if current_heading:

            rows.append({"New_Name": current_heading, "value": line, "context": "rendered"})

    return pd.DataFrame(rows)


def normalise_dates(series):
    s = series.astype(str).str.strip()

    parsed = pd.Series(index=s.index, dtype='datetime64[ns]')

    formats = ['%d-%b-%y', '%d-%b-%Y', '%d-%B-%y', '%d-%B-%Y', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%y', '%d-%m-%y', '%d.%m.%y', 
               '%d.%b.%y', '%d.%b.%Y', '%d.%B.%y', '%d.%B.%Y', '%y-%b-%d', '%Y %B %d', '%Y %b %d', '%d %B %Y', '%d %B %y', '%d %b %Y', '%d %b %y']

    for fmt in formats:
        mask = parsed.isna()
        parsed.loc[mask] = pd.to_datetime(s.loc[mask], format=fmt, errors='coerce')

    return parsed.dt.strftime('%d/%m/%Y')


def switch_to_html_method(html, df):

    result_html = ED.parse_html(html)

    html_data = extract_rendered_financials_mapped(result_html)

    if html_data.empty:
        return(None)

    df_html = html_data.copy()

    df_html["Final_Name"] = df_html["New_Name"] + "_" + df_html["period_mapped"]
    df_html['Value_Final'] = df_html['value']

    df['Final_Name'] = df['Final_Name'] + "_Original"

    df = pd.concat([df_html, df[['Final_Name', 'Value_Final']]], axis = 0)
    
    df = df.drop_duplicates(subset='Final_Name').reset_index(drop = True)

    return(df)



def reformat_html_df(df):

    valid_employee_names = set(df.loc[df['Final_Name'].str.startswith('AverageNumberEmployeesDuringPeriod_')
        & df['Final_Name'].str.endswith('_Original'), 'Final_Name'].str.replace('_Original$', '', regex=True))

    for suffix in ['Current', 'Previous']:

        original_number = df.loc[df['Final_Name'] == f'UKCompaniesHouseRegisteredNumber_{suffix}_Original', 'Value_Final']

        current_number = df.loc[df['Final_Name'] == f'UKCompaniesHouseRegisteredNumber_{suffix}', 'Value_Final']

        if not original_number.empty and (current_number.empty or original_number.iloc[0] != current_number.iloc[0]):
            df = df[df['Final_Name'] != f'UKCompaniesHouseRegisteredNumber_{suffix}'].copy()
            df.loc[df['Final_Name'] == f'UKCompaniesHouseRegisteredNumber_{suffix}_Original', 'Final_Name'] = f'UKCompaniesHouseRegisteredNumber_{suffix}'

        original_employees = df.loc[df['Final_Name'] == f'AverageNumberEmployeesDuringPeriod_{suffix}_Original', 'Value_Final']

        current_employees = df.loc[df['Final_Name'] == f'AverageNumberEmployeesDuringPeriod_{suffix}', 'Value_Final']

        if not original_employees.empty and (current_employees.empty or original_employees.iloc[0] != current_employees.iloc[0]):
            df = df[df['Final_Name'] != f'AverageNumberEmployeesDuringPeriod_{suffix}'].copy()
            df.loc[df['Final_Name'] == f'AverageNumberEmployeesDuringPeriod_{suffix}_Original', 'Final_Name'] = f'AverageNumberEmployeesDuringPeriod_{suffix}'

    df = df[~(df['Final_Name'].str.startswith('AverageNumberEmployeesDuringPeriod_')
              & ~df['Final_Name'].str.replace('_Original$', '', regex=True).isin(valid_employee_names))].copy()

    df['Final_Name'] = df['Final_Name'].str.replace('_Original', '', regex=False)

    return(df)


def add_concept(name, current, previous):
    """
    Add a financial concept to the output rows list.

    Creates up to two records:
    - Current period value
    - Previous period value

    Parameters
    ----------
    name : str
        Standardised concept name, e.g. 'Debtors'.

    current : str | int | float | None
        Current-period value.

    previous : str | int | float | None
        Previous-period value.

    Notes
    -----
    Values are converted to strings and commas are removed to
    ensure consistency with the rest of the extraction pipeline.

    Example
    -------
    add_concept("Debtors", "17,361", "2,425")

    Produces:
        Debtors | 17361 | Current
        Debtors | 2425  | Previous
    """

    if current is not None:
        current_row = {
            "New_Name": name,
            "value": str(current).replace(",", ""),
            "period_mapped": "Current",
            "context": "rendered"
        }

    if previous is not None:
        previous_row = {
            "New_Name": name,
            "value": str(previous).replace(",", ""),
            "period_mapped": "Previous",
            "context": "rendered"
        }

    return(current_row, previous_row)


def extract_numeric_values(lines, start_idx, required=2):

    """
    Extract financial values from rendered HTML text.

    Starting from a specified position in the document,
    scans forward and returns the next financial values found.

    The function ignores note references such as:

        Tangible assets
        4
        2,166,129
        1,585,000

    where '4' is a note number rather than a financial value.

    Parameters
    ----------
    lines : list[str]
        List of text rows extracted from the rendered HTML.

    start_idx : int
        Position from which to begin searching.

    required : int, default 2
        Number of financial values to return.

    Returns
    -------
    list[str]
        Financial values with commas removed.

    Example
    -------
    Input rows:

        Tangible assets
        4
        2,166,129
        1,585,000

    Returns:

        ['2166129', '1585000']
    """

    nums = []
    j = start_idx

    while j < len(lines) and len(nums) < required:

        txt = str(lines[j]).strip()

        # Skip note references such as 4,5,6,7
        if re.fullmatch(r"\d{1,2}", txt):
            j += 1
            continue

        if re.fullmatch(r"-?[\d,]+", txt):
            nums.append(txt.replace(",", ""))

        j += 1

    return nums



def extract_rendered_financials_mapped(rendered_df):
    """
    Extract financial statement data from rendered Companies House HTML.

    This function is used as a fallback when detailed iXBRL facts are not
    available. It parses the rendered HTML text, identifies key balance
    sheet line items, and maps them into a standardised format consistent
    with the iXBRL extraction process.

    The function:

    1. Converts the rendered HTML rows into a list of text lines.
    2. Keeps only the Statement of Financial Position section and ignores
       subsequent notes and accounting policy disclosures.
    3. Extracts financial values associated with key balance sheet items.
    4. Ignores footnote references (e.g. note numbers 4, 5, 6, 7).
    5. Maps extracted values to standard concept names such as:
       - PropertyPlantEquipment
       - CurrentAssets
       - Debtors
       - CashBankOnHand
       - Creditors
       - NetCurrentAssetsLiabilities
       - TotalAssetsLessCurrentLiabilities
       - NetAssetsLiabilities
       - Equity
       - AverageNumberEmployeesDuringPeriod
    6. Returns the results in the same structure used by the iXBRL parser.

    Parameters
    ----------
    rendered_df : pandas.DataFrame
        DataFrame produced by parse_html(), containing a column called
        'row_text' with the rendered financial statement text.

    Returns
    -------
    pandas.DataFrame
        Standardised financial data containing:

        - New_Name
            Standard concept name.

        - value
            Extracted financial value.

        - period_mapped
            'Current' or 'Previous'.

        - context
            Set to 'rendered' to indicate the value was extracted from
            rendered HTML rather than tagged iXBRL facts.

    Examples
    --------
    Input:

        Fixed assets
        Tangible assets
        4
        2,166,129
        1,585,000

    Output:

        New_Name                  value     period_mapped
        -------------------------------------------------
        PropertyPlantEquipment    2166129  Current
        PropertyPlantEquipment    1585000  Previous

    Notes
    -----
    Some Companies House filings contain balance sheet figures only in
    rendered XHTML and not as tagged iXBRL facts. This function is designed
    to extract those values so they can be processed using the same
    downstream pipeline as normal iXBRL data.
    """

    rows = []

    lines = (rendered_df["row_text"].dropna().astype(str).str.strip().tolist())

    # Only use the statement section
    stop_markers = ["Judgements and key sources of estimation uncertainty", "Accounting policies"]

    statement_lines = []

    for line in lines:

        if any(marker in line for marker in stop_markers):
            break

        statement_lines.append(line)

    # ---------------------------------
    # Main balance sheet extraction
    # ---------------------------------

    for i, line in enumerate(statement_lines):

        # Property Plant Equipment
        if line == "Tangible assets":

            nums = extract_numeric_values(statement_lines, i + 1, required=2)
            
            if len(nums) == 2:
                current_row, previous_row = add_concept("PropertyPlantEquipment", nums[0], nums[1])
                rows.append(current_row)
                rows.append(previous_row)
                
        # Debtors
        elif line == "Debtors":

            nums = extract_numeric_values(statement_lines, i + 1, required=2)

            if len(nums) == 2:
                current_row, previous_row = add_concept("Debtors", nums[0], nums[1])
                rows.append(current_row)
                rows.append(previous_row)
                
        # Cash + Current Assets
        elif line == "Cash at bank and in hand":

            nums = extract_numeric_values(statement_lines, i + 1, required=4)

            if len(nums) >= 2:
                current_row, previous_row = add_concept("CashBankOnHand", nums[0], nums[1])
                rows.append(current_row)
                rows.append(previous_row)
            if len(nums) >= 4:
                current_row, previous_row = add_concept("CurrentAssets", nums[2], nums[3])
                rows.append(current_row)
                rows.append(previous_row)
                
        # Creditors within one year
        elif line == "Creditors: amounts falling due within one year":

            nums = extract_numeric_values(statement_lines, i + 1, required=4)

            if len(nums) >= 2:
                current_row, previous_row = add_concept("Creditors_Within1Y", float(nums[0].replace(",", "")), float(nums[1].replace(",", "")))
                rows.append(current_row)
                rows.append(previous_row)
            if len(nums) >= 4:
                current_row, previous_row = add_concept("NetCurrentAssetsLiabilities", nums[2], nums[3])
                rows.append(current_row)
                rows.append(previous_row)
                
        # Total assets less current liabilities
        elif line == "Total assets less current liabilities":

            nums = extract_numeric_values(statement_lines, i + 1, required=2)

            if len(nums) >= 2:

                current_row, previous_row = add_concept("TotalAssetsLessCurrentLiabilities", nums[0], nums[1])
                rows.append(current_row)
                rows.append(previous_row)
                
        # Creditors after one year
        elif line == "Creditors: amounts falling due after more than one year":

            nums = extract_numeric_values(statement_lines, i + 1, required=2)

            if len(nums) >= 2:

                current_row, previous_row = add_concept("Creditors_After1Y", float(nums[0].replace(",", "")), float(nums[1].replace(",", "")))
                rows.append(current_row)
                rows.append(previous_row)
                
        # Net assets
        elif line == "Net assets attributable to members":

            nums = extract_numeric_values(statement_lines, i + 1, required=2)

            if len(nums) >= 2:
                current_row, previous_row = add_concept("NetAssetsLiabilities", nums[0], nums[1])
                rows.append(current_row)
                rows.append(previous_row)
                
                current_row, previous_row = add_concept("Equity_TotalEquity", nums[0], nums[1])
                rows.append(current_row)
                rows.append(previous_row)
                
        # Share capital
        elif line == "Members' capital classified as equity":

            nums = extract_numeric_values(statement_lines, i + 1, required=2)

            if len(nums) >= 2:

                current_row, previous_row = add_concept("Equity_ShareCapital", nums[0], nums[1])
                rows.append(current_row)
                rows.append(previous_row)
                
        # Revaluation reserve
        elif line == "Revaluation reserve":

            nums = extract_numeric_values(statement_lines, i + 1, required=2)

            if len(nums) >= 2:

                current_row, previous_row = add_concept("Equity_RevaluationReserve", nums[0], nums[1])
                rows.append(current_row)
                rows.append(previous_row)
    # ---------------------------------
    # Metadata
    # ---------------------------------

    text_blob = " ".join(lines)

    company_match = re.search(r"registration number\s+([A-Z]{0,2}\d{6,8})", text_blob, flags=re.I)

    if company_match:
        rows.append({
            "New_Name": "UKCompaniesHouseRegisteredNumber",
            "value": company_match.group(1),
            "period_mapped": "Current",
            "context": "rendered"
        })

    # Employee count
    employee_match = re.search(r"Employees.*?Number.*?Number.*?(\d+).*?(\d+)", text_blob, flags=re.S | re.I)

    if employee_match:

        current_row, previous_row = add_concept("AverageNumberEmployeesDuringPeriod", employee_match.group(1), employee_match.group(2))
        rows.append(current_row)
        rows.append(previous_row)
        
    return pd.DataFrame(rows)