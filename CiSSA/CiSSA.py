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
    """
    Converts the 'Año' and 'Trimestre' columns into a datetime index.

    Parameters
    ----------
    data : pandas.DataFrame
        The DataFrame containing columns 'Año' (year) and 'Trimestre' (quarter).
        Assumes that the year and quarter columns are at the top level of 
        a MultiIndex column structure.

    Returns
    -------
    pandas.DataFrame
        DataFrame with a new 'Date' column converted to a DateTime index.
        The original 'Año' and 'Trimestre' columns are dropped, and the
        DataFrame is sorted by the new Date index.

    Notes
    -----
    - The function remaps quarter names (e.g., 'Dic - Feb') into an integer 
      code for easier conversion to datetime.
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
    
    This function applies CiSSA to decompose the input `series` into its 
    reconstructed components, such as trend, seasonality, long-term cycles, 
    and noise. The window length `L` can be manually set, or it can be 
    dynamically adjusted to half the length of the time series minus one 
    (`T/2 - 1`), ensuring that `L` is a multiple of 12.

    Parameters
    ----------
    series : pandas Series or numpy array
        The input time series data to decompose.
    L : int, optional
        The window length for CiSSA decomposition. Default is 12.
    use_max_L : bool, optional
        If True, sets `L` to the maximum allowable value based on the length 
        of the time series, calculated as `(T/2 - 1)//12 * 12`. Default is False.
    
    Raises
    ------
    ValueError
        If `L` is greater than or equal to half the length of the series.
    
    Warnings
    --------
    UserWarning
        If `L` is not a multiple of 12, a warning is issued and the function 
        returns without performing the computation.
    
    Returns
    -------
    rc : dict
        A dictionary containing the reconstructed components from CiSSA, 
        such as trend, seasonality, long-term cycles, and noise.
    
    Example Usage
    -------------
    >>> result = get_cissa(my_series, L=24, use_max_L=True)
    >>> trend = result['trend']
    """
    
    T = series.shape[0]

    if use_max_L:
        L = (T//2 - 1)//12 * 12
    
    else:
        if L % 12 != 0:
            raise ValueError("L must be a multiple of 12")
        if L >= T:
            raise ValueError(f"The window length must be less than T/2. Currently L = {L}, T = {T}")
    
    print(f"Computing CiSSA for L={L}")
    Z, psd = cissa(series, L, multi_thread_run=False)
    data_per_year = 12
    rc, sh, kg = group(Z, psd, data_per_year)
    
    return rc


# Plot CiSSA components
def plot_cissa(series, L=12):
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
    rc = get_cissa(series, L=L, force_cissa=False)
    
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
    plot_cissa(tasa, L=12)
