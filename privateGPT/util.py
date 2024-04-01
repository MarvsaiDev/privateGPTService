import os
import logging as log
from typing import List

import pandas as pd
from langchain.docstore.document import Document

from privateGPT.env_config import EnvironmentConfig


def load_yaml_env():
    return EnvironmentConfig('settings.yaml')

    # Example: Access the environment variable
    # print(f"OPENAI_API_KEY: {os.environ.get('OPENAI_API_KEY')}")


def _extract_page_number_meta(s: Document) -> int:
    # Use regex to find the page number in the string
    page = s.metadata.get('page', None)
    if isinstance(page, int) or (isinstance(page, str) and page.isdigit()):
        # If a page number is found, return it as an integer
        return int(page)+1
    else:
        # If no page number is found, return a large number to sort this item last
        return -1
def prepare_dir(job_uuid, projpath='', rootdir='./'):
    error = None
    try:
        fullprojpath = job_uuid
        os.mkdir(fullprojpath)
    except Exception as e:
        error = str(e)
        log.info('ignoring base user directory if it exists' + str(fullprojpath))
    try:
        if projpath:
            fullprojpath = projpath + os.path.sep + job_uuid
            log.info('making sure user job directory exists')
            os.mkdir(fullprojpath)
    except Exception as e:
        error = str(e)
        log.error(str(e))
    finally:
        return fullprojpath, error

    import pandas as pd

def merge_or_return_larger(df1, df2):
    # Check if the two dataframes have the same shape
    if df1.shape[1] == df2.shape[1]:
        try:
            # Try to merge
            result = pd.concat([df1, df2], ignore_index=True)
            print("Dataframes are compatible and have been merged.")
        except ValueError:
            print("Dataframes are not compatible dimension-wise.")
            # Return the dataframe with the larger number of rows
            result = df1 if df1.size > df2.size else df2
    else:
        print("Dataframes do not have the same number of columns.")
        # Return the dataframe with the larger number of rows
        result = df1 if df1.size > df2.size else df2

    return result


def clean_df(df:pd.DataFrame, cols_array:List[str], PRICE_COL:int, has_subscription_date=False, total_from_quote:float=None):
    try:
        if PRICE_COL is None:
            return
        total_calc_value = -1
        df = df.dropna(subset=cols_array[PRICE_COL:PRICE_COL+1])
        df.fillna(0, inplace=True)
        df[cols_array[PRICE_COL]] = df[cols_array[PRICE_COL]].replace({'\$': '', ',': '', '\(': '-', '\)':''}, regex=True).astype(float)
        try:
            df[cols_array[PRICE_COL+1]] = df[cols_array[PRICE_COL+1]].replace({'\$': '', ',': '', '\(': '-', '\)':''}, regex=True).astype(float)
        except Exception as extended:
            log.warning('extended price is not numerical')

        if 'part' not in df.columns.values[0].lower():
            log.info('Sorting')
            df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0].replace(r'\D+', 0, regex=True))
            df = df.sort_values(df.columns[0])
        if has_subscription_date:
            subsIdx =  df.columns.tolist().index('Subscription End Date')
            added_comment = ''
            if len(df.columns)>subsIdx+1 and 'Quote' not in df.columns[subsIdx+1]:
                added_comment = ' ' +df.columns[subsIdx+1] + ' ' +df.iloc[:, subsIdx+1].replace(0, '')
            df['Description'] = df['Description'].replace(0, '')
            df['Description'] += ' Start: '+df['Subscription Start Date'].replace(0, '').astype(str) + ' End: '+ df['Subscription End Date'].replace(0, '').astype(str) + added_comment
        # If you want to add this total as a new row in your DataFrame:
        total_calc_value = df[cols_array[PRICE_COL+1]].sum()
        message = ''
        if total_from_quote:
            if total_calc_value==total_from_quote:
                message='OK'
            elif total_calc_value<total_from_quote-1:
                message='ERROR'
            else:
                message='WARNING'

        # df.loc['Total'] = pd.Series(total_calc_value, index=[cols_array[PRICE_COL+1]])
        # df.loc['Message'] = pd.Series(val, index=[cols_array[PRICE_COL]])
    except Exception as e:
        print('WARNING, UNABLE TO CLEAN on line:'+str(e.__traceback__.tb_lineno))
        log.warning('Clean error'+str(e.__traceback__.tb_lineno))
    return df, total_calc_value, message
