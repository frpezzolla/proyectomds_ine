import numpy as np
import os
import pandas as pd

data = {}

for year in range(10, 24):
    data[f'20{year}'] = pd.read_csv(
        os.path.join(
            'data',
            f'ano-20{year}.csv'), 
        encoding='latin-1',
        sep=';'
    )
