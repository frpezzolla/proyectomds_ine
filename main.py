import argparse
import logging
import os
import sys
import shlex
from pathlib import Path
import warnings
import traceback

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from models.x13_model import X13Model
from models.stl import STLModel
from models.cissa import CiSSAModel

from utils.setup_logging import setup as setup_logging
from utils.diagnose import Diagnose

def apply_x13(series, verbose=False):
    """Apply X13-ARIMA-SEATS decomposition to the provided series."""
    if verbose:
        logging.info("Applying X13 decomposition...")
    try:
        x13_model = X13Model()
        x13_model.fit(series)
        series_adj = x13_model.adjust()
        #deseasonalised_series = pd.Series(series_adj, index=series.index)
        return series_adj.seasadj
    except Exception as e:
        logging.error(f"X13 decomposition failed: {e}")
        return None

def apply_stl(series, verbose=False):
    """Apply STL decomposition to the provided series.
    series: 1D series, datetime index"""
    # DONE: Implement STL decomposition and return the trend component
    if verbose:
        logging.info("Applying STL decomposition...")
    try:
        stl_model = STLModel()
        stl_model.fit(series)
        series_adj = stl_model.adjust()
        #deseasonalised_series = pd.Series(series_adj, index=series.index)
        return series_adj.seasadj
    except Exception as e:
        logging.error(f"STL decomposition failed: {e}")
        return None

def apply_cissa(series, verbose=False, save_decomposition=True):
    """Apply CiSSA decomposition to the provided series."""
    if verbose:
        logging.info("Applying CiSSA decomposition...")
    try:
        cissa_model = CiSSAModel()
        cissa_model.fit(series).adjust()
        return cissa_model.seasadj
    except Exception as e:
        logging.error(f"CiSSA decomposition failed: {e}")
        return None

def import_data(file_dir):
    try:
        data = pd.read_csv(file_dir)
        data['date'] = pd.to_datetime(data['ano'].astype(str) + '-' + data['mes'].astype(str) + '-01')
        data.set_index('date', inplace=True)
        data.drop(['ano', 'mes'], axis=1, inplace=True)
        logging.info("Data imported successfully.")
    except (FileNotFoundError, pd.errors.ParserError, ValueError) as e:
        logging.error(f"Error reading input file: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading the input file: {e}")
        sys.exit(1)
    return data


def plot_series(original_series, trend_series, method_name, output_dir, usetex=False):
    """Plot the original and trend series."""
    if usetex:
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')
        matplotlib.rcParams.update({'font.size': 14})

    plt.figure(figsize=(10, 6))
    plt.plot(original_series.index, original_series, label='Original')
    plt.plot(trend_series.index, trend_series, label=f'Trend ({method_name})')
    plt.title(f'{method_name} Decomposition')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plot_filename = os.path.join(output_dir, f'{method_name}_decomposition.png')
    plt.savefig(plot_filename)
    plt.close()
    logging.info(f"Plot saved to {plot_filename}")

