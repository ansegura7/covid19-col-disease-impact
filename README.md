# Impact of Covid-19 in Colombia
Development and evaluation of mathematical and epidemiological models that support decision-making in response to the Covid-19 emergency in Colombia. The project was approached from the perspective of data science, using Data Analytics and Machine Learning techniques.

## Framework
The analytical framework proposed and implemented in this work, named ANE from “Analytics for NoCOVID Events” adapts the ASUM-DM (Analytics Solutions Unified Method for Data Mining) methodology to include and handle specific characteristic of health events and its data. The proposed framework can be seen in the following image.

![analytical-framework](https://github.com/ansegura7/covid19-col-disease-impact/blob/master/images/framework.png?raw=true)

## Implementation
The proposed analytical framework was mainly implemented in 2 software components:
1. <a href="https://github.com/ansegura7/covid19-col-disease-impact/tree/master/solution-desc">Descriptive Engine</a>
2. <a href="https://github.com/ansegura7/covid19-col-disease-impact/tree/master/solution-pred">Predictive Engine</a>

## Events / Diseases
The selected events on which the proposed framework was applied are:
1. Tuberculosis (TB)
2. Suicide Attempt (SA)
3. Infant Mortality (IM)
4. Diabetes Mellitus (DM)
5. Acute Diarrheal Disease (EDA)
6. Excess Mortality (EM)

Click <a href="https://github.com/ansegura7/covid19-col-disease-impact/tree/master/solution-desc/data" target="_blank">here</a> to view the dataset files for the descriptive solution.

Click <a href="https://github.com/ansegura7/covid19-col-disease-impact/tree/master/solution-pred/data" target="_blank">here</a> to view the dataset files for the predictive solution.

## Data
Primary sources:
- <a href="http://portalsivigila.ins.gov.co/Paginas/Vigilancia-Rutinaria.aspx" target="_blank">SIVIGILA</a>
- <a href="https://www.sispro.gov.co/Pages/Home.aspx" target="_blank">SISPRO</a>
- <a href="https://www.dane.gov.co/index.php/estadisticas-por-tema" target="_blank">DANE</a>
- <a href="https://www.datos.gov.co/Salud-y-Protecci-n-Social/Casos-positivos-de-COVID-19-en-Colombia/gt2j-8ykr" target="_blank">Colombia Open Data</a>

The data (both source and predictions) are up to date:
- Tuberculosis: 12/27/2020
- Suicide Attempt: 12/27/2020
- Infant Mortality: 4/12/2020
- Diabetes Mellitus: 4/12/2020
- Acute Diarrheal Disease: 4/12/2020
- Excess Mortality: 4/12/2020

## Dependencies
The project was carried out with the latest version of <a href="https://www.anaconda.com/products/individual" target="_blank" >Anaconda</a> on Windows.

The program can also be run on Linux with Python 3.7.x (or higher) by previously installing the following libraries:
```python
  sudo apt install
  sudo add-apt-repository universe
  sudo apt-get update
  sudo apt install python3-pandas
  sudo apt install python3-sklearn
  sudo apt install python3-statsmodels
```

## Author
- Created by <a href="https://github.com/ansegura7">Andrés Segura Tinoco</a>
- Created on Jul 15, 2020
- Last update on Sep 06, 2021

## Acknowledgements
We would like to make a special acknowledgement to the National Health Institute of Colombia.
