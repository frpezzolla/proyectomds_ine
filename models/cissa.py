import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.linalg import hankel, dft
from scipy.signal import lfilter
from scipy import stats
from spectrum import aryule

def build_groupings(period_ranges, data_per_unit_period, psd, z, include_noise=True):
    """
    Build groupings of frequencies for CiSSA components.

    Parameters:
    - period_ranges: dict, keys are group names, values are tuples (min_period, max_period)
    - data_per_unit_period: int, number of data points per unit period (e.g., 12 for monthly data)
    - psd: numpy array, power spectral density
    - z: numpy array, elementary reconstructed components by frequency
    - include_noise: bool, whether to include noise component

    Returns:
    - kg: dict, keys are group names, values are arrays of frequency indices
    """
    L = len(psd)
    T, F = z.shape

    if L % data_per_unit_period != 0:
        raise ValueError(f'L must be proportional to the number of data per unit period. Got L % data_per_unit_period = {L % data_per_unit_period}')

    kg = {}
    min_k = L
    s = data_per_unit_period

    for key_p, value_p in period_ranges.items():
        if value_p[0] == value_p[1]:
            myarray = L * np.arange(1, np.floor(s / 2) + 1) / (value_p[0] * s)
            kg[key_p] = myarray.astype(int)
            min_k = min(min_k, myarray.min())
        else:
            myarray = np.arange(
                max(1, np.floor(L / (value_p[1] * s) + 1)) - 1,
                min(F - 1, np.floor(L / (value_p[0] * s) + 1)),
                dtype=int
            )
            kg[key_p] = myarray
            min_k = min(min_k, myarray.min())

    kg['trend'] = np.arange(0, int(min_k))

    if include_noise:
        current_k = np.concatenate([kg[key] for key in kg])
        missing_k = np.setdiff1d(np.arange(0, int(np.floor(L / 2))), current_k)
        kg['noise'] = missing_k

    return kg

def diagaver_single_thread(Y):
    """
    Perform diagonal averaging for SSA.

    Parameters:
    - Y: numpy 2D array, trajectory matrix

    Returns:
    - y: numpy array, reconstructed time series
    """
    LL, NN = Y.shape
    if LL > NN:
        Y = Y.transpose()
    L = min(LL, NN)
    N = max(LL, NN)
    T = N + L - 1
    y = np.zeros((T, 1))

    for t in range(1, T + 1):
        if 1 <= t <= L - 1:
            j_inf = 1
            j_sup = t
        elif L <= t <= N:
            j_inf = 1
            j_sup = L
        else:
            j_inf = t - N + 1
            j_sup = T - N + 1
        nsum = j_sup - j_inf + 1
        for m in range(j_inf, j_sup + 1):
            y[t - 1] += Y[m - 1, t - m] / nsum

    return y

def extend(x, H):
    """
    Extend time series for SSA.

    Parameters:
    - x: numpy array, original time series
    - H: int, extension parameter

    Returns:
    - xe: numpy array, extended time series
    """
    T = len(x)
    if H == 0:
        xe = x.copy()
    elif H == T:
        xe = np.concatenate([np.flipud(x), x, np.flipud(x)])
    else:
        p = int(np.fix(T / 3))
        dx = np.diff(x, axis=0)
        A, _, _ = aryule(dx.flatten(), p)
        y = x.copy()
        dy = np.diff(y, axis=0)
        er = lfilter(np.append(1, A), 1, dy.flatten())
        dy = lfilter([1], np.append(1, A), np.concatenate([er, np.zeros(H)]))
        y = y[0] + np.concatenate([0], np.cumsum(dy))
        y = np.flipud(y)
        dy = np.diff(y, axis=0)
        er = lfilter(np.append(1, A), 1, dy.flatten())
        dy = lfilter([1], np.append(1, A), np.concatenate([er, np.zeros(H)]))
        y = y[0] + np.concatenate([0], np.cumsum(dy))
        xe = np.flipud(y)
    return xe.reshape(-1, 1)

def group(Z, psd, I, season_length=1, cycle_length=[1.5, 8], include_noise=True):
    """
    Group reconstructed components by frequency.

    Parameters:
    - Z: numpy array, reconstructed components by frequency
    - psd: numpy array, power spectral density
    - I: int or dict, grouping instructions
    - season_length: int, length of the season in years
    - cycle_length: list, cycle periods
    - include_noise: bool, whether to include noise component

    Returns:
    - rc: dict, reconstructed components
    - sh: dict, share of psd for each group
    - kg: dict, indices of frequencies for each group
    """
    T, F = Z.shape
    L = len(psd)

    if isinstance(I, int) and I > 0:
        s = I
        kg = {}
        kg['seasonality'] = (L * np.arange(1, np.floor(s / 2) + 1) / (season_length * s)).astype(int)
        kg['long term cycle'] = np.arange(
            max(1, int(np.floor(L / (cycle_length[1] * s) + 1)) - 1),
            min(F - 1, int(np.floor(L / (cycle_length[0] * s) + 1))),
            dtype=int
        )
        kg['trend'] = np.arange(0, kg['long term cycle'][0])

        if include_noise:
            current_k = np.concatenate([kg[key] for key in kg])
            missing_k = np.setdiff1d(np.arange(0, int(np.floor(L / 2))), current_k)
            kg['noise'] = missing_k
    else:
        raise ValueError("Invalid value for I. Expected a positive integer.")

    if L % 2:
        pzz = np.concatenate([psd[0:1], 2 * psd[1:F]])
    else:
        pzz = np.concatenate([psd[0:1], 2 * psd[1:F - 1], psd[F - 1:F]])

    rc = {}
    sh = {}
    for key in kg:
        idx = kg[key]
        rc[key] = Z[:, idx].sum(axis=1, keepdims=True)
        sh[key] = 100 * pzz[idx].sum() / pzz.sum()

    return rc, sh, kg

