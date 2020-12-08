# Impact of Covid-19 in Colombia
Development and evaluation of mathematical and epidemiological models that support decision-making in response to the Covid-19 emergency in Colombia. The project was approached from the perspective of data science, using Data Analytics and Machine Learning techniques.

## Events / Diseases
- Tuberculosis (TB)
- Infant Mortality (IM)
- Suicide Attempt (SA)
- Diabetes Mellitus (DM)
- Acute Diarrheal Disease (EDA)
- Excess Mortality (EM)

Click <a href="https://github.com/ansegura7/covid19-col-disease-impact/tree/master/solution-pred/data" target="_blank">here</a> to see the dataset files.

## Data
Main sources:
- <a href="http://portalsivigila.ins.gov.co/Paginas/Vigilancia-Rutinaria.aspx" target="_blank">SIVIGILA</a>
- <a href="https://www.sispro.gov.co/Pages/Home.aspx" target="_blank">SISPRO</a>
- <a href="https://www.dane.gov.co/index.php/estadisticas-por-tema" target="_blank">DANE</a>
- <a href="https://www.datos.gov.co/Salud-y-Protecci-n-Social/Casos-positivos-de-COVID-19-en-Colombia/gt2j-8ykr" target="_blank">Datos Abiertos</a>

## Program setup
The behavior of the predictive engine is configured from an input JSON file.

```json
{
  "event_list": [
    {
      "analysis_list": [ "PARTIAL", "FULL" ],
      "ci_alpha": 0.9,
      "enabled": true,
      "full_init_date": "2017-01-01",
      "mape_threshold": 4.0,
      "n_forecast": 13,
      "name": "TUBERCULOSIS",
      "partial_end_date": "2019-12-27",
      "perc_test": 0.20,
      "ts_tolerance": 4.0
    },
    {
    
    }
  ],
  "entity_filter": ["COLOMBIA", "BOGOTA DC", "ANTIOQUIA"],
  "n_process": 1
}
```

## Dependencies
The project was carried out with the latest version of <a href="https://www.anaconda.com/products/individual" target="_blank" >Anaconda</a> on Windows.

## Author
- Created by <a href="https://github.com/ansegura7">Andrés Segura Tinoco</a>
- Created on Jul 25, 2020
- Last update on Dec 08, 2020
