import argparse
import logging
import os
import time
import sys
import shlex
import shutil

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from models.x13_model import X13Model
from models.stl import STLModel
from models.cissa import CiSSAModel

from utils.diagnose import Diagnose
from utils.preprocess import ENE

#%% MODELS
def apply_x13(series):
    """Realiza la desestacionalización X13-ARIMA-SEATS."""
    try:
        x13_model = X13Model()
        x13_model.fit(series)
        series_adj = x13_model.adjust()
        return series_adj.seasadj
    except Exception as e:
        raise RuntimeError(f"Error en X13: {e}")

def apply_stl(series):
    """Realiza la desestacionalización STL."""
    try:
        stl_model = STLModel()
        stl_model.fit(series)
        series_adj = stl_model.adjust()
        return series_adj.seasadj
    except Exception as e:
        raise RuntimeError(f"Error en STL: {e}")

def apply_cissa(series):
    """Realiza la desestacionalización CiSSA."""
    try:
        cissa_model = CiSSAModel()
        cissa_model.fit(series)
        cissa_model.adjust()
        return cissa_model.seasadj
    except Exception as e:
        raise RuntimeError(f"Error en CiSSA: {e}")


#%% IMPORT DATA
def import_data(file_dir):
    try:
        data = pd.read_csv(file_dir, sep=';')
        data['date'] = pd.to_datetime(data['ano'].astype(str) + '-' + data['mes'].astype(str) + '-01')
        data.set_index('date', inplace=True)
        data.drop(['ano', 'mes'], axis=1, inplace=True)
        logging.info("Data imported successfully.")
    except (FileNotFoundError, pd.errors.ParserError, ValueError) as e:
        logging.error(f"Error reading input file: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading the input file: {e}")
        # sys.exit(1)
        raise e
    return data

#%% PLOT
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

