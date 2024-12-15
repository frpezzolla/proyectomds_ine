# Proyecto de Ciencia de Datos: Ajuste Estacional de la Tasa de Desocupación para el Instituto Nacional de Estadísticas

## Descripción del Proyecto

Este proyecto es una **Herramienta de Descomposición de Series de Tiempo** desarrollada para el **Instituto Nacional de Estadísticas (INE)** de Chile. Proporciona herramientas para realizar la desestacionalización de datos de empleo y desempleo utilizando tres métodos:

- **X13-ARIMA-SEATS**
- **STL (Descomposición Estacional y de Tendencia mediante Loess)**
- **CiSSA (Análisis de Espectro Singular Circulante)**

La herramienta permite desestacionalizar las series de empleo y desempleo, calcular la tasa de desempleo y generar resultados. Está diseñada para ser modular, extensible y fácil de usar, con opciones de interfaz de línea de comandos, registro de eventos (logging), manejo de errores y capacidades opcionales de generación de gráficos.

## Integrantes del Equipo

- **Alonso Uribe**
- **Fabrizzio Pezzolla**
- **Israel Astudillo**
- **Rodrigo Molina**

## Repositorio de Datos

- [Google Drive](https://drive.google.com/drive/folders/1921PmK4MH-ttoz9gJdE00I1X0UiyZwg4?usp=drive_link)

## Características y Funcionalidades

- **Descomposición Estacional y de Tendencia**: Aplica los métodos X13-ARIMA-SEATS, STL y CiSSA a los datos de empleo y desempleo.
- **Cálculo de la Tasa de Desempleo**: Calcula la tasa de desempleo utilizando las series desestacionalizadas.
- **Interfaz de Línea de Comandos**: Especifica archivos de entrada/salida y opciones para los métodos de descomposición a través de argumentos de línea de comandos.
- **Manejo de Errores**: Manejo robusto de errores para operaciones de archivos y procesamiento de datos.
- **Registro de Eventos (Logging)**: Registro configurable en consola o archivo con diferentes niveles de detalle.
- **Generación de Gráficos**: Funcionalidad opcional para generar gráficos de las series originales y sus componentes de tendencia, con soporte para fuentes formateadas en LaTeX.
- **Indicadores de Progreso**: Visualiza el progreso de la desestacionalización y el cálculo de tasas mediante barras de progreso con `tqdm`.

## Instalación

### Requisitos Previos

- **Windows**
- **Python 3.8 a 3.12**
- Instalador de paquetes **pip**
- **Git** (opcional, para clonar el repositorio)

### Dependencias

Los paquetes de Python requeridos se enumeran en el archivo `requirements.txt` e incluyen:

- `numpy`
- `pandas`
- `matplotlib`
- `statsmodels`
- `scipy`
- `tqdm`

### Pasos de Instalación

1. **Clonar el Repositorio**

   ```bash
   git clone https://github.com/usuario/proyectomds_ine.git
   cd proyectomds_ine
   ```

2. **Crear un Entorno Virtual (Recomendado)**

   ```bash
   python -m venv venv
   source venv/bin/activate      # En Windows: venv\Scripts\activate
   ```

3. **Instalar Dependencias**

   ```bash
   pip install -r requirements.txt
   ```

4. **Verificación de la Instalación**

   ```bash
   python main.py --help
   ```

   Deberías ver el mensaje de ayuda con las opciones disponibles.

### Configuración de X13-ARIMA-SEATS

#### Windows

- Descargue el binario de X13 (.ASCII) desde el [sitio web de la Oficina del Censo de EE. UU.](https://www.census.gov/data/software/x13as.html).
- Extraiga los archivos y coloque el ejecutable en un directorio incluido en la variable de entorno `PATH` de su sistema. Llame a esta variable `X13PATH`.

## Uso

### Argumentos de Línea de Comandos

La herramienta se ejecuta a través del script `main.py` con las siguientes opciones:

- `-i`, `--input`: Ruta del archivo CSV de entrada (requerido). Actualmente **el archivo debe estar ubicado en `data/preprocess`.**
- `-o`, `--output`: Nombre del archivo CSV de salida (por defecto: `results.csv`).
- `--output_dir`: Directorio de salida (por defecto: `output`).
- `--output_dir_diag`: Directorio deseado para los resultados de diagnósticos si se usa `-d` o `--diagnose` (por defecto: `diag`).
- `--plot_dir`: Directorio para guardar los gráficos (por defecto: `plot`).
- `--log_dir`: Directorio para guardar los registros (por defecto: `log`).
- `--x13`: Aplica el método X13-ARIMA-SEATS.
- `--stl`: Aplica el método STL.
- `--cissa`: Aplica el método CiSSA.
- `--plot`: Genera gráficos.
- `--usetex`: Utiliza LaTeX para las fuentes en los gráficos.
- `--verbose`: Habilita salida detallada.
- `--loglevel`: Nivel de registro (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- `--logfile`: Nombre del archivo de registro (si se deja vacío, registra en la consola).
- `--show_traceback`: Habilita mostrar el Traceback de errores para debugging.

### Formato de los Datos de Entrada

El archivo de entrada debe ser un archivo CSV con las siguientes columnas:

- `ano`: Año (numérico).
- `mes`: Mes (numérico).
- Otras columnas representando categorías de ocupados y desocupados, siguiendo la nomenclatura utilizada en el código (e.g., `dh15`, `dm15`, `oh15`, etc.).

### Ejemplos

#### Ejemplo 1: Aplicar X13-ARIMA-SEATS con Generación de Gráficos

```bash
python main.py -i datos_empleo.csv --x13 --plot --usetex --loglevel INFO
```

- Aplica el método X13-ARIMA-SEATS.
- Genera gráficos con fuentes formateadas en LaTeX.
- Establece el nivel de registro en INFO.
- Guarda los gráficos en `plot/` y los resultados en `output/results.csv`.

#### Ejemplo 2: Aplicar CiSSA y Guardar Registros en un Archivo

```bash
python main.py -i datos_empleo.csv -o resultados_cissa.csv --cissa --logfile cissa.log --log_dir logs --loglevel DEBUG
```

- Aplica solo el método CiSSA.
- Guarda los registros en `logs/cissa.log`.
- Establece el nivel de registro en DEBUG para registros detallados.
- Guarda los resultados en `output/resultados_cissa.csv`.

#### Ejemplo 3: Aplicar Descomposición STL Sin Generar Gráficos

```bash
python main.py -i datos_empleo.csv --stl
```

- Aplica solo el método STL.
- No genera gráficos.
- Utiliza el archivo de salida y directorios por defecto (`output/results.csv`, `plot/`, `log/`).

#### Ejemplo 4: Uso de `arguments.txt`

Si no pasas argumentos por la consola, el script intentará leer `arguments.txt`. Un ejemplo de `arguments.txt`:

```
-i datos_empleo.csv
--stl
--diagnose
--loglevel DEBUG
--output_dir custom_outputs
```

Correr:

```bash
python main.py
```

Usará los argumentos definidos en `arguments.txt`.

## Estructura del Proyecto

```
proyectomds_ine/
├── README.md
├── requirements.txt
├── arguments.txt
├── main.py
├── data/
│   ├── preprocess/         # Archivos de datos de entrada
│   ├── raw/
│   │   ├── anual/
│   │   └── monthly/
│   └── diagnostics/
├── output/
│   └── (resultados generados)
├── diagnostics/
│   ├── __init__.py
│   ├── sliding_spans.py
│   ├── revisions_history_diagnostics.py
│   ├── outlier_prediction.py
│   └── plotting.py
├── logs/
│   └── (archivos de registro)
├── models/
│   ├── __init__.py
│   ├── base.py
│   ├── cissa.py
│   ├── x13.py
│   └── stl.py
└── utils/
    ├── logging.py
    ├── setup_logging.py
    ├── preprocess.py
    └── plotting.py
```

## Información de Contacto

Para cualquier pregunta o soporte, por favor contacta a:

- **Alonso Uribe**
  - Correo electrónico: [mail](https://github.com/alonsoU)
  - GitHub: [link](mailto:alonso.uribe@ug.uchile.cl)
- **Fabrizzio Pezzolla**
  - Correo electrónico: [mail](mailto:frpezzoll@gmail.com)
  - GitHub: [link](https://github.com/frpezzolla)
- **Israel Astudillo**
  - Correo electrónico: [mail](mailto:israel.astudillo@ug.uchile.cl)
  - GitHub: [link](https://github.com/IsraPKMNPAP)
- **Rodrigo Molina**
  - Correo electrónico: [mail](mailto:rodmolina@ug.uchile.cl)
  - GitHub: [link](https://github.com/RodrigoMolinaAvila)

## Agradecimientos

- **pyCiSSA**: [pyCiSSA](https://github.com/LukeAFullard/pyCiSSA.git) por Luke A. Fullard.
- **X13-ARIMA-SEATS**: Proporcionado por la Oficina del Censo de EE. UU. e implementada usando la biblioteca `statsmodels`.
- **Descomposición STL**: Implementada utilizando la biblioteca `statsmodels`.
