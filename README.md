# Impact of Covid-19 in Colombia
Development and evaluation of mathematical and epidemiological models that support decision-making in response to the Covid-19 emergency in Colombia. The project was approached from the perspective of data science, using Data Analytics and Machine Learning techniques.

## Events / Diseases
- Tuberculosis (TB)
- Infant Mortality (IM)
- Suicide Attempt (SA)
- Diabetes Mellitus (DM)

Click <a href="https://github.com/ansegura7/covid19-col-disease-impact/tree/master/solution/data" target="_blank">here</a> to see the dataset files.

## Data
Main sources:
- <a href="https://www.ins.gov.co/Direcciones/Vigilancia/Paginas/SIVIGILA.aspx" target="_blank">SIVIGILA</a>
- <a href="https://www.sispro.gov.co/Pages/Home.aspx" target="_blank">SISPRO</a>
- <a href="https://www.dane.gov.co/index.php/estadisticas-por-tema" target="_blank">DANE</a>

## Program setup
The behavior of the predictive engine is configured from an input YALM file.

```python
event_list: ['TUBERCULOSIS']       # ['TUBERCULOSIS', 'INFANT_MORTALITY', 'SUICIDE_ATTEMPT', 'EXT_MATERNAL_MORBIDITY']
analysis_list: ['PARTIAL', 'FULL'] # ['PARTIAL', 'FULL']
entity_filter: []                  # ['COLOMBIA', 'ANTIOQUIA', 'CUNDINAMARCA', 'MEDELLIN', 'BOGOTA DC', 'CALI', 'BARRANQUILLA']
n_process: 1                       # 2, 4, 8
perc_test: 0.20                    # 0.1, 0.3
mape_threshold: 4.0                # 5.0, 10.0
ts_tolerance: 4.0                  # 3.0, 5.0
n_forecast: 13                     # 6
ci_alpha: 0.9                      # 0.8, 0.95
```

## Dependencies
The project was carried out with the latest version of <a href="https://www.anaconda.com/products/individual" target="_blank" >Anaconda</a> on Windows.

## Author
- Created by <a href="https://github.com/ansegura7">Andrés Segura Tinoco</a>
- Created on Jul 25, 2020
- Last update on Oct 20, 2020
