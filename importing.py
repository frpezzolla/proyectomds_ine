import os
import pandas as pd
import logging
import coloredlogs

# Setup logging with colored output
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

def import_data():
    """
    Imports and concatenates yearly data from CSV files into a single Pandas DataFrame.

    This function reads CSV files for each year from 2010 to 2023, concatenates them
    into a single DataFrame, and logs the process. The data files are expected to be
    located in a 'data' directory within the current working directory.

    Returns:
        pd.DataFrame: A DataFrame containing the concatenated data from all years.
    """

    # Start with importing the data for the year 2010
    logger.info('Importing data for the year 2010')
    data = pd.read_csv(
        os.path.join(os.getcwd(), 'data', 'ano-2010.csv'),
        encoding='latin-1',
        sep=';'
    )

    # Loop through the years 2011 to 2023 and concatenate the data
    for year in range(11, 24):
        logger.info(f"Importing data for the year 20{year}")
        yearly_data = pd.read_csv(
            os.path.join(os.getcwd(), 'data', f'ano-20{year}.csv'),
            encoding='latin-1',
            sep=';'
        )
        data = pd.concat([data, yearly_data], ignore_index=True)

    return data

# The following function is commented out as it might be used in the future:
# def load_data():
#     """
#     Loads pre-saved data from a Parquet file.

#     This function reads a Parquet file containing all years' data into a Pandas DataFrame
#     and logs the process. The Parquet file is expected to be located in a 'data' directory
#     within the current working directory.

#     Returns:
#         pd.DataFrame: A DataFrame containing the loaded data.
#     """

#     logger.info('Loading data from todos-anos.parquet')
#     data = pd.read_parquet(
#         os.path.join(os.getcwd(), 'data', 'todos-anos.parquet')
#     )
    
#     return data

