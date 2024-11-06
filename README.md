# Herramienta de Descomposición de Series de Tiempo para el INE

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

## Instalación

### Requisitos Previos

- **Python 3.8 o superior**
- Instalador de paquetes **pip**
- **Git** (opcional, para clonar el repositorio)

### Dependencias

Los paquetes de Python requeridos se enumeran en el archivo `requirements.txt` e incluyen:

- `numpy`
- `pandas`
- `matplotlib`
- `statsmodels`
- `scipy`
- `pycissa` (desde el repositorio `pyCiSSA`)

#### Requisitos Adicionales para Windows

Para usuarios de Windows, se requiere la instalación de **Microsoft Visual C++ 14.0** o superior debido a que la biblioteca `spectrum`, una dependencia de `pycissa`, lo necesita. Puede instalarlo desde [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/). Para detalles sobre qué instalar, consulte [esta guía](https://www.scivision.dev/python-windows-visual-c-14-required/).

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

4. **Instalar pyCiSSA**

   ```bash
   pip install git+https://github.com/LukeAFullard/pyCiSSA.git
   ```

   > **Nota**: Asegúrese de tener Git instalado para clonar el repositorio `pyCiSSA`.

### Configuración de X13-ARIMA-SEATS

#### Windows

- Descargue el binario de X13 desde el [sitio web de la Oficina del Censo de EE. UU.](https://www.census.gov/data/software/x13as.html).
- Extraiga los archivos y coloque el ejecutable en un directorio incluido en la variable de entorno `PATH` de su sistema.

#### macOS y Linux

- Instale X13 mediante `conda`:

  ```bash
  conda install -c conda-forge x13as
  ```

- Alternativamente, descargue y compile el código fuente desde el [sitio web de la Oficina del Censo de EE. UU.](https://www.census.gov/data/software/x13as.html).

### Verificación de la Instalación

Ejecute el siguiente comando para verificar que la instalación fue exitosa:

```bash
python main.py --help
```

Debería ver el mensaje de ayuda con instrucciones de uso y opciones disponibles.

## Uso

### Argumentos de Línea de Comandos

La herramienta se ejecuta a través del script `main.py` con las siguientes opciones:

- `-i`, `--input`: Ruta del archivo CSV de entrada (requerido).
- `-o`, `--output`: Nombre del archivo CSV de salida (por defecto: `results.csv`).
- `--output_dir`: Directorio de salida (por defecto: `outputs`).
- `--plot_dir`: Directorio para guardar los gráficos (por defecto: `plots`).
- `--log_dir`: Directorio para guardar los registros (por defecto: `logs`).
- `--x13`: Aplica el método X13-ARIMA-SEATS.
- `--stl`: Aplica el método STL.
- `--cissa`: Aplica el método CiSSA.
- `--plot`: Genera gráficos.
- `--usetex`: Utiliza LaTeX para las fuentes en los gráficos.
- `--verbose`: Habilita salida detallada.
- `--loglevel`: Nivel de registro (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- `--logfile`: Nombre del archivo de registro (si se deja vacío, registra en la consola).

### Formato de los Datos de Entrada

El archivo CSV de entrada debe contener las siguientes columnas:

- `date`: Fechas en un formato reconocido por pandas (por ejemplo, `YYYY-MM-DD`).
- `employment`: Datos de empleo como valores numéricos.
- `unemployment`: Datos de desempleo como valores numéricos.

### Ejemplos

#### Ejemplo 1: Aplicar Todos los Métodos de Descomposición con Generación de Gráficos

```bash
python main.py -i data/datos_empleo.csv --x13 --stl --cissa --plot --usetex --loglevel INFO
```

- Aplica los métodos X13-ARIMA-SEATS, STL y CiSSA.
- Genera gráficos con fuentes formateadas en LaTeX.
- Establece el nivel de registro en INFO.

#### Ejemplo 2: Aplicar Solo CiSSA y Guardar Registros en un Archivo

```bash
python main.py -i data/datos_empleo.csv -o resultados_cissa.csv --cissa --logfile logs/cissa.log --loglevel DEBUG
```

- Aplica solo el método CiSSA.
- Guarda los registros en `logs/cissa.log`.
- Establece el nivel de registro en DEBUG para registros detallados.

#### Ejemplo 3: Aplicar Descomposición STL Sin Generar Gráficos

```bash
python main.py -i data/datos_empleo.csv --stl
```

- Aplica solo el método STL.
- No genera gráficos.
- Utiliza el archivo de salida y directorios por defecto.

## Estructura del Proyecto

```
proyectomds_ine/
├── README.md
├── requirements.txt
├── setup.py
├── main.py
├── data/
│   └── (archivos de datos de entrada)
├── src/
│   ├── __init__.py
│   ├── cissa.py
│   ├── x13.py
│   ├── stl.py
│   ├── plotting.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_cissa.py
│   ├── test_x13.py
│   ├── test_stl.py
│   └── test_utils.py
├── logs/
│   └── (archivos de registro)
└── plots/
    └── (gráficos generados)
```

## Contribuciones

Agradecemos las contribuciones de la comunidad. Para contribuir:

1. **Haz un fork** del repositorio.
2. **Crea una nueva rama** para tu característica o corrección de errores.
3. Escribe **mensajes de commit claros y descriptivos**.
4. Asegúrate de que tu código cumple con los **estándares de codificación** del proyecto.
5. Escribe **pruebas unitarias** para la nueva funcionalidad.
6. Envía un **pull request** al repositorio principal.

Por favor, consulta el archivo `CONTRIBUTING.md` para obtener directrices detalladas.

## Licencia

Este proyecto está licenciado bajo la **Licencia MIT**. Consulta el archivo `LICENSE` para más detalles.

## Información de Contacto

Para cualquier pregunta o soporte, por favor contacta a:

- **Coordinador del Proyecto**: Rodrigo Molina
  - Correo electrónico: [rodrigo.molina@ejemplo.com](mailto:rodrigo.molina@ejemplo.com)

## Agradecimientos

- **pyCiSSA**: [pyCiSSA](https://github.com/LukeAFullard/pyCiSSA.git) por Luke A. Fullard.
- **X13-ARIMA-SEATS**: Proporcionado por la Oficina del Censo de EE. UU.
- **Descomposición STL**: Implementada utilizando la biblioteca `statsmodels`.

---

Por favor, asegúrate de tener los permisos apropiados para usar y distribuir los datos y software incluidos en este proyecto.

---