#%% MAIN
def main(args):

    logging.info("Starting the STD process...")
    
    if not os.path.isfile(args.input):
        logging.warning(f"El archivo de entrada '{args.input}' no existe."
            "Inferiendo a partir de datos anuales y/o mensuales."
            "Este proceso puede requerir conexión a la base de datos pública del INE.")

        
    # =========================================================================
    # TRANSFORM ENE
    # =========================================================================

    ene = ENE()
    if not os.path.exists(args.input):
        ene.groupby_cae('anual')
    
    # TODO: Siempre descarga datos?
    logging.info("Descargando datos desde la base de datos del INE.")
    ene.nuevos_datos()
    ene.groupby_cae('mensual')

    # =========================================================================
    # IMPORT DATA
    # =========================================================================
    logging.info("Iniciando la importación de datos...")
    ti = time.time()
    timeout = 60
    
    try:
        data = import_data(args.input)
        logging.info(f"Archivo '{args.input}' importado exitosamente.")
    except FileNotFoundError:
        wait = time.time() - ti
        if wait < timeout:
            logging.error(f"Archivo '{args.input}' no encontrado después de {wait:.2f} segundos.")
        else:
            logging.error(f"Archivo '{args.input}' no encontrado. Tiempo de espera agotado ({timeout} segundos).")
        sys.exit(1)
    except RuntimeError as e:
        logging.error(str(e), exc_info=args.show_traceback)
        sys.exit(1)
        
    # # =========================================================================
    # # IMPORT DATA
    # # =========================================================================
    # logging.info("Iniciando la importación de datos...")
    # ti = time.time()
    # timeout = 60
    
    # try:
    #     data = import_data(args.input)
    #     logging.info(f"Archivo '{args.input}' importado exitosamente.")
        
    #     # Explicitly flush logs
    #     for handler in logging.getLogger().handlers:
    #         if isinstance(handler, logging.StreamHandler):
    #             handler.flush()
    # except FileNotFoundError:
    #     wait = time.time() - ti
    #     if wait < timeout:
    #         logging.error(f"Archivo '{args.input}' no encontrado después de {wait:.2f} segundos.")
    #     else:
    #         logging.error(f"Archivo '{args.input}' no encontrado. Tiempo de espera agotado ({timeout} segundos).")
        
    #     # Explicitly flush logs
    #     for handler in logging.getLogger().handlers:
    #         if isinstance(handler, logging.StreamHandler):
    #             handler.flush()
        
    #     sys.exit(1)
    # except RuntimeError as e:
    #     logging.error(str(e), exc_info=args.show_traceback)
        
    #     # Explicitly flush logs
    #     for handler in logging.getLogger().handlers:
    #         if isinstance(handler, logging.StreamHandler):
    #             handler.flush()
        
    #     sys.exit(1)

    # =========================================================================
    # APPLY STD METHODS
    # =========================================================================
    deseasonalised_series = {}
    
    for series_name in data.columns:
        series = data[series_name]
        logging.info(f"Iniciando desestacionalización para la serie: {series_name}")
        
        try:
            if args.x13:
                logging.info("Aplicando desestacionalización X13-ARIMA-SEATS...")
                deseasonalised_series[f"{series_name}_std"] = apply_x13(series)
            elif args.stl:
                logging.info("Aplicando desestacionalización STL...")
                deseasonalised_series[f"{series_name}_std"] = apply_stl(series)
            elif args.cissa:
                logging.info("Aplicando desestacionalización CiSSA...")
                deseasonalised_series[f"{series_name}_std"] = apply_cissa(series)
        except RuntimeError as e:
            logging.error(str(e), exc_info=args.show_traceback)
            continue
    
    deseasonalised_df = pd.DataFrame(deseasonalised_series)
    results = pd.concat([data, deseasonalised_df], axis=1)
    logging.info("Proceso de desestacionalización completado.")
    
    # =========================================================================
    # RUN DIAGNOSTICS
    # =========================================================================
    
    if args.diagnose:
        logging.info("Iniciando diagnóstico de series temporales...")
        
        try:
            tasa = data[['td']].copy()
            tasa.index.name = 'ds'
            tasa = tasa['td']
            logging.info("Datos de diagnóstico preparados exitosamente.")
    
            outlier_serie = pd.Series(pd.date_range(start='2020-01-01', end='2022-05-01', freq='MS'))
            outlier_serie.index = pd.DatetimeIndex(outlier_serie)
            outlier_serie.loc[:] = 1
            logging.info("Serie de outliers de pandemia creada exitosamente.")
    
            diag = Diagnose(tasa)
            diag.set_outlier(outlier_serie)
            logging.info("Diagnóstico inicializado correctamente.")
            
            if args.x13:
                logging.info("Ejecutando diagnóstico para X13-ARIMA-SEATS...")
                try:
                    diag.outlier_diags(X13Model)
                    logging.info("Diagnóstico para X13-ARIMA-SEATS completado exitosamente.")
                except Exception as e:
                    logging.error(f"Error al ejecutar diagnóstico con X13-ARIMA-SEATS: {type(e).__name__}: {e}", 
                                  exc_info=args.show_traceback)
                    sys.exit(1)
    
            if args.stl:
                logging.info("Ejecutando diagnóstico para STL...")
                try:
                    diag.outlier_diags(STLModel)
                    logging.info("Diagnóstico para STL completado exitosamente.")
                except Exception as e:
                    logging.error(f"Error al ejecutar diagnóstico con STL: {type(e).__name__}: {e}", 
                                  exc_info=args.show_traceback)
                    sys.exit(1)
    
            if args.cissa:
                logging.info("Ejecutando diagnóstico para CiSSA...")
                try:
                    diag.outlier_diags(CiSSAModel)
                    logging.info("Diagnóstico para CiSSA completado exitosamente.")
                except Exception as e:
                    logging.error(f"Error al ejecutar diagnóstico con CiSSA: {type(e).__name__}: {e}", 
                                  exc_info=args.show_traceback)
                    sys.exit(1)
    
        except Exception as e:
            logging.critical(f"Error crítico durante la preparación de diagnóstico: {type(e).__name__}: {e}", 
                             exc_info=args.show_traceback)
            sys.exit(1)


    # =========================================================================
    # CALCULATE UNEMPLOYMENT RATES
    # =========================================================================
    
    logging.info("Iniciando cálculo de tasas de desempleo...")
    
    # List of columns required for calculation
    required_columns = [f'd{sex}{age_group}' for sex in ['h', 'm'] for age_group in ['15', '25']] + \
                       [f'o{sex}{age_group}' for sex in ['h', 'm'] for age_group in ['15', '25']]
    missing_columns = [col for col in required_columns if col not in data.columns or col not in results.columns]
    
    if missing_columns:
        logging.error(f"Faltan las siguientes columnas necesarias para calcular las tasas de desempleo: {missing_columns}")
        sys.exit(1)
    
    try:
        for sex in ['h', 'm']:
            for age_group in ['15', '25']:
                # Extract original and deseasonalised data
                unoccupied_original = results[f'd{sex}{age_group}']
                occupied_original = data[f'o{sex}{age_group}']
                unoccupied_deseasonalised = results.get(f'd{sex}{age_group}_std', None)
                occupied_deseasonalised = results.get(f'o{sex}{age_group}_std', None)
                
                # Safeguards for division by zero
                total_original = occupied_original + unoccupied_original
                if (total_original == 0).any():
                    logging.warning(f"Se encontraron valores cero en el total de ocupados y desocupados para "
                                    f"sexo '{sex}' y grupo de edad '{age_group}'. La tasa se establecerá como NaN.")
                results[f'td{sex}{age_group}'] = unoccupied_original / total_original.replace(0, pd.NA)
    
                if unoccupied_deseasonalised is not None and occupied_deseasonalised is not None:
                    total_deseasonalised = occupied_deseasonalised + unoccupied_deseasonalised
                    if (total_deseasonalised == 0).any():
                        logging.warning(f"Se encontraron valores cero en el total desestacionalizado de ocupados y "
                                        f"desocupados para sexo '{sex}' y grupo de edad '{age_group}'. La tasa se establecerá como NaN.")
                    results[f'td{sex}{age_group}_std'] = unoccupied_deseasonalised / total_deseasonalised.replace(0, pd.NA)
                else:
                    logging.info(f"Columnas desestacionalizadas no disponibles para sexo '{sex}' y grupo de edad '{age_group}'. "
                                 f"Solo se calcularán las tasas originales.")
    
        logging.info("Cálculo de tasas de desempleo completado exitosamente.")
    
    except KeyError as e:
        logging.error(f"Error al acceder a una columna necesaria: {e}. Verifique la consistencia de las columnas en los datos.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error inesperado durante el cálculo de tasas de desempleo: {type(e).__name__}: {e}", exc_info=args.show_traceback)
        sys.exit(1)


    # =========================================================================
    # PLOTTING
    # =========================================================================
    
    # Create plot directory if needed
    if args.plot:
        if not os.path.exists(args.plot_dir):
            os.makedirs(args.plot_dir, exist_ok=True)
            logging.info(f"Directorio de gráficos creado: {args.plot_dir}")
    
        logging.info("Iniciando generación de gráficos...")
            
        model_name = 'x13' if args.x13 else 'stl' if args.stl else 'cissa'
        
        col_meaning = {
            'dh15': 'Desocupados hombres 15 a 24', 
            'dm15': 'Desocupados mujeres 15 a 24', 
            'dh25': 'Desocupados hombres 25 o más', 
            'dm25': 'Desocupados mujeres 25 o más', 
            'oh15': 'Ocupados hombres 15 a 24', 
            'om15': 'Ocupados mujeres 15 a 24', 
            'oh25': 'Ocupados hombres 25 o más', 
            'om25': 'Ocupados mujeres 25 o más',
            'd': 'Total desocupados', 
            'o': 'Total ocupados', 
            'dh': 'Desocupados hombres', 
            'dm': 'Desocupados mujeres', 
            'oh': 'Ocupados hombres', 
            'om': 'Ocupados mujeres', 
            'fh': 'Fuerza de trabajo hombres', 
            'fm': 'Fuerza de trabajo mujeres', 
            'ft': 'Fuerza de trabajo total',
            'tdh': 'Tasa desocupados hombres',
            'tdm': 'Tasa desocupados mujeres', 
            'td': 'Tasa desocupados'
        }
        
        try:
            for series in data.columns:
                if series in results.columns and f"{series}_std" in results.columns:
                    plot_series(
                        original_series=results[series],
                        trend_series=results[f"{series}_std"],
                        method_name=model_name,
                        output_dir=args.plot_dir,
                        usetex=args.use_tex
                    )
                    logging.info(f"Gráfico generado para {col_meaning.get(series, series)}.")
                else:
                    logging.warning(f"Faltan datos para graficar la serie '{col_meaning.get(series, series)}'.")
        except Exception as e:
            logging.error(f"Error al generar gráficos: {type(e).__name__}: {e}", exc_info=args.show_traceback)

    
    # =========================================================================
    # SAVE RESULTS
    # =========================================================================
    logging.info("Iniciando el guardado de resultados...")
    
    if not os.path.exists(args.output_dir):
        try:
            os.makedirs(args.output_dir, exist_ok=True)
            logging.info(f"Directorio de salida creado: {args.output_dir}")
        except Exception as e:
            logging.error(f"Error al crear el directorio de salida '{args.output_dir}': {type(e).__name__}: {e}", exc_info=args.show_traceback)
            sys.exit(1)
    
    output_file = os.path.join(args.output_dir, args.output)
    
    try:
        results.to_csv(output_file)
        logging.info(f"Resultados guardados exitosamente en: {output_file}")
    except PermissionError as e:
        logging.error(f"Permiso denegado al intentar guardar el archivo: {type(e).__name__}: {e}", exc_info=args.show_traceback)
        sys.exit(1)
    except FileNotFoundError as e:
        logging.error(f"Ruta de archivo no encontrada al intentar guardar resultados: {type(e).__name__}: {e}", exc_info=args.show_traceback)
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error desconocido al guardar resultados: {type(e).__name__}: {e}", exc_info=args.show_traceback)
        sys.exit(1)



