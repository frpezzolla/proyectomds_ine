"""
CiSSA Decomposition and Visualization of Time Series Data

This script performs the following steps:

1. **Data Loading and Preprocessing**:
   - Reads a historical dataset from an Excel file.
   - Reformats columns and indexes to create a time-indexed DataFrame.
   - Converts "Trimestre" and "Año" columns into a proper date index for use
     in time series analysis.

2. **Time Series Decomposition using CiSSA**:
   - Extracts a specific time series from the dataset.
   - Applies Circulant Singular Spectrum Analysis (CiSSA) to decompose the
     series into components: Trend, Seasonality, Long Term Cycle, and Noise.

3. **Visualization**:
   - Creates a figure with five subplots to visualize each component of the
     decomposition and the original time series.
   - Each subplot corresponds to:
     - `trend`: Long-term progression.
     - `seasonality`: Recurring patterns.
     - `long term cycle`: Longer cyclic behavior.
     - `noise`: Random fluctuations.
     - Original series: Full series before decomposition.

4. **Parameters**:
   - `L`: Window length for CiSSA, determining the series portion used for
     analyzing each component.
   - `data_per_year`: Data points per year, defining seasonal patterns.

5. **Usage**:
   - Execute the script to load data, perform decomposition, and plot results.
   - Adjust `L` to explore effects on decomposition.

6. **Dependencies**:
   - `pandas`: Data manipulation.
   - `matplotlib.pyplot`: Plotting.
   - `numpy`: Numerical operations.
   - `pycissa`: CiSSA decomposition functions.

This script aids in exploring time series components: trend, cycles, and noise.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pycissa import cissa, group

# Function to convert date columns to index
def date_to_index(data):
    df = data.copy()
    trim_date = dict(zip(df[("Trimestre", np.nan)].unique(), (np.arange(12, 0, -1) - 7) % 12 + 1001))
    trim_date = {k: str(v).replace("100", "0").replace("101", "1") for k, v in trim_date.items()}
    df[("Trimestre", np.nan)] = df[("Trimestre", np.nan)].apply(lambda trim: trim_date[trim])
    df["Date"] = df[["Año", "Trimestre"]].agg(lambda row: "-".join(row.astype("string")) + "-01", axis=1)
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
    df.index = df["Date"]
    df.drop(columns=[("Año", np.nan), ("Trimestre", np.nan), ("Date", "")], inplace=True)
    df.sort_index(inplace=True)
    return df

# Load and preprocess data
data = pd.read_excel(io="../data/ine/ajuste_estacional_historico.xlsx", sheet_name="tasa_as")
data = data.loc[3:172]
data.columns = pd.MultiIndex.from_arrays(data.iloc[0:2].to_numpy())
data = data.loc[6:].reset_index(drop=True)
data = date_to_index(data=data)

# Flatten column names for easier access
pdata = data.copy()
pdata.columns = pd.Index(map(str.strip, pdata.columns.get_level_values(0) + " " + pdata.columns.get_level_values(1)))

# Extract the specific column for analysis
tasa = pdata["Tasa ajustada MJJ2024"]

if __name__ == '__main__':
    # Set window length
    L = 12  # Window length for CiSSA decomposition
    data_per_year = 12
    
    # Apply CiSSA decomposition
    Z, psd = cissa(tasa, L, multi_thread_run=False)
    rc, sh, kg = group(Z, psd, data_per_year)
    
    # Create subplot to visualize each component
    fig, axs = plt.subplots(5, 1, figsize=(10, 12), sharex=True)
    
    # Plot each component
    axs[0].plot(tasa.index, rc['trend'], 'b', lw=1.0, label='trend')
    axs[0].set_ylabel('Trend')
    axs[0].set_title(f'L = {L // 12} años')
    axs[0].legend()
    
    axs[1].plot(tasa.index, rc['seasonality'], 'g', lw=1.0, label='seasonality')
    axs[1].set_ylabel('Seasonality')
    axs[1].legend()
    
    axs[2].plot(tasa.index, rc['long term cycle'], 'r', lw=1.0, label='long term cycle')
    axs[2].set_ylabel('Long Term Cycle')
    axs[2].legend()
    
    axs[3].plot(tasa.index, rc['noise'], 'k', lw=1.0, label='noise')
    axs[3].set_ylabel('Noise')
    axs[3].set_xlabel('Date')
    axs[3].legend()
    
    axs[4].plot(tasa.index, tasa, label='Tasa ajustada MJJ2024')
    axs[4].set_ylabel('Tasa')
    axs[4].legend()
    
    plt.tight_layout()
    plt.show()