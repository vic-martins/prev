import pandas as pd
import numpy as np
import datetime as dt
from datetime import date, datetime

#from prophet import Prophet
#from prophet.plot import plot_plotly, plot_components_plotly

import plotly.graph_objects as go
from plotly.colors import n_colors
import plotly.express as px

import streamlit as st

st.set_page_config(page_title="🔮",
                   layout="wide",
                   initial_sidebar_state="expanded")

st.markdown('''
# Previsões 🔮
Victor Martins
''')

#@st.cache()
df = pd.read_csv('forecast.csv')

df = df.rename(columns={'y': 'real', 'yhat': 'previsto', 'ds': 'data'})

df['data'] = pd.to_datetime(df['data'])

df = df.loc[~df['data'].dt.year.isin([2020, 2021])]

fig = px.scatter(df,
                 x='data',
                 y='real',
                 color_discrete_sequence=px.colors.qualitative.Alphabet[::-1])

fig.add_trace(
    go.Line(x=df['data'],
            y=df['previsto'],
            line=dict(color='black'),
            name='Ajuste'))

fig.add_trace(
    go.Line(x=df['data'],
            y=df['yhat_upper'],
            line=dict(color='slategray', dash='dot'),
            opacity=0.7,
            showlegend=False))

fig.add_trace(
    go.Line(x=df['data'],
            y=df['yhat_lower'],
            line=dict(color='slategray', dash='dot'),
            opacity=0.7,
            showlegend=False))

fig.update_traces(marker=dict(size=5))

fig.update_xaxes(title_text='Data')
fig.update_yaxes(title_text='y')

fig.update_layout(title='Ajuste do modelo', height=500, width=1200)

st.plotly_chart(fig)

df23 = df.loc[df['data'].dt.year == 2023]

soma_previsoes = sum(df23['previsto'])

st.write('**Soma das previsões:**')
st.write(soma_previsoes)

df23['geom_dist'] = df23['previsto'] / soma_previsoes

# Create an empty dictionary

cenarios = {}

c1, c2, c3 = st.columns(3)

cen1 = c1.text_input("Nome do cenário 1", value='Pessimista')
valor1 = c1.number_input("Montante 1",
                         value=800000,
                         min_value=100000,
                         max_value=10000000,
                         step=1000000)

cen2= c2.text_input("Nome do cenário 2", value='Realista')
valor2= c2.number_input("Montante 2",
                         value=1000000,
                         min_value=100000,
                         max_value=10000000,
                         step=1000000)

cen3 = c3.text_input("Nome do cenário 3", 'Otimista')
valor3 = c3.number_input("Montante 3",
                         value=1300000,
                         min_value=100000,
                         max_value=10000000,
                         step=1000000)

mae = 3613

fig = go.Figure()

limite = st.number_input("Limite",
                         value=25000,
                         min_value=100,
                         max_value=1000000,
                         step=100)
achatar = st.checkbox('Achatar a curva')
picos = st.checkbox('Denotar picos')

fig.add_hline(y=limite,
              line_dash='dot',
              annotation_text='Limite',
              annotation_position='bottom right')


def Redistribui(col, cen, df, limite):
    col = col + cen
    dif = 0
    df['topou' + cen] = 0
    for data in df['data'][::-1]:
        df.loc[df['data'] == data, col] = df[col] + dif
        pred = df[col].loc[df['data'] == data].item()
        if pred > limite:
            df.loc[df['data'] == data, 'topou' + cen] = 1
            df.loc[df['data'] == data, col] = limite
            dif = pred - limite
        else:
            dif = 0
    return df

def GeraCurva(df, cen, valor, cor, h):
    df['dist_' + cen] = df['geom_dist'] * valor
    df['yhat_upper_' + cen] = df['dist_' + cen] + mae
    df['yhat_lower_' + cen] = df['dist_' + cen] - mae
    df.loc[df['yhat_lower_' + cen] < 0, 'yhat_lower_' + cen] = 0
    
    if achatar == True:
        df = Redistribui('dist_', cen, df, limite)
        topo = df.loc[df['topou' + cen] == 1]
        inicio = str(topo['data'].loc[topo['data'].idxmin()].date())
        fim = str(topo['data'].loc[topo['data'].idxmax()].date())
        df = Redistribui('yhat_upper_', cen, df, limite)
        df = Redistribui('yhat_lower_', cen, df, limite)
        if picos == True:
            fig.add_annotation(x=inicio,
                       y=limite,
                       text=inicio[5:],
                       showarrow=True,
                       arrowhead=1,
                       ax=-15,
                       ay=h,
                       arrowcolor=cor)
            fig.add_annotation(x=fim,
                               y=limite,
                               text=fim[5:],
                               showarrow=True,
                               arrowhead=1,
                               ax=15,
                               ay=h,
                               arrowcolor=cor)
    
    fig.add_trace(
        go.Line(x=df['data'],
                y=df['dist_' + cen],
                line=dict(color=cor),
                name='Cenário ' + cen))
    fig.add_trace(
        go.Line(x=df['data'],
                y=df['yhat_upper_' + cen],
                line=dict(color=cor, dash='dot'),
                opacity=0.2,
                showlegend=False))
    fig.add_trace(
        go.Line(x=df['data'],
                y=df['yhat_lower_' + cen],
                line=dict(color=cor, dash='dot'),
                opacity=0.2,
                showlegend=False))
    return df

if st.button("Gerar distribuições"):
    df23 = GeraCurva(df23, cen1, valor1, 'deeppink', -40)
    df23 = GeraCurva(df23, cen2, valor2, 'red', -60)
    df23 = GeraCurva(df23, cen3, valor3, 'pink', -80)
    fig.update_layout(title='Curvas customizadas', height=500, width=1200)
    st.plotly_chart(fig)
