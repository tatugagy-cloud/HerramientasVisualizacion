# Panel de Indicadores Financieros - Banxico

## Descripción del proyecto

Este proyecto consiste en el desarrollo de un dashboard interactivo utilizando Streamlit, conectado a la API del Sistema de Información Económica (SIE) del Banco de México (Banxico).

El objetivo es consultar, procesar y visualizar indicadores financieros mediante un panel que facilite el análisis de su comportamiento histórico.

## Objetivo

Integrar una API externa con Streamlit para transformar los datos obtenidos en información visual, organizada e interactiva que facilite su interpretación.

## Indicadores disponibles

- Tipo de cambio FIX.
- Tipo de cambio para solventar obligaciones.
- Tasa de Interés Interbancaria de Equilibrio (TIIE) a 28 días.

## Funcionalidades

- Consulta de información directamente desde la API de Banxico.
- Selección de indicadores financieros.
- Filtros por fechas.
- Tarjetas de indicadores KPI.
- Cálculo de promedio, mínimo y máximo.
- Cálculo de variación porcentual.
- Gráficas históricas interactivas.
- Visualización de tendencias mediante media móvil.
- Comparación de indicadores.
- Tabla de registros consultados.
- Descarga de información en formato CSV.

## Decisiones de visualización

Se eliminó el histograma porque, para analizar una serie de tiempo, no permite observar directamente su evolución ni su tendencia. En su lugar, se incorporó una media móvil ajustable, que ayuda a suavizar las fluctuaciones diarias y facilita la identificación del comportamiento general del indicador.

## Tecnologías utilizadas

- Python
- Streamlit
- Pandas
- Requests
- Plotly
- Matplotlib
- Seaborn
- API del Sistema de Información Económica de Banxico

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/tatugagy-cloud/HerramientasVisualizacion.git
```

2. Entrar a la carpeta:

```bash
cd HerramientasVisualizacion
```

3. Crear un entorno virtual:

```bash
python -m venv venv
```

4. Activar el entorno virtual en Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

5. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

## Configuración del token

Para consultar la API es necesario contar con un token de Banxico.

Crear el archivo:

`.streamlit/secrets.toml`

Agregar la siguiente configuración:

```toml
banxico_token = "TU_TOKEN_DE_BANXICO"
```

Importante: el archivo de credenciales no debe publicarse en GitHub.

## Ejecución

Iniciar el dashboard con:

```bash
streamlit run dashboard_banxico.py
```

La aplicación se abrirá en el navegador y permitirá interactuar con los indicadores financieros.

## Fuente de información

Banco de México - Sistema de Información Económica (SIE).

https://www.banxico.org.mx/SieAPIRest/service/v1/

## Evidencias

En la carpeta `evidencias/` se incluyen capturas de pantalla y material audiovisual que muestran el funcionamiento del dashboard.

## Autor

Proyecto académico.

Ingeniería en Datos e Inteligencia Artificial.

Universidad Politécnica de Querétaro.