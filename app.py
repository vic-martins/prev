import pandas as pd
import numpy as np
import datetime as dt
from datetime import date, datetime

#from prophet import Prophet
#from prophet.plot import plot_plotly, plot_components_plotly

import plotly.graph_objects as go
from plotly.colors import n_colors
import plotly.express as px
import plotly.offline as pyo
pyo.init_notebook_mode()

import streamlit as st

st.set_page_config(
    page_title= "🔮",
    layout="wide",
    initial_sidebar_state="expanded")

st.markdown('''
# Previsões 🔮
Victor Martins
''')

df = pd.read_csv('forecast.csv')

df = df.rename(columns={'y': 'real',
                        'yhat': 'previsto',
                        'ds': 'data'})

df['data'] = pd.to_datetime(df['data'])

df = df.loc[~df['data'].dt.year.isin([2020, 2021])]

fig = px.scatter(df, 
                 x='data', 
                 y='real',
                 color_discrete_sequence=px.colors.qualitative.Alphabet[::-1])

fig.add_trace(go.Line(x=df['data'], 
                      y=df['previsto'], 
                      line=dict(color='black'),
                      name='Ajuste'))

fig.add_trace(go.Line(x=df['data'], 
                      y=df['yhat_upper'], 
                      line=dict(color='slategray', dash='dot'),
                      opacity=0.7,
                      showlegend=False))

fig.add_trace(go.Line(x=df['data'], 
                      y=df['yhat_lower'], 
                      line=dict(color='slategray', dash='dot'),
                      opacity=0.7,
                      showlegend=False))


fig.update_traces(marker=dict(size=5))

fig.update_xaxes(title_text='Data')
fig.update_yaxes(title_text='y')

fig.update_layout(title='Ajuste do modelo',
                  height=500, 
                  width=1200)

st.plotly_chart(fig)

df23 = df.loc[df['data'].dt.year==2023]

soma_previsoes = sum(df23['previsto'])

st.write('**Soma das previsões:**') 
st.write(soma_previsoes)

df23['geom_dist'] = df23['previsto'] / soma_previsoes

valor_dist = st.number_input('Insira o montante', min_value=100000, max_value=10000000, value=1000000, step=100000)

df23['dist_custom'] = df23['geom_dist'] * valor_dist

mae = 3613

df23['yhat_upper'] = df23['dist_custom'] + mae
df23['yhat_lower'] = df23['dist_custom'] - mae
df23.loc[df23['yhat_lower'] < 0, 'yhat_lower'] = 0

fig = go.Figure()

fig.add_trace(go.Line(x=df23['data'], 
                      y=df23['dist_custom'], 
                      line=dict(color='deeppink'),
                      name='Cenário'))

fig.add_trace(go.Line(x=df23['data'], 
                      y=df23['yhat_upper'], 
                      line=dict(color='slategray', dash='dot'),
                      opacity=0.7,
                      showlegend=False))

fig.add_trace(go.Line(x=df23['data'], 
                      y=df23['yhat_lower'], 
                      line=dict(color='slategray', dash='dot'),
                      opacity=0.7,
                      showlegend=False))

fig.update_layout(title='Curva customizada',
                  height=500, 
                  width=1200)

st.plotly_chart(fig)