#%% RUN
if __name__ == "__main__":
    
    print("Comenzando proceso de desestacionalización...")

    # =========================================================================
    # INITIALISE PARSER
    parser = argparse.ArgumentParser(
        description="Process employment data with optional X13, STL, and CiSSA methods."
    )
    
    # =========================================================================
    # INITIALISE TEMPORARY LOGGING
    
    logging.basicConfig(level=logging.ERROR, 
                        format='%(asctime)s - %(levelname)s - %(message)s', 
                        stream=sys.stdout)
    logging.info("Activando logging temporal.")

    # =========================================================================
    # SET DEFAULTS
    DEFAULT_OUTPUT_NAME = "results.csv"
    DEFAULT_OUTPUT_DIR = "output"
    DEFAULT_LOG_LEVEL = "INFO"
    DEFAULT_PLOT_DIR = "plot"
    DEFAULT_DIAGNOSTICS_DIR = "diag"
    DEFAULT_LOG_FILENAME = None
    DEFAULT_VERBOSE_BOOL = True
    DEFAULT_LOGFILE_DIR = 'log'
    
    # =========================================================================
    # I/O
    # INPUT FILE PATH (required)
    parser.add_argument('-i', '--input', type=str, help='PATH al archivo de entrada.')
    # TODO: mix the following two?
    # desired OUTPUT FILE PATH
    parser.add_argument('-o', '--output', type=str, default=DEFAULT_OUTPUT_NAME, help='Nombre deseado para el archivo de salida.')
    # desired OUTPUT DIRECTORY for OUTPUT FILE
    parser.add_argument('--output_dir', type=str, default=DEFAULT_OUTPUT_DIR, help="Directorio deseado para el archivo de salida. Por defecto: './outputs/'.")
    
    # =========================================================================
    # SEASONAL TREND DECOMPOSITION METHOD
    parser.add_argument('--x13', action='store_true', help='Aplica desestacionalización X13-ARIMA-SEATS.')
    parser.add_argument('--stl', action='store_true', help='Aplica desestacionalización STL.')
    parser.add_argument('--cissa', action='store_true', help='Aplica desestacionalización CiSSA.')
    
    # =========================================================================
    # DIAGNOSTICS
    # choose whether to run diagnosis
    parser.add_argument('-d', '--diagnose', action='store_true', help='Aplica diagnósticos')
    # desired LOGGING DIRECTORY for LOGGING FILE
    parser.add_argument('--output_dir_diag', type=str, default=DEFAULT_DIAGNOSTICS_DIR, help="Directorio deseado para los resultados de diagnóstocos si '-d' o '--diagnose' es llamado. Por defecto: './diagnostics/'.")
        
    # =========================================================================
    # LOGGING ARGUMENTS
    # SET LOG LEVEL
    parser.add_argument('--log_level', type=str, default=DEFAULT_LOG_LEVEL, help='Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    # desired LOG FILE PATH
    parser.add_argument('--log_filename', type=str, default=DEFAULT_LOG_FILENAME, help='Archivo para guardar logs (si se entrega vacío, solo se utiliza la consola)')
    # choose if the logging is verbose
    parser.add_argument('--verbose', action='store_true', default=DEFAULT_VERBOSE_BOOL, help="Habilita output 'verbose' para logging")
    # desired LOGGING FILE PATH
    parser.add_argument('--log_dir', type=str, default=DEFAULT_LOGFILE_DIR, help="Directorio de salida para logging si '--log_name' es entregado. Por defecto: './logs/'.")
    
    # =========================================================================
    # PLOTTING
    # choose whether to plot
    parser.add_argument('--plot', action='store_true', help="Genera gráficos y los guarda según '--plot_dir'")
    # desired PLOT DIRECTORY
    parser.add_argument('--plot_dir', type=str, default=DEFAULT_PLOT_DIR, help="Directorio de salida para los gráficos generados. Por defecto: './plots/'.")
    # choose wether to use LaTeX for typesetting
    parser.add_argument('--use_tex', action='store_true', help='Habilita LaTeX como la fuente usada para los gráficos')
    
    # =========================================================================
    # Show Traceback
    parser.add_argument('--show_traceback', action='store_true', help="Habilita mostrar el Traceback de errorer para debugging.")
    
    # =========================================================================
    # CHECK ARGUMENTS
    
    # =========================================================================
    # Check if command line arguments have been provided
    # If they have, then those are used
    # If they haven´t, then 'arguments.txt' is checked
    # If neither contains arguments, an error is raised
    try:
        if len(sys.argv) > 1:
            args = parser.parse_args()
            logging.info("Usando los comandos proporcionados en la consola.")
        elif os.path.isfile('arguments.txt'):
            try:
                with open('arguments.txt', 'r') as f:
                    arg_str = f.read()
                    args_list = shlex.split(arg_str)
                    args = parser.parse_args(args_list)
                    logging.info("No se han proporcionado comandos desde la consola. "
                                 "Obteniendo argumentos desde 'arguments.txt'.")
            except Exception as e:
                logging.error(f"Error en la lectura de 'arguments.txt': {e}", exc_info=True)
                sys.exit(1)
        else:
            logging.error("No se han entregado argumentos de consola y 'arguments.txt' está vacío. "
                          "Consulta 'python main.py --help' si necesitas ayuda.", exc_info=True)
            sys.exit(1)    
    except Exception as e:
        logging.error(f"Se produjo un error durante la configuración de los argumentos: {e}", exc_info=True)
        sys.exit(1)
    
    # =========================================================================
    # Handle logging input        
    logging_level_dict = {'DEBUG': logging.DEBUG,
                          'INFO': logging.INFO,
                          'WARNING': logging.WARNING,
                          'ERROR': logging.ERROR,
                          'CRITICAL': logging.CRITICAL}
    # Determine log file path
    LOG_FILENAME = os.path.join(args.log_dir, args.log_filename) if args.log_filename else None
    # Check and apply the logging level
    if args.log_level.upper() in logging_level_dict:
        logging.basicConfig(filename=LOG_FILENAME,
                            level=logging_level_dict[args.log_level.upper()],
                            format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info(f"Iniciando logging con nivel: {args.log_level.upper()}")
    else:
        logging.basicConfig(filename=LOG_FILENAME,
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info(f"Nivel de logging '--log_level' inválido: {args.log_level}. Usando el nivel por defecto: 'INFO'.")
    # Create log directory if needed
    if args.log_filename:
        if not os.path.exists(args.log_dir):
            os.makedirs(args.log_dir, exist_ok=True)
            logging.info(f"Directorio de logs creado: {args.log_dir}")
    
    # =========================================================================
    # Check if input file has been provided
    if not args.input:
        logging.error("No se ha proporcionado un archivo de entrada.", exc_info=args.show_traceback)
        sys.exit(1)

    # =========================================================================   
    # Check if only one STD method has been called
    # If more than one, raise an Exception and abort
    std_methods = [args.x13, args.stl, args.cissa]
    if sum(std_methods) > 1:
        logging.error("Solo se puede seleccionar un método de desestacionalización a la vez (--x13, --stl, --cissa).", 
                      exc_info=args.show_traceback)
        sys.exit(1)
    elif not any(std_methods):
        logging.error("Debe seleccionar al menos un método de desestacionalización (--x13, --stl, --cissa).", 
                      exc_info=args.show_traceback)
        sys.exit(1)
    
    # =========================================================================
    # Check LaTeX
    if args.use_tex and not shutil.which('latex'):
        logging.error("No se ha encontrado una instalación de LaTeX en el sistema. "
                      "Instale LaTeX e intente de nuevo, u omita el argumento '--usetex'.", 
                      exc_info=args.show_traceback)
        sys.exit(1)
    

        
    # =========================================================================    
    main(args)

# python main.py input_file output_file --x13 --stl --cissa --verbose