def main(args):

    logging.info("Starting the STD process...")
    
    if not os.path.isfile(args.input):
        logging.error(f"Input file '{args.input}' does not exist.")
        sys.exit(1)
        
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.plot_dir, exist_ok=True)
    os.makedirs(args.log_dir, exist_ok=True)

    # =========================================================================
    # IMPORT DATA
    # =========================================================================
    
    data = import_data(args.input)

    # =========================================================================
    # APPLY STD METHODS
    # =========================================================================
    
    deseasonalised_series = {}
    
    if args.x13:
        logging.info("Applying X13-ARIMA-SEATS decomposition...")
        try:
            for series in data.columns:
                logging.info(f"Starting X13 decomposition for series {series}")
                deseasonalised_series[series+'_std'] = apply_x13(data[series])
        except Exception as e:
            logging.error(f"X13 decomposition failed: {e}")

    if args.stl:
        logging.info("Applying STL decomposition...")
        try:
            for series in data.columns:
                logging.info(f"Starting STL decomposition for series {series}")
                deseasonalised_series[series+'_std'] = apply_stl(data[series])
        except Exception as e:
            logging.error(f"STL decomposition failed: {e}")

    if args.cissa:
        logging.info("Applying CiSSA decomposition...")
        try:
            for series in data.columns:
                logging.info(f"Starting CiSSA decomposition for series {series}")
                deseasonalised_series[series+'_std'] = apply_cissa(data[series])
        except Exception as e:
            logging.error(f"CiSSA decomposition failed: {e}")
            
    deseasonalised_df = pd.DataFrame(deseasonalised_series)
    
    results = pd.concat([data, deseasonalised_df], axis=1)
    print(results.head())

    # =========================================================================
    # RUN DIAGNOSTICS
    # =========================================================================

    if args.diagnose:
        tasa = pd.read_csv("./data/endogena/to202406.csv")
        tasa.index = pd.DatetimeIndex(tasa.pop('ds'))
        tasa = tasa['to']

        outlier_serie = pd.Series(pd.date_range(start='2020-01-01', end='2022-05-01', freq='MS'))
        outlier_serie.index = pd.DatetimeIndex(outlier_serie)
        outlier_serie.loc[:] = 1
        diag = Diagnose(tasa)
        diag.set_outlier(outlier_serie)
        # X13
        if args.x13:
            try:
                diag.outlier_diags(X13Model)
            except Exception as e:
                warnings.warn(traceback.format_exc())

        # STL
        if args.stl:
            try:
                diag.outlier_diags(STLModel)
            except Exception as e:
                warnings.warn(traceback.format_exc())

        # CISSA
        if args.cissa:
            try:
                diag.outlier_diags(CiSSAModel)
            except Exception as e:
                warnings.warn(traceback.format_exc())

    # =========================================================================
    # CALCULATE UNEMPLOYMENT RATES
    # =========================================================================

    results = data.copy()[['dh15', 'dm15', 'dh25', 'dm25', 'oh15', 'om15', 'oh25', 'om25']]
    for sex in ['h', 'm']:
        for age_group in ['15', '25']:
            
            unoccupied_original = data[f'd{sex}{age_group}']
            occupied_original = data[f'o{sex}{age_group}']
            results[f'{sex}{age_group}'] = unoccupied_original / (occupied_original + unoccupied_original)
            
            unoccupied_deseasonalised = deseasonalised_series[f'd{sex}{age_group}']
            occupied_deseasonalised = deseasonalised_series[f'o{sex}{age_group}']
            results[f'{sex}{age_group}_deseasonalised'] = unoccupied_deseasonalised / (occupied_deseasonalised + unoccupied_deseasonalised)
    
    # =========================================================================
    # PLOTTING
    # =========================================================================
    
    import matplotlib.pyplot as plt
    
    model_name = 'x13' if args.x13 else 'stl' if args.stl else 'cissa'
    
    col_meaning = {'dh15': 'desocupados hombres 15 a 24', 
                'dm15': 'desocupados mujeres 15 a 24', 
                'dh25': 'desocupados hombres 25 o más', 
                'dm25': 'desocupados mujeres 25 o más', 
                'oh15': 'ocupados hombres 15 a 24', 
                'om15': 'ocupados mujeres 15 a 24', 
                'oh25': 'ocupados hombres 25 o más', 
                'om25': 'ocupados mujeres 25 o más',
                'desocupados': 'total desocupados', 
                'ocupados': 'total ocupados', 
                'dh': 'desocupados hombres', 
                'dm': 'desocupados mujeres', 
                'oh': 'ocupados hombres', 
                'om': 'ocupados mujeres', 
                'ft_h': 'fuerza de trabajo hombres', 
                'ft_m': 'fuerza de trabajo mujeres', 
                'ft': 'fuerza de trabajo total',
                'td_h': 'total desocupados hombres',
                'td_m': 'total desocupados mujeres', 
                'td': 'total desocupados'}
    
    for series in data.columns:
        plt.figure(figsize=(6,4))
        plt.title(f'{col_meaning[series]} -- {model_name}')
        plt.plot(results[series], label='oficial', lw=1)
        plt.plot(results[series+'_std'], label='desestacionalizada', lw=1)
        plt.xlabel('date')
        plt.ylabel('rate')
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.savefig(f'./outputs/graphs/{series}.pdf', bbox_inches='tight')
        plt.show()
    
    # =========================================================================
    # SAVE RESULTS
    # =========================================================================

    output_file = os.path.join(args.output_dir, args.output)
    try:
        results.to_csv(output_file)
        logging.info(f"Results saved to {output_file}")
    except Exception as e:
        logging.error(f"Error saving results: {e}")
        sys.exit(1)

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(
        description="Process employment data with optional X13, STL, and CiSSA methods."
    )
    parser.add_argument('-i', '--input', type=str, required=True, help='Input CSV file path')
    parser.add_argument('-o', '--output', type=str, default='results.csv', help='Output CSV file name')
    parser.add_argument('--output_dir', type=str, default='outputs', help='Output directory')
    parser.add_argument('--plot_dir', type=str, default='plots', help='Directory to save plots')
    parser.add_argument('--log_dir', type=str, default='logs', help='Directory to save logs')
    parser.add_argument('--x13', action='store_true', default=False, help='Apply X13-ARIMA-SEATS decomposition')
    parser.add_argument('--stl', action='store_true', default=False, help='Apply STL decomposition')
    parser.add_argument('--cissa', action='store_true', default=False, help='Apply CiSSA decomposition')
    parser.add_argument('-d', '--diagnose', action='store_true', default=False, help='Apply Diagnostics for every model of interest')
    parser.add_argument('--plot', action='store_true', help='Generate plots')
    parser.add_argument('--usetex', action='store_true', help='Use LaTeX for plot fonts')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--loglevel', type=str, default='INFO', help='Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--logfile', type=str, default='', help='Log file name (if empty, logs to console)')

    # Read arguments from 'arguments.txt' if it exists
    args_list = []
    if os.path.isfile('arguments.txt'):
        try:
            with open('arguments.txt', 'r') as f:
                arg_str = f.read()
                args_list = shlex.split(arg_str)
                logging.info("Arguments read from 'arguments.txt'")
        except Exception as e:
            logging.error(f"Error reading arguments from file: {e}")
            sys.exit(1)
    else:
        logging.info("'arguments.txt' not found. Proceeding with command-line arguments.")

    # Combine arguments from the file with any command-line arguments
    # Command-line arguments take precedence
    combined_args = args_list + sys.argv[1:]

    # Parse the combined arguments
    # Use parse_known_args to avoid issues with unknown arguments
    args, unknown = parser.parse_known_args(combined_args)

    # Now that we have args, we can set up logging properly
    # setup_logging(args.loglevel, args.logfile)
    logging.info("Logging is configured.")

    # If there are unknown arguments, log a warning
    if unknown:
        logging.warning(f"Unknown arguments encountered and ignored: {unknown}")

    # Proceed to main function
    main(args)

# python main.py input_file output_file --x13 --stl --cissa --verbose