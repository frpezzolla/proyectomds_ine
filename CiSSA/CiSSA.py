"""
CiSSA Decomposition and Visualization of Time Series Data

This script performs the following tasks:

1. **Data Loading and Preprocessing**:
   - Loads historical time series data from an Excel file.
   - Converts "Trimestre" (quarter) and "Año" (year) columns into a time-indexed DataFrame.
   - Reformats columns and sets a proper date index for time series analysis.

2. **Time Series Decomposition using CiSSA**:
   - Extracts a specified time series column for analysis.
   - Applies Circulant Singular Spectrum Analysis (CiSSA) to decompose the time series.
   - Decomposes the series into key components such as:
     - Trend: Represents the long-term progression.
     - Seasonality: Recurring seasonal patterns.
     - Long-term cycle: Captures longer cyclic behavior.
     - Noise: Random fluctuations.

3. **Caching of CiSSA Results**:
   - The results of the CiSSA decomposition are saved to a file to avoid recomputation.
   - If `force_cissa` is set to `True`, CiSSA is run again regardless of any cached results.
   - If `force_cissa` is `False`, the function first checks for existing saved results to load.

4. **Visualization**:
   - Generates a plot consisting of five subplots, each representing a component of the decomposition:
     - Trend
     - Seasonality
     - Long-term cycle
     - Noise
     - The original series (Tasa ajustada MJJ2024)

5. **Parameters**:
   - `L`: Window length for CiSSA decomposition (can be adjusted to observe the effects on the components).
   - `force_cissa`: Boolean flag to force recalculation of CiSSA or load from cache.

6. **Usage**:
   - Adjust the window length `L` and call the script to load the data, perform CiSSA decomposition, and visualize the results.
   - Run `plot_cissa()` to visualize the components of the decomposed time series.

7. **Dependencies**:
   - `pandas`: For data manipulation and preprocessing.
   - `matplotlib.pyplot`: For visualizing the components of the time series.
   - `numpy`: For numerical operations.
   - `pycissa`: Provides the CiSSA decomposition functions.
   - `pickle`: To save and load CiSSA results.

This script is useful for analyzing the key components of a time series (trend, seasonality, cycles, and noise) and facilitates understanding of the data's temporal structure.
"""
import os
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pycissa import cissa, group

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

def get_cissa(L=12, force_cissa=False):
    """
    Perform CiSSA decomposition on a time series and optionally load or save results.

    Parameters
    ----------
    L : int, optional
        The window length for CiSSA decomposition, by default 12.
        Affects the size of the portion of the series used for analyzing
        each component.
        
    force_cissa : bool, optional
        If `True`, forces the computation of CiSSA and saves the result to a file
        regardless of whether a precomputed result exists. If `False`, it first
        checks if a previous result file exists and loads it. If no such file
        is found, it performs the CiSSA decomposition and saves the result.
        By default False.

    Returns
    -------
    rc : dict
        A dictionary containing the components of the decomposed time series,
        such as 'trend', 'seasonality', 'long term cycle', and 'noise'.
        
    Notes
    -----
    - The results of the decomposition are saved as a pickle file named 
      `cissa_L{L}.pkl`, where `L` is the value of the window length.
    - This function checks for existing files to avoid redundant computation,
      thus speeding up analysis when working with large datasets.
    - If force_cissa is True, it will recompute CiSSA and overwrite any 
      existing result file.

    Examples
    --------
    To compute and store the CiSSA results for L=12:
    >>> rc_L12 = get_cissa(L=12, force_cissa=True)

    To load previously computed results if they exist:
    >>> rc_L12 = get_cissa(L=12, force_cissa=False)
    """   
    filename = f"cissa_L{L}.pkl"
    if not force_cissa and os.path.exists(filename):
        print(f"Loading precomputed CiSSA result from {filename}")
        with open(filename, 'rb') as file:
            rc = pickle.load(file)
        return rc
    
    print(f"Computing CiSSA for L={L}")
    Z, psd = cissa(tasa, L, multi_thread_run=False)
    data_per_year = 12
    rc, sh, kg = group(Z, psd, data_per_year)
    
    with open(filename, 'wb') as file:
        pickle.dump(rc, file)
    print(f"Saved CiSSA result to {filename}")
    return rc

# Plot CiSSA components
def plot_cissa(L=12):
    """
    Visualize the components of CiSSA decomposition for a given time series.

    Parameters
    ----------
    L : int, optional
        The window length for CiSSA decomposition, by default 12. 
        Affects the granularity of the decomposition into trend, seasonality,
        long-term cycle, and noise components.

    Notes
    -----
    - The function retrieves the decomposed components from `get_cissa()`.
    - It creates a figure with five subplots:
        1. Trend component
        2. Seasonality component
        3. Long-term cycle
        4. Noise
        5. Original time series
    - All components share the same x-axis (date index).
    
    Example
    -------
    To plot CiSSA decomposition with a window length of 72:
    >>> plot_cissa(L=72)
    """
    rc = get_cissa(L=L, force_cissa=False)
    
    fig, axs = plt.subplots(5, 1, figsize=(10, 12), sharex=True)
    
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

# Load and preprocess data
data = pd.read_excel(io="../data/ine/ajuste_estacional_historico.xlsx", sheet_name="tasa_as")
data = data.loc[3:172]
data.columns = pd.MultiIndex.from_arrays(data.iloc[0:2].to_numpy())
data = data.loc[6:].reset_index(drop=True)
data = date_to_index(data=data)

pdata = data.copy()
pdata.columns = pd.Index(map(str.strip, pdata.columns.get_level_values(0) + " " + pdata.columns.get_level_values(1)))

tasa = pdata["Tasa ajustada MJJ2024"]

if __name__ == '__main__':
    plot_cissa(L=12)