def cissa(x, L, H=0):
    """
    Perform Circulant Singular Spectrum Analysis (CiSSA).

    Parameters:
    - x: numpy array, original time series
    - L: int, window length
    - H: int, extension parameter

    Returns:
    - Z: numpy array, reconstructed components by frequency
    - psd: numpy array, power spectral density
    """
    T = len(x)
    N = T - L + 1
    if L >= N:
        raise ValueError(f'The window length must be less than T/2. Got L = {L}, T = {T}')

    if H == 1:
        H = T
    elif H == 2:
        H = 0
    else:
        H = L

    if L % 2:
        nf2 = (L + 1) / 2 - 1
    else:
        nf2 = L / 2 - 1
    nft = nf2 + abs(L % 2 - 2)

    xe = extend(x, H)
    col = xe[0:L]
    row = xe[L - 1:]
    X = hankel(col, row)

    gam = np.array([np.dot((x[0:T - k] - x.mean()).T, (x[k:T] - x.mean())) / (T - k) for k in range(L)])
    S = gam[0] * np.eye(L)
    C = S.copy()
    for i in range(L):
        for j in range(i + 1, L):
            k = abs(i - j)
            S[i, j] = gam[k]
            S[j, i] = S[i, j]
            C[i, j] = ((L - k) / L) * gam[k] + (k / L) * gam[L - k]
            C[j, i] = C[i, j]

    U = dft(L) / np.sqrt(L)
    U[:, 0] = np.real(U[:, 0])

    for k in range(1, int(nf2) + 1):
        u_k = U[:, k]
        U[:, k] = np.sqrt(2) * np.real(u_k)
        U[:, L - k] = np.sqrt(2) * np.imag(u_k)
    U = np.real(U)

    if L % 2 == 0:
        U[:, int(nft - 1)] = np.real(U[:, int(nft - 1)])

    psd = np.abs(np.diag(U.T @ C @ U))
    W = U.T @ X

    R = np.zeros((T + 2 * H, L))
    for k in range(L):
        R[:, k:k + 1] = diagaver_single_thread((U[:, k:k + 1] @ W[k:k + 1, :]))

    Z = np.zeros((T + 2 * H, int(nft)))
    Z[:, 0:1] = R[:, 0:1]
    for k in range(1, int(nf2) + 1):
        Z[:, k:k + 1] = R[:, k:k + 1] + R[:, L - k:L - k + 1]
    if L % 2 == 0:
        Z[:, int(nft - 1):int(nft)] = R[:, int(nft - 1):int(nft)]

    Z = Z[H:T + H, :]
    psd = psd.reshape(-1, 1)
    return Z, psd

def get_cissa(series, L=12, use_max_L=True):
    """
    Perform CiSSA decomposition with dynamic window length adjustment.

    Parameters:
    - series: pandas Series, input time series
    - L: int, window length (multiple of 12)
    - use_max_L: bool, whether to adjust L to maximum possible value

    Returns:
    - rc: dict, reconstructed components
    - sh: dict, share of psd for each group
    - kg: dict, indices of frequencies for each group
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
    Z, psd = cissa(series.values, L)
    data_per_year = 12
    rc, sh, kg = group(Z, psd, data_per_year)

    return rc, sh, kg

def plot_cissa(series, L=12):
    """
    Visualize the components of CiSSA decomposition for a given time series.

    Parameters:
    - series: pandas Series, input time series
    - L: int, window length (multiple of 12)

    Returns:
    - None
    """
    rc, _, _ = get_cissa(series, L=L)

    fig, axs = plt.subplots(5, 1, figsize=(10, 12), sharex=True)

    axs[0].plot(series.index, rc['trend'], 'b', lw=1.0, label='Trend')
    axs[0].set_ylabel('Trend')
    axs[0].set_title(f'CiSSA Decomposition (L = {L // 12} years)')
    axs[0].legend()

    axs[1].plot(series.index, rc['seasonality'], 'g', lw=1.0, label='Seasonality')
    axs[1].set_ylabel('Seasonality')
    axs[1].legend()

    axs[2].plot(series.index, rc['long term cycle'], 'r', lw=1.0, label='Long Term Cycle')
    axs[2].set_ylabel('Long Term Cycle')
    axs[2].legend()

    axs[3].plot(series.index, rc['noise'], 'k', lw=1.0, label='Noise')
    axs[3].set_ylabel('Noise')
    axs[3].set_xlabel('Date')
    axs[3].legend()

    axs[4].plot(series.index, series, label='Original Series')
    axs[4].set_ylabel('Value')
    axs[4].legend()

    plt.tight_layout()
    plt.show()

# Example usage (this would be in main.py or another script)
if __name__ == "__main__":
    # Load your data here
    data = pd.read_excel(io="your_data.xlsx")
    # Preprocess data as required
    series = data['your_series_column']
    plot_cissa(series, L=12)
