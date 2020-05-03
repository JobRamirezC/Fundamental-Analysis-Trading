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

pio.renderers.default = "browser"  # render de imagenes para correr en script


# -- ----------------------------------------- Grafica: Serie de tiempo -- #
# -- Graficar serie de tiempo
def g_serie_tiempo(ventana):
    fig = go.Figure()
    df_ventana = datos.load_pickle_file('datos/ventanas_historicos.pkl')['historicos_sucesos'][ventana]

    fig.add_trace(go.Scatter(x=df_ventana.TimeStamp, y=df_ventana.Close,
                             mode='lines'))

    # Cambiar titulo y ejes
    fig.update_layout(title={'text': 'Historico GBP_USD',
                             'y': 0.95,
                             'x': 0.5,
                             'xanchor': 'center',
                             'yanchor': 'top'},
                      xaxis_title='Date',
                      yaxis_title='$$$',
                      font=dict(
                          family="Courier New, monospace",
                          size=18,
                          color="#7f7f7f"),
                      showlegend=True)
    fig.show()


# -- ----------------------------------------- Grafica: Datos atípicos -- #
# -- Graficar para detectar valores atípicos de la serie
def g_statistics(df_timeseries):
    fig = make_subplots(rows=2, cols=1)
    fig.add_trace(go.Box(y=df_timeseries['Close'],
                         boxpoints='suspectedoutliers',  # only suspected outliers
                         marker=dict(
                             color='rgb(8,81,156)',
                             outliercolor='rgba(219, 64, 82, 0.6)',
                             line=dict(
                                 outliercolor='rgba(219, 64, 82, 0.6)',
                                 outlierwidth=2)),
                         line_color='rgb(8,81,156)',
                         name='Distribucion y Atípicos'
                         ), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_timeseries.index, y=df_timeseries['Close'],
                             mode='lines',
                             name='GBP_USD'), row=1, col=1)
    fig.show()
