import krakenex
from pykrakenapi import KrakenAPI
import pandas as pd
import time
import os
import streamlit as st
import plotly.graph_objects as go
from PIL import Image
from plotly.subplots import make_subplots




##############################################################################################
######################## Generación del dataset a través de la api de Kraken #################
##############################################################################################

#Definimos las variables que utilizaremos para llamar a la API
api = krakenex.API()
k= KrakenAPI(api)

#Inicializamos el dataframe con datos de una moneda que no utilizaremos. Esto no es para nada eficiente, pero me evita
#problemas con respecto a crear un dataframe vacío y es un atajo para que funcione. Definimos los parámetros iniciales
#para la query.

pair = 'XDGUSD' #El par a consultar
interval = 1   #El intervalo es en minutos.
#Ponemos un timestamp de hace 10 años. Como sólo nos traerá los últimos 720 data points, es simplemente para asegurarnos
#de que nos traerá lo máximo posible.
start_time = int(1323212400)



#query para inicializar el df
df, last = k.get_ohlc_data(pair,interval, ascending=True)

#sustituimos el 'time' por el índice, ya que dicho campo viene en formato Timestamp y no se lee fácil.
df['time'] = df.index

#reseteamos índice para no tener la fecha dos veces.
df.reset_index(drop=True, inplace=True)

#Pasamos a numéricos todos los campos menos la fecha.
df[['open', 'high', 'low', 'close', 'vwap', 'volume']] = df[['open', 'high', 'low', 'close', 'vwap', 'volume']].apply(pd.to_numeric)

#Generamos el campo 'coin', que nos permitirá filtrar por moneda los datos a mostrar.
df['coin'] = 'DOGE-USD'

#Generamos el campo 'intervalo', que nos permitirá filtrar por intervalo los datos a mostrar.
df['interval']= 1


#Un sleep para que la API no nos corte
time.sleep(2)

#Definimos el dataset 'coinselect' con 2 columnas:
#La primera sirve como selector en streamlit de la moneda a visualizar.
#La segunda es la que utilizaremos para filtrar el dataset

coinselect = pd.DataFrame({'Coin':['BTC-USD','ETH-USD'],
                          'Pair':['XXBTZUSD','XETHZUSD']
                          })

#las opciones del selector de intervalos en el dashboard.
#intervalselect = [1, 5, 15, 30]
intervalselect = pd.DataFrame({'selector':["1 minuto", "5 minutos", "15 minutos", "30 minutos","1 hora","1 día"], 'intervalo':[1, 5, 15, 30,60, 1440]})

#Definimos la función que nos servirá para realizar la query a la API.
def kquery(pair, interval, since):
    newquery, last = k.get_ohlc_data(pair, interval, since=since, ascending=True)
    return newquery

#Este bucle nos genera el dataset por par e intervalo que alimentará nuestro dashboard, utilizando la función 'kquery'
#previamente definida. Soy consciente que no es el método más eficiente ni escalable para hacerlo, pero es el que me
#ha resultado más sencillo con el margen de tiempo del que dispongo.

for coin in coinselect['Pair']:
    for interv in intervalselect['intervalo']:

        nq = pd.DataFrame(kquery(coin,interv, start_time))
        # newquery, last = k.get_ohlc_data(coin, interv, since=start_time, ascending=True)
        # nq = pd.DataFrame(newquery)
        nq['time'] = nq.index
        nq.reset_index(drop=True, inplace=True)
        nq['coin'] = coin
        nq['interval'] = interv
        df = pd.concat([df, nq])
        time.sleep(2)

#######################################
########CALCULO VWAP###################
#Aquí sustituimos el VWAP que venía en los datos de la API por el que vamos a calcular

#Definimos una función vwap que haga los cálculos y la aplicamos con un apply agrupado por moneda e intervalo al dataset

def vwap(df):
    sum_vol = df['volume'].values
    sum_price = ((df['high'] + df['low'] + df['close'] ) /3).values
    return df.assign(vwap=(sum_vol * sum_price).cumsum() / sum_vol.cumsum())

df = df.groupby(['coin','interval']).apply(vwap)




#################################################################################
#################### Elementos de streamlit #####################################

#Cargamos el path de la imagen que utilizaremos como título en nuestra aplicación

script_dir = os.path.dirname(__file__) #path de la aplicación dentro del sistema
rel_path = "../assets/Easycrypto.png" #path de la imagen en el directorio de la aplicación
abs_file_path = os.path.join(script_dir, rel_path) #concatenamos los dos anteriores

#Metemos la imagen en una variable y la llamamos con streamlit
image = Image.open(abs_file_path)
st.image(image)

#Incluimos un subheader que aparecerá justo debajo de la imagen
st.subheader("La información de las cryptomonedas más populares")

#Estos serían los selectores que aparecerán en el sidebar de la izquierda en nuestra aplicación, y cuyo valor filtrarán
#el dataset.
coin_sel = st.sidebar.selectbox(
    '¿Qué criptomoneda quieres ver?',
    coinselect['Coin'])

inter_sel = st.sidebar.selectbox(
    "Intervalo de las velas",
    intervalselect['selector'])

#Esta línea nos permite filtrar el dashboard por moneda e intervalo en base a los selectores de streamlit.
df_filtered = df.loc[(df["interval"] == intervalselect.loc[intervalselect['selector']==inter_sel, 'intervalo'].iloc[0])&(df["coin"] == coinselect.loc[coinselect['Coin']== coin_sel, 'Pair'].iloc[0])]



############################################################################
################### Gráficas ##############################################

#Vamos a generar 3 subplots: uno para las velas, otro de línea para VWAP y otro de barras para el volumen, este último
#con un eje Y diferente.

try:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Candlestick(name='OHLC',
            x=df_filtered['time'],
            open=df_filtered['open'],
            high=df_filtered['high'],
            low=df_filtered['low'],
            close=df_filtered['close']),
        secondary_y=True
        )



    fig.add_trace(
        go.Scatter(name='VWAP',
            x=df_filtered['time'],
            y=df_filtered['vwap']),
        secondary_y=True
        )

    fig.add_trace(
        go.Bar(name='volumen',
            x=df_filtered['time'],
            y=df_filtered['volume']),
        secondary_y=False
        )

except:
    st.error("Ha habido un error al generar las gráficas.")

#Ajustamos algunos parámetros estéticos de los gráficos
fig.update_layout(
    title_text='Cotización de '+ coin_sel,  # title of plot
    bargap=0.01,
    showlegend=True,

    xaxis=dict(
        showticklabels=True
    ),
    yaxis=dict(
        showticklabels=True
    ),

    yaxis2=dict(
        title="Precio (USD)",
        side="right"
    )
)

fig.update_layout(height=600)
fig.update_layout(width=800)
fig.update_yaxes(title_text="Volumen", showgrid=False, secondary_y=False)

#Añadimos la botonera para poder dibujar líneas
config = {
    'modeBarButtonsToAdd': ['drawline']
}

st.plotly_chart(fig, use_container_width=False, config=config)



#########################


