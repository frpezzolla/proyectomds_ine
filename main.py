# main.py

import argparse
import logging
import os
import sys

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from src.cissa import get_cissa  # Assuming cissa.py is in src/ directory
# from src.x13 import apply_x13  # TODO: Implement X13 method in x13.py
# from src.stl import apply_stl  # TODO: Implement STL method in stl.py
from src.utils import setup_logging

def apply_x13(series):
    """Apply X13-ARIMA-SEATS decomposition to the provided series."""
    # TODO: Implement X13 decomposition and return the trend component
    return

def apply_stl(series, period=12):
    """Apply STL decomposition to the provided series."""
    # TODO: Implement STL decomposition and return the trend component
    return

def apply_cissa(series, verbose=False):
    """Apply CiSSA decomposition to the provided series."""
    if verbose:
        logging.info("Applying CiSSA decomposition...")
    try:
        reconstructed_series, singular_values, groups = get_cissa(series)
        return reconstructed_series  # Expected to be a pd.Series
    except Exception as e:
        logging.error(f"CiSSA decomposition failed: {e}")
        return None
    
def run_diagnostics():
    
    return

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
    # Set up logging
    setup_logging(args.loglevel, args.logfile)

    logging.info("Starting the STD process...")

    # Check if input file exists
    if not os.path.isfile(args.input):
        logging.error(f"Input file '{args.input}' does not exist.")
        sys.exit(1)

    # Create output directories if they don't exist
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.plot_dir, exist_ok=True)
    os.makedirs(args.log_dir, exist_ok=True)

    # =========================================================================
    # Import data
    try:
        data = pd.read_csv(args.input)
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)
        logging.info("Data imported successfully.")
    except (FileNotFoundError, pd.errors.ParserError, ValueError) as e:
        logging.error(f"Error reading input file: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading the input file: {e}")
        sys.exit(1)

    # Check for required columns
    required_columns = ['employment', 'unemployment']
    for col in required_columns:
        if col not in data.columns:
            logging.error(f"Input data must contain '{col}' column.")
            sys.exit(1)

    employment_series = data['employment']
    unemployment_series = data['unemployment']

    # Initialize dictionaries to store trend components
    employment_trends = {}
    unemployment_trends = {}

    # =========================================================================
    # Apply STD methods
    if args.x13:
        logging.info("Applying X13-ARIMA-SEATS decomposition...")
        try:
            employment_trends['x13'] = apply_x13(employment_series)
            unemployment_trends['x13'] = apply_x13(unemployment_series)
        except Exception as e:
            logging.error(f"X13 decomposition failed: {e}")

    if args.stl:
        logging.info("Applying STL decomposition...")
        try:
            employment_trends['stl'] = apply_stl(employment_series)
            unemployment_trends['stl'] = apply_stl(unemployment_series)
        except Exception as e:
            logging.error(f"STL decomposition failed: {e}")

    if args.cissa:
        logging.info("Applying CiSSA decomposition...")
        employment_trends['cissa'] = apply_cissa(employment_series, verbose=args.verbose)
        unemployment_trends['cissa'] = apply_cissa(unemployment_series, verbose=args.verbose)
        
    # =========================================================================
    # Run diagnostics
    
    # =========================================================================
    # Calculate unemployment rates
    results = pd.DataFrame(index=data.index)
    results['employment'] = employment_series
    results['unemployment'] = unemployment_series
    results['unemployment_rate_raw'] = unemployment_series / (employment_series + unemployment_series)

    for method in employment_trends.keys():
        trend_employment = employment_trends[method]
        trend_unemployment = unemployment_trends[method]
        if trend_employment is not None and trend_unemployment is not None:
            results[f'unemployment_rate_{method}'] = trend_unemployment / (trend_employment + trend_unemployment)
            # Optional plotting
            if args.plot:
                plot_series(unemployment_series, trend_unemployment, f'Unemployment_{method}', args.plot_dir, usetex=args.usetex)
                plot_series(employment_series, trend_employment, f'Employment_{method}', args.plot_dir, usetex=args.usetex)
                plot_series(results['unemployment_rate_raw'], results[f'unemployment_rate_{method}'], f'Unemployment_Rate_{method}', args.plot_dir, usetex=args.usetex)
        else:
            logging.warning(f"Trend components for '{method}' are None. Skipping unemployment rate calculation.")
    
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
    parser = argparse.ArgumentParser(
        description="Process employment data with optional X13, STL, and CiSSA methods."
    )
    parser.add_argument('-i', '--input', type=str, required=True, help='Input CSV file path')
    parser.add_argument('-o', '--output', type=str, default='results.csv', help='Output CSV file name')
    parser.add_argument('--output_dir', type=str, default='outputs', help='Output directory')
    parser.add_argument('--plot_dir', type=str, default='plots', help='Directory to save plots')
    parser.add_argument('--log_dir', type=str, default='logs', help='Directory to save logs')
    parser.add_argument('--x13', action='store_true', help='Apply X13-ARIMA-SEATS decomposition')
    parser.add_argument('--stl', action='store_true', help='Apply STL decomposition')
    parser.add_argument('--cissa', action='store_true', help='Apply CiSSA decomposition')
    parser.add_argument('--plot', action='store_true', help='Generate plots')
    parser.add_argument('--usetex', action='store_true', help='Use LaTeX for plot fonts')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--loglevel', type=str, default='INFO', help='Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--logfile', type=str, default='', help='Log file name (if empty, logs to console)')

    args = parser.parse_args()

    main(args)


# python main.py input_file output_file --x13 --stl --cissa --verbose