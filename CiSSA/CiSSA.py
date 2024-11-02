"""
CiSSA Decomposition and Visualization of Time Series Data

This script performs the following tasks:

[Your original description here]
"""

import os
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

# Handle import compatibility when run as a standalone script
if __name__ == "__main__":
    import sys
    from pathlib import Path
    # Add the package's root directory to sys.path for standalone execution
    sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from .pycissa import cissa, group  # Relative import when used as part of the package
except ImportError:
    from pycissa import cissa, group   # Absolute import for standalone usage


def date_to_index(data):
    """
    Converts the 'Año' and 'Trimestre' columns into a datetime index.
    [Function docstring remains the same]
    """
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

def get_cissa(series, L=12, use_max_L=True):
    """
    Perform Circulant Singular Spectrum Analysis (CiSSA) decomposition on the 
    input time series with dynamic window length adjustment.
    [Function docstring remains the same]
    """
    T = series.shape[0]

    if use_max_L:
        L = (T // 2 - 1) // 12 * 12
    else:
        if L % 12 != 0:
            raise ValueError("L must be a multiple of 12")
        if L >= T:
            raise ValueError(f"The window length must be less than T/2. Currently L = {L}, T = {T}")
    
    print(f"Computing CiSSA for L={L}")
    Z, psd = cissa(series, L, multi_thread_run=False)
    data_per_year = 12
    rc, sh, kg = group(Z, psd, data_per_year)
    
    return rc, sh, kg


# Plot CiSSA components
def plot_cissa(series, L=12):
    """
    Visualize the components of CiSSA decomposition for a given time series.
    [Function docstring remains the same]
    """
    rc, _, _ = get_cissa(series, L=L)
    
    fig, axs = plt.subplots(5, 1, figsize=(10, 12), sharex=True)
    
    axs[0].plot(series.index, rc['trend'], 'b', lw=1.0, label='trend')
    axs[0].set_ylabel('Trend')
    axs[0].set_title(f'L = {L // 12} años')
    axs[0].legend()
    
    axs[1].plot(series.index, rc['seasonality'], 'g', lw=1.0, label='seasonality')
    axs[1].set_ylabel('Seasonality')
    axs[1].legend()
    
    axs[2].plot(series.index, rc['long term cycle'], 'r', lw=1.0, label='long term cycle')
    axs[2].set_ylabel('Long Term Cycle')
    axs[2].legend()
    
    axs[3].plot(series.index, rc['noise'], 'k', lw=1.0, label='noise')
    axs[3].set_ylabel('Noise')
    axs[3].set_xlabel('Date')
    axs[3].legend()
    
    axs[4].plot(series.index, series, label='Tasa ajustada MJJ2024')
    axs[4].set_ylabel('Tasa')
    axs[4].legend()
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Example data load and function calls if running this script directly
    data = pd.read_excel(io="../data/ine/ajuste_estacional_historico.xlsx", sheet_name="tasa_as")
    data = data.loc[3:172]
    data.columns = pd.MultiIndex.from_arrays(data.iloc[0:2].to_numpy())
    data = data.loc[6:].reset_index(drop=True)
    data = date_to_index(data=data)

    pdata = data.copy()
    pdata.columns = pd.Index(map(str.strip, pdata.columns.get_level_values(0) + " " + pdata.columns.get_level_values(1)))

    tasa = pdata["Tasa ajustada MJJ2024"]
    plot_cissa(tasa, L=12)
