import numpy as np
import os
import pandas as pd

#%%
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

#%%

def import_data():
    data = {}
    
    # for year in range(10, 24):
    #     data[f'20{year}'] = pd.read_csv(
    #         os.path.join(
    #             'data',
    #             f'ano-20{year}.csv'), 
    #         encoding='latin-1',
    #         sep=';'
    #     )
    
    logger.info('importing year 2010')
    data = pd.read_csv(
        os.path.join(
            os.getcwd(),
            'data',
            f'ano-20{10}.csv'),
        encoding='latin-1',
        sep=';'
        )
    
    for year in range(11, 24):
        logger.info(f"importing year 20{year}")
        data = pd.concat([data, 
                    pd.read_csv(                    
                        os.path.join(
                            os.getcwd(),
                            'data',
                            f'ano-20{year}.csv'), 
                        encoding='latin-1',
                        sep=';'
        )])
    
    # logger.info('saving to todos-anos.csv')    
    # data.to_parquet('todos-anos.parquet', compression='snappy')
    
    return data
    
# def load_data():
    
#     logger.info('loading todos-anos.csv')
    
#     data = pd.read_parquet(
#         os.path.join(
#             os.getcwd(),
#             'data',
#             'todos-anos.csv'),
#         encoding='latin-1',
#         sep=','
#         )
    
#     return data

#%%