import argparse
import logging
import os
import sys
import shlex

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from models.x13_model import X13Wrap
from models.stl import STLModel
from models.cissa import get_cissa

from diagnostics import outlier

from utils.setup_logging import setup as setup_logging

def apply_x13(series):
    """Apply X13-ARIMA-SEATS decomposition to the provided series."""
    # TODO: Implement X13 decomposition and return the trend component
    return

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
        deseasonalised_series = pd.Series(series_adj, index=series.index)
        return deseasonalised_series
    except Exception as e:
        logging.error(f"STL decomposition failed: {e}")
        return None

def apply_cissa(series, verbose=False):
    """Apply CiSSA decomposition to the provided series."""
    if verbose:
        logging.info("Applying CiSSA decomposition...")
    try:
        reconstructed_series, singular_values, groups = get_cissa(series)
        # do something with the seasonal trend decomposition
        deseasonalised_series = pd.Series(reconstructed_series['long term cycle'].flatten(), index=series.index)
        return deseasonalised_series
    except Exception as e:
        logging.error(f"CiSSA decomposition failed: {e}")
        return None
    
def run_diagnostics():
    pass

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
    # Import data
    data = import_data(args.input)

    # =========================================================================
    # Apply STD methods
    
    deseasonalised_series = {}
    
    if args.x13:
        logging.info("Applying X13-ARIMA-SEATS decomposition...")
        try:
            pass
        except Exception as e:
            logging.error(f"X13 decomposition failed: {e}")

    if args.stl:
        logging.info("Applying STL decomposition...")
        try:
            for sex in ['h', 'm']:
                for age_group in ['15', '25']:
                    deseasonalised_series[f'd{sex}{age_group}'] = apply_stl(data[f'd{sex}{age_group}'])
                    deseasonalised_series[f'o{sex}{age_group}'] = apply_stl(data[f'o{sex}{age_group}'])
        except Exception as e:
            logging.error(f"STL decomposition failed: {e}")

    if args.cissa:
        logging.info("Applying CiSSA decomposition...")
        for sex in ['h', 'm']:
            for age_group in ['15', '25']:
                deseasonalised_series[f'd{sex}{age_group}'] = apply_cissa(data[f'd{sex}{age_group}'])
                deseasonalised_series[f'o{sex}{age_group}'] = apply_cissa(data[f'o{sex}{age_group}'])
        
    # =========================================================================
    # Run diagnostics
    tasa = pd.read_csv("./data/endogena/to202406.csv")
    tasa.index = pd.DatetimeIndex(tasa.pop('ds'))
    tasa = tasa['to']

    outlier_serie = pd.Series(pd.date_range(start='2020-01-01', end='2022-05-01', freq='MS'))
    outlier_serie.index = pd.DatetimeIndex(outlier_serie)
    outlier_serie.loc[:] = 1
    # X13
    x13model = X13Wrap()
    out_analist = outlier.OutlierAnalysis()    
    span_analist = outlier.SlidingOutliers(x13model)
    history_analist = outlier.RevisionOutlier(x13model)
    
    out_analist.fit(tasa, outlier=outlier_serie)
    out_analist.seasonality_diff(x13model)
    out_analist.model_evolution(x13model)
    out_analist.plot_evol()

    span_analist.A_mse(tasa, outlier=outlier_serie)
    span_analist.MM_mse(tasa, outlier=outlier_serie)
    span_analist.A_analysis(tasa, outlier=outlier_serie)
    span_analist.MM_analysis(tasa, outlier=outlier_serie)

    history_analist.fit(tasa)
    history_analist.A_analysis(outlier=outlier_serie)
    history_analist.C_analysis(outlier=outlier_serie)


    # STL
    out_analist = outlier.OutlierAnalysis(STLModel)    
    span_analist = outlier.SlidingOutliers(STLModel)
    history_analist = outlier.RevisionOutlier(STLModel)

    # CISSA
    out_analist = outlier.OutlierAnalysis()    
    span_analist = outlier.SlidingOutliers()
    history_analist = outlier.RevisionOutlier()
    # =========================================================================
    # Calculate unemployment rates
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
    # Save results
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