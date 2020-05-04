# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Proyecto Final - Sistema de Trading
# -- archivo: visualizaciones.py - funciones para visualización de datos
# -- mantiene: IF Hermela Peña, IF Manuel Pintado
# -- repositorio: https://github.com/manuelpintado/Proyecto_Equipo_6.git
# -- ------------------------------------------------------------------------------------ -- #

# Importar librerias
import plotly.graph_objects as go  # Libreria para graficar
import plotly.io as pio  # renderizador para visualizar imagenes
from plotly.subplots import make_subplots  # crear subplots con plotly
import datos
import numpy as np
from datetime import datetime

pio.renderers.default = "browser"  # render de imagenes para correr en script


# -- ----------------------------------------- Grafica: Serie de tiempo -- #
# -- Graficar serie de tiempo
def g_serie_tiempo(ventana):
    """
    :param ventana: fecha en la que se emitio el indicador en formato 'aaaa/mm/dd HH:MM:SS'
    :return: grafica de la serie de tiempo de la ventana con otras lineas

    Debugging
    --------
    ventana='2019-06-07 12:30:00'
    """
    fig = go.Figure()
    df_ventana = datos.load_pickle_file('datos/ventanas_historicos.pkl')['historicos_sucesos'][ventana]

    fig.add_trace(go.Candlestick(x=df_ventana['TimeStamp'], open=df_ventana['Open'], high=df_ventana['High'],
                                 low=df_ventana['Low'], close=df_ventana['Close'],
                                 name='Exchange Rate'))

    # maximo de la ventana
    max_point = df_ventana['High'].max()
    max_point_index = df_ventana['High'].idxmax(axis=0)
    if max_point > df_ventana['Open'][0] and max_point_index != 0:
        m = (max_point - df_ventana['Open'][0]) / (max_point_index - df_ventana.index[0])
        O2H_values = np.array([i * m + df_ventana['Open'][0] for i in range(0, max_point_index + 1)])
        O2H_dates = np.array([df_ventana['TimeStamp'][i] for i in range(0, max_point_index + 1)])
        fig.add_trace(go.Scatter(x=O2H_dates, y=O2H_values,
                                 mode='lines',
                                 name='Open to Max'))

    # anotacion del maximo
    fig.add_annotation(x=df_ventana['TimeStamp'][max_point_index], y=max_point,
                       text='max = {}'.format(max_point))

    # minimo de la ventana
    min_point = df_ventana['Low'].min()
    min_point_index = df_ventana['Low'].idxmin(axis=0)
    if min_point < df_ventana['Open'][0] and min_point_index != 0:
        m = (min_point - df_ventana['Open'][0]) / (min_point_index - df_ventana.index[0])
        O2L_values = np.array([i * m + df_ventana['Open'][0] for i in range(0, min_point_index + 1)])
        O2L_dates = np.array([df_ventana['TimeStamp'][i] for i in range(0, min_point_index + 1)])
        fig.add_trace(go.Scatter(x=O2L_dates, y=O2L_values,
                                 mode='lines',
                                 name='Open to Min'))

    # anotacion del minimo
    fig.add_annotation(x=df_ventana['TimeStamp'][min_point_index], y=min_point,
                       text='min = {}'.format(min_point))

    # volatilidad de la ventana
    fig.add_trace(go.Scatter(x=[df_ventana['TimeStamp'][15], df_ventana['TimeStamp'][15]], y=[max_point, min_point],
                             mode='lines',
                             name='Volatility'))

    # anotacion de volatilidad
    fig.add_annotation(x=df_ventana['TimeStamp'][15], y=(max_point + min_point) / 2,
                       text='Volatilidad en pips = {}'.format(np.round((max_point - min_point) * 10000), 2))

    # Cambiar titulo y ejes
    fig.update_layout(title={'text': 'Historico GBP_USD OHLC {}'.format(
        datetime.strptime(ventana, '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y')),
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        xaxis_title='Time',
        yaxis_title='$$$',
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"),
        showlegend=True)

    fig.update_xaxes(rangeslider_visible=False)
    fig.show()


# -- ----------------------------------------- Grafica: Datos atípicos -- #
# -- Graficar para detectar valores atípicos de la serie
def g_statistics(df_indicador):
    """
    :param df_indicador:
    :return:

    Debugging
    --------
    ventana='2019-06-07 12:30:00'
    """
    fig = go.Figure()
    # Box Actual
    fig.add_trace(go.Box(y=df_indicador['Actual'],
                         boxpoints='suspectedoutliers',  # only suspected outliers
                         marker=dict(
                             color='rgb(8,81,156)',
                             outliercolor='rgba(219, 64, 82, 0.6)',
                             line=dict(
                                 outliercolor='rgba(219, 64, 82, 0.6)',
                                 outlierwidth=2)),
                         line_color='rgb(8,81,156)',
                         name='Actual'))

    # Box Consensus
    fig.add_trace(go.Box(y=df_indicador['Consensus'],
                         boxpoints='suspectedoutliers',  # only suspected outliers
                         marker=dict(
                             color='rgb(8,81,156)',
                             outliercolor='rgba(205, 50, 90, 0.6)',
                             line=dict(
                                 outliercolor='rgba(205, 50, 90, 0.6)',
                                 outlierwidth=2)),
                         line_color='rgb(0,200,85)',
                         name='Consensus'))
    # Cambiar titulo y ejes
    fig.update_layout(title={'text': 'Distribucion Datos',
                             'y': 0.95,
                             'x': 0.5,
                             'xanchor': 'center',
                             'yanchor': 'top'},
                      xaxis_title='Serie',
                      yaxis_title='Tasa de Desempleo en %',
                      font=dict(
                          family="Courier New, monospace",
                          size=18,
                          color="#7f7f7f"),
                      showlegend=True)
    fig.show()
