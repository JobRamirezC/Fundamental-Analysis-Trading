# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Proyecto Final - Sistema de Trading
# -- archivo: funciones.py - funciones diversas utilizadas en el proyecto
# -- mantiene: IF Hermela Peña, IF Manuel Pintado
# -- repositorio: https://github.com/manuelpintado/Proyecto_Equipo_6.git
# -- ------------------------------------------------------------------------------------ -- #

# Importar librerias
import numpy as np


# -- --------------------------------------------------------- FUNCION: Condiciones  -- #
# -- Condiciones para que se cumplan los diferentes escenarios de sucesos

def condition(actual, consensus, previous):
    """
    :param actual: movimiento real del mercado
    :param consensus: movimiento esperado del mercado
    :param previous: movimiento anterior del mercado ante la noticia
    :return: df con escenario A, B, C o D

    Debugging
    --------
    actual = 1000
    consensus = 950
    previous = 900
    """
    if actual >= consensus >= previous:
        return 'A'
    elif actual >= consensus < previous:
        return 'B'
    elif actual < consensus >= previous:
        return 'C'
    else:
        return 'D'


# -- --------------------------------------------------------- FUNCION: Conclusiones  -- #
# -- Conclusiones generales para cada ventana de tiempo

def conclusiones_generales(df_ventana, fecha):
    """
    :param df_ventana: data frame de la ventana de 30 min despues de el anuncio de la tasa de desempleo
    :param fecha: fecha que inicia la ventana de tiempo
    :return: conclusion en base a datos generales de la ventana

    Debugging
    --------
    from datos import load_pickle_file
    fecha = '2018-06-01 12:30:00'
    ventana = fecha
    df_ventana = load_pickle_file('datos/ventanas_historicos.pkl')['historicos_sucesos'][ventana]
    """
    max_point = df_ventana['High'].max()
    min_point = df_ventana['Low'].min()
    volatilidad = np.round((max_point - min_point) * 10000, 2)
    if df_ventana['Open'][0] < df_ventana['Close'].iloc[-1]:
        ventana = 'alcista'
    else:
        ventana = 'bajista'

    pips_alcistas = np.round((max_point - df_ventana['Open'][0]) * 10000, 2)
    pips_bajistas = np.round((df_ventana['Open'][0] - min_point) * 10000, 2)
    conclusion = 'La ventana de la fecha {} tiene un movimiento {}. \n' \
                 'El punto maximo alcanzado por la ventana es de {}.\n' \
                 'El punto minimo de la ventana es de {}.\n' \
                 'La volatilidad observada en la ventana es de {} pips.\n' \
                 'De la apertura al maximo de la ventana hay {} pips,' \
                 ' al minimo de la ventana hay {} pips.\n\n'.format(fecha, ventana, np.round(max_point, 5),
                                                                   np.round(min_point, 5), volatilidad,
                                                                   pips_alcistas, pips_bajistas)
    return conclusion


# -- --------------------------------------------------------- FUNCION: Sharp  -- #
# -- Funcion para el radio de sharp

def sharp(df_portfolio, rf: float = 0.08):
    """
    :param df_portfolio: dataframe con el capital acumulado del portafolio
    :param rf: tasa libre de riesgo de EUA
    :return: radio de sharp

    Debugging
    --------
    """
    log_returns = np.log(df_portfolio.capital_acm / df_portfolio.capital_acm.shift()).dropna()
    port_ret = np.sum(log_returns)
    port_std = log_returns.std()
    sharp = (port_ret - rf) / port_std
    return sharp