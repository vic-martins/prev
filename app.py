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

feriados = pd.to_datetime([
    '2023-02-20', '2023-02-21', '2023-02-22',
    '2023-04-09', '2023-04-21',
    '2023-05-01', 
    '2023-06-08',
    '2023-07-09',
    '2023-10-12',
    '2023-11-02', '2023-11-15', '2023-11-20',
    '2023-12-25',
])

df.loc[df['data'].isin(feriados), 'yhat'] = 0

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
                         step=100000)

cen2= c2.text_input("Nome do cenário 2", value='Realista')
valor2= c2.number_input("Montante 2",
                         value=1000000,
                         min_value=100000,
                         max_value=10000000,
                         step=100000)

cen3 = c3.text_input("Nome do cenário 3", 'Otimista')
valor3 = c3.number_input("Montante 3",
                         value=1300000,
                         min_value=100000,
                         max_value=10000000,
                         step=100000)

mae = 2999

fig = go.Figure()

limite = st.number_input("Limite",
                         value=25000,
                         min_value=100,
                         max_value=1000000,
                         step=100)

achatar = st.sidebar.checkbox('Achatar a curva')
picos = st.sidebar.checkbox('Denotar picos')

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

def GeraCurva(df, cen, valor, limite, cor, h):
    df['dist_' + cen] = df['geom_dist'] * valor
    df['yhat_upper_' + cen] = df['dist_' + cen] + mae
    df['yhat_lower_' + cen] = df['dist_' + cen] - mae
    df.loc[df['yhat_lower_' + cen] < 0, 'yhat_lower_' + cen] = 0
    
    if achatar == True:
        df = Redistribui('dist_', cen, df, limite)
        if df['topou' + cen].sum()>0:
            topo = df.loc[df['topou' + cen] == 1]
            inicio = str(topo['data'].loc[topo['data'].idxmin()].date())
            fim = str(topo['data'].loc[topo['data'].idxmax()].date())
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
        df = Redistribui('yhat_upper_', cen, df, limite)
        df = Redistribui('yhat_lower_', cen, df, limite)
        
    fig.add_hline(
        y=limite,
        line_color=cor,
        line_dash='dot',
        annotation_text='Limite',
        annotation_position='bottom right')

    fig.add_trace(
        go.Line(x=df['data'],
                y=df['dist_' + cen],
                line=dict(color=cor),
                name=cen))
    fig.add_trace(
        go.Line(x=df['data'],
                y=df['yhat_upper_' + cen],
                line=dict(color=cor, dash='dot'),
                opacity=0.2,
                name='limiar superior'))
    fig.add_trace(
        go.Line(x=df['data'],
                y=df['yhat_lower_' + cen],
                line=dict(color=cor, dash='dot'),
                opacity=0.2,
                name='limiar inferior'))
    return df

colors = px.colors.qualitative.Alphabet

if st.button("Gerar distribuição de cenários"):
    df23 = GeraCurva(df23, cen1, valor1, limite, colors[1], -40)
    df23 = GeraCurva(df23, cen2, valor2, limite, colors[2], -60)
    df23 = GeraCurva(df23, cen3, valor3, limite, colors[3], -80)
    fig.update_layout(title='Curvas customizadas', height=500, width=1200)
    st.plotly_chart(fig)
    
montante = st.number_input(
    "Montante",
    value=1000000,
    min_value=100000,
    max_value=10000000,
    step=100000)

c1, c2, c3, c4, c5, c6 = st.columns(6)

g1 = c1.text_input("Nome 1", value='1')
pct1 = c1.number_input("Porcentagem 1",
                         value=40,
                         min_value=0,
                         max_value=100,
                         step=5)

g2= c2.text_input("Nome 2", value='2')
pct2= c2.number_input("Porcentagem 2",
                         value=30,
                         min_value=0,
                         max_value=100,
                         step=5)

g3 = c3.text_input("Nome 3", '3')
pct3 = c3.number_input("Porcentagem 3",
                         value=10,
                         min_value=0,
                         max_value=100,
                         step=5)

g4 = c4.text_input("Nome 4", value='4')
pct4 = c4.number_input("Porcentagem 4",
                         value=10,
                         min_value=0,
                         max_value=100,
                         step=5)

g5 = c5.text_input("Nome 5", value='5')
pct5 = c5.number_input("Porcentagem 5",
                         value=5,
                         min_value=0,
                         max_value=100,
                         step=5)

g6 = c6.text_input("Nome 6", value='6')

pct6 = c6.number_input(
    "Porcentagem 6",
    value=5,
    min_value=0,
    max_value=100,
    step=5)

if st.button("Gerar distribuições de curvas"):
    fig = go.Figure()
    if pct1>0:
        df23 = GeraCurva(df23, g1, (pct1/100)*montante, (pct1/100)*limite, colors[-1], -60)
    if pct2>0:
        df23 = GeraCurva(df23, g2, (pct2/100)*montante, (pct2/100)*limite, colors[-2], -60)
    if pct3>0:
        df23 = GeraCurva(df23, g3, (pct3/100)*montante, (pct3/100)*limite, colors[-3], -60)
    if pct4>0:
        df23 = GeraCurva(df23, g4, (pct4/100)*montante, (pct4/100)*limite, colors[-4], -60)
    if pct5>0:
        df23 = GeraCurva(df23, g5, (pct5/100)*montante, (pct5/100)*limite, colors[-5], -60)
    if pct6>0:
        df23 = GeraCurva(df23, g6, (pct6/100)*montante, (pct6/100)*limite, colors[-6], -60)
    fig.update_layout(title='Curvas customizadas', height=500, width=1200)
    st.plotly_chart(fig)

