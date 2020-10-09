# Impact of Covid-19 in Colombia
Development and evaluation of mathematical and epidemiological models that support decision-making in response to the Covid-19 emergency in Colombia. The project was approached from the perspective of data science, using Data Analytics and Machine Learning techniques.

## Events / Diseases
- Tuberculosis (TB)
- Infant Mortality (IM)
- Suicide Attempt (SA)
- Mellitus Diabetes (MD)

## Data
Main sources:
- <a href="https://www.ins.gov.co/Direcciones/Vigilancia/Paginas/SIVIGILA.aspx" target="_blank">SIVIGILA</a>
- <a href="https://www.sispro.gov.co/Pages/Home.aspx" target="_blank">SISPRO</a>
- <a href="https://www.dane.gov.co/index.php/estadisticas-por-tema" target="_blank">DANE</a>

## Program setup
The behavior of the predictive engine is configured from an input YALM file.

```python
entity_filter: []
event_list: ['TUBERCULOSIS', 'INFANT_MORTALITY', 'SUICIDE_ATTEMPT', 'EXT_MATERNAL_MORBIDITY']
algo_type: ['PARTIAL', 'FULL']
perc_test: 0.20
n_forecast: 13
ci_alpha: 0.9
mape_threshold: 4.0
ts_tolerance: 4.0
```

## Dependencies
The project was carried out with the latest version of <a href="https://www.anaconda.com/distribution/" target="_blank" >Anaconda</a> on Windows.

## Author
- Created by <a href="https://github.com/ansegura7">Andrés Segura Tinoco</a>
- Created on Jul 25, 2020
- Last update on Oct 6, 2020
