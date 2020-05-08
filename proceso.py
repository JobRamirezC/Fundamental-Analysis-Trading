# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Proyecto Final - Sistema de Trading
# -- archivo: proceso.py - funciones para procesamiento de datos
# -- mantiene: IF Hermela Peña, IF Manuel Pintado
# -- repositorio: https://github.com/manuelpintado/Proyecto_Equipo_6.git
# -- ------------------------------------------------------------------------------------ -- #

# Importar librerias
import datos
import funciones as fn
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.diagnostic import het_arch
from scipy.stats import shapiro

# -- ----------------------------------------- FUNCION: Dicky Fuller Aumentada -- #
# -- Encontrar estacionariedad de la serie
def f_a_dicky_fuller(df_indicador):
    """
    :param df_indicador: dataframe de serie de tiempo indicador
    :return: pueba dick fuller aumentada e impresion de parametros hasta rechazar H0. nivelde confianza 95%

    Debugging
    --------
    df_indicador = datos.f_leer_archivo(file_path='datos/Unemployment Rate - United States.csv')
    """
    serie = df_indicador
    a_dicky_fuller = adfuller(serie.Actual)
    print('ADF Statistic: %f' % a_dicky_fuller[0])
    print('p-value: %f' % a_dicky_fuller[1])
    print('Critical Values:')
    for key, value in a_dicky_fuller[4].items():
        print('\t%s: %.3f' % (key, value))

    i = 1
    while a_dicky_fuller[1] > 0.05:
        serie['Actual'] = serie['Actual'].diff()
        serie.dropna(inplace=True)
        a_dicky_fuller = adfuller(serie.Actual)
        print('\n Transformada {}'.format(i))
        print('ADF Statistic: %f' % a_dicky_fuller[0])
        print('p-value: %f' % a_dicky_fuller[1])
        print('Critical Values:')
        for key, value in a_dicky_fuller[4].items():
            print('\t%s: %.3f' % (key, value))
        i += 1
        serie.reset_index(inplace=True)
    return a_dicky_fuller


# -- ----------------------------------------- FUNCION: Normalidad -- #
# -- Encontrar si la serie es normal

def f_normalidad(df_indicador):
    """
    :param df_indicador: dataframe de la serie de tiempo del indicador
    :return: informacion de la prueba de shapiro (t-stat y p-value)

    Debugging
    --------
    df_indicador = datos.f_leer_archivo(file_path='datos/Unemployment Rate - United States.csv')
    """
    shapiro_results = shapiro(df_indicador.Actual)
    print('Prueba de normalidad: \n'
          ' H0: La serie es normal \n'
          ' H1: La serie no es normal \n')
    if shapiro_results[1] <= 0.05:
        print('P-value: {}'.format(shapiro_results[1]))
        print('Se rechaza la H0, la serie no es normal')
    else:
        print('P-value: {}'.format(shapiro_results[1]))
        print('Se acepta la H0, la serie es normal')

    return shapiro_results


# -- ----------------------------------------- FUNCION: ARCH -- #
# -- Encontrar autoregresion

def f_heterocerasticidad(df_residuals):
    """
    
    Parameters
    ----------
    df_indicador

    Returns
    -------

    """
    arch = het_arch(df_residuals)
    pass


# -- ----------------------------------------- FUNCION: Estacionalidad -- #
# -- Encontrar estacionalidad

def f_estacionalidad(df_indicador):
    """
    :param df_indicador: datos del indicador que sean estacionarios
    :return: descomposicion de la serie para ver estacionalidad

    Debugging
    --------
    df_indicaros = df_indicador
    """
    resultado = seasonal_decompose(df_indicador['Actual'], period=1)
    return resultado


# -- --------------------------------------------------------- FUNCION: Cargar y clasificar -- #
# -- Cargar archivo de historico indicador y clasificar cada ocurrencia

def f_clasificacion_ocurrencias(file_path: str, columns=None):
    """
    :param file_path: lugar donde esta ubicado el archivo de los datos historicos del indicador
    :param columns: columnas a tomar del archivo (opcional)
    :return: dataframe del archivo agregando la clasificacion de cada ocurrencia

    Debugging
    --------
    file_path = 'datos/Unemployment Rate - United States.csv'
    """
    # Cargar información de archivos
    df_indicador = datos.f_leer_archivo(file_path=file_path, columns=columns)  # Historico de indicador

    # Verificar que todas las columnas esten llenas y llenar datos faltantes
    df_indicador = datos.f_validar_info(df_indicador)

    # Asignar condicion a cada renglon de las diferentes
    df_indicador['escenario'] = [fn.condition(row['Actual'], row['Consensus'], row['Previous'])
                                 for index, row in df_indicador.iterrows()]
    return df_indicador


# -- --------------------------------------------------------- FUNCION: Cargar y clasificar -- #
# -- Cargar archivo de historico indicador y clasificar cada ocurrencia

def f_metricas(df_indicador, load_file: bool = False):
    """
    :param df_indicador: data frame con los datos de cuando se reporto el indicador y las columnas
        - Actual
        - Consensus
        - Previous
    :param load_file: Cargar un archivo con los datos historicos
    :return: mismo dataframe con las sigueintes metricas
        - Direccion: 1 = alcista, -1 = bajista
        - Pips_alcistas: cantidad de pips que subio la ventana
        - Pips_bajistas: cantidad de pips que bajo la ventana
        - volatilidad diferencia entre maximo y minimo de la ventana

    Debugging
    --------
    df_indicador = datos.f_leer_archivo(file_path='datos/Unemployment Rate - United States.csv')
    """
    # obtener diccionario de ventanas de 30 min despues de indicador
    if load_file:
        dict_historicos = datos.load_pickle_file('datos/ventanas_historicos.pkl')
    else:
        dict_historicos = datos.f_ventanas_30_min(df=df_indicador)

    # Agregar columnas de indicadores a df
    df_indicador['direccion'] = 0
    df_indicador['pips_alcistas'] = 0
    df_indicador['pips_bajistas'] = 0
    df_indicador['volatilidad'] = 0

    # Inicializar contador
    i = 0
    # Ciclo para calcular indicadores basicos
    for df in dict_historicos['historicos_sucesos'].values():
        # obtener direccion de ventana
        if df.Close.iloc[-1] - df.Open.iloc[0] >= 0:
            df_indicador.loc[i, 'direccion'] = 1  # 1 = alcista
        else:
            df_indicador.loc[i, 'direccion'] = -1  # -1 = bajista

        # obtener pips
        df_indicador.loc[i, 'pips_alcistas'] = (df.High.max() - df.Open[0]) * 10000
        df_indicador.loc[i, 'pips_bajistas'] = (df.Open[0] - df.Low.min()) * 10000

        # obtener volatilidad de la ventana
        df_indicador.loc[i, 'volatilidad'] = df.High.max() - df.Low.min()

        # Contador
        i += 1

    return df_indicador


# -- --------------------------------------------------------- FUNCION: Backtest -- #
# -- Hacer backtest de datos historicos

def f_backtest(df_decisiones, df_escenarios, inversion_inicial: float):
    """

    :param df_decisiones: dataframe de las decisiones para cada tipo de escenario del indicador (A,B,C,D)
    :param df_escenarios: dataframe de cuando se emitio el indicador y que tipo de escenario es
    :param inversion_inicial: monto inicial de la cuenta
    :return: dataframe con el backtest para todos los escenarios del indicador

    Debugging
    --------
    df_decisiones = df_decisiones
    df_escenarios = train
    inversion_inicial = 100000
    """
    df_backtest = df_escenarios.loc[:, ('DateTime', 'escenario')]
    df_backtest['operacion'] = ''
    df_backtest['volumen'] = 0
    df_backtest['resultado'] = ''
    df_backtest['pips'] = 0
    df_backtest['capital'] = 0
    df_backtest['capital_acm'] = 0

    for i in df_backtest.index:
        df_ventana = datos.load_pickle_file('datos/ventanas_historicos.pkl')['historicos_sucesos'
                                                                             ][str(df_backtest['DateTime'][i])]
        valores = df_decisiones.loc[df_decisiones.escenario == df_escenarios.escenario[i]]
        sl = valores.sl.values[0]  # Stop loss
        tp = valores.tp.values[0]  # Take profit
        df_backtest.loc[i, 'operacion'] = valores.operacion.values[0]  # Tipo de operacion (compra/venta)
        df_backtest.loc[i, 'volumen'] = valores.volumen.values[0]  # Volumen de operacion

        if df_backtest.operacion[i] == 'buy':
            for k in df_ventana.index:
                if df_ventana.High[k] >= df_ventana.Open[0] + (tp / 10000):
                    df_backtest.loc[i, 'resultado'] = 'ganadora'
                    df_backtest.loc[i, 'pips'] = tp
                    df_backtest.loc[i, 'capital'] = tp / 10000 * df_backtest.volumen[i]
                    if i == 0:
                        df_backtest.loc[i, 'capital_acm'] = inversion_inicial + df_backtest.capital[0]
                    else:
                        df_backtest.loc[i, 'capital_acm'] = df_backtest.capital_acm[i - 1] + df_backtest.capital[i]
                    break
                elif df_ventana.Low[k] <= df_ventana.Open[0] - (sl / 10000):
                    df_backtest.loc[i, 'resultado'] = 'perdedora'
                    df_backtest.loc[i, 'pips'] = -sl
                    df_backtest.loc[i, 'capital'] = -sl / 10000 * df_backtest.volumen[i]
                    if i == 0:
                        df_backtest.loc[i, 'capital_acm'] = inversion_inicial + df_backtest.capital[0]
                    else:
                        df_backtest.loc[i, 'capital_acm'] = df_backtest.capital_acm[i - 1] + df_backtest.capital[i]
                    break
                elif k == df_ventana.last_valid_index():
                    if df_ventana.Close[k] >= df_ventana.Open[0]:
                        df_backtest.loc[i, 'resultado'] = 'ganadora'
                    else:
                        df_backtest.loc[i, 'resultado'] = 'perdedora'
                    df_backtest.loc[i, 'pips'] = (df_ventana.Close[k] - df_ventana.Open[0]) * 10000
                    df_backtest.loc[i, 'capital'] = df_backtest.pips[i] / 10000 * df_backtest.volumen[i]
                    if i == 0:
                        df_backtest.loc[i, 'capital_acm'] = inversion_inicial + df_backtest.capital[0]
                    else:
                        df_backtest.loc[i, 'capital_acm'] = df_backtest.capital_acm[i - 1] + df_backtest.capital[i]
        else:  # operacion = sell
            for k in df_ventana.index:
                if df_ventana.Low[k] <= df_ventana.Open[0] - (tp / 10000):
                    df_backtest.loc[i, 'resultado'] = 'ganadora'
                    df_backtest.loc[i, 'pips'] = tp
                    df_backtest.loc[i, 'capital'] = tp / 10000 * df_backtest.volumen[i]
                    if i == 0:
                        df_backtest.loc[i, 'capital_acm'] = inversion_inicial + df_backtest.capital[0]
                    else:
                        df_backtest.loc[i, 'capital_acm'] = df_backtest.capital_acm[i - 1] + df_backtest.capital[i]
                    break
                elif df_ventana.High[k] >= df_ventana.Open[0] + (sl / 10000):
                    df_backtest.loc[i, 'resultado'] = 'perdedora'
                    df_backtest.loc[i, 'pips'] = -sl
                    df_backtest.loc[i, 'capital'] = -sl / 10000 * df_backtest.volumen[i]
                    if i == 0:
                        df_backtest.loc[i, 'capital_acm'] = inversion_inicial + df_backtest.capital[0]
                    else:
                        df_backtest.loc[i, 'capital_acm'] = df_backtest.capital_acm[i - 1] + df_backtest.capital[i]
                    break
                elif k == df_ventana.last_valid_index():
                    if df_ventana.Close[k] <= df_ventana.Open[0]:
                        df_backtest.loc[i, 'resultado'] = 'ganadora'
                    else:
                        df_backtest.loc[i, 'resultado'] = 'perdedora'
                    df_backtest.loc[i, 'pips'] = (df_ventana.Open[0] - df_ventana.Close[k]) * 10000
                    df_backtest.loc[i, 'capital'] = df_backtest.pips[i] / 10000 * df_backtest.volumen[i]
                    if i == 0:
                        df_backtest.loc[0, 'capital_acm'] = inversion_inicial + df_backtest.capital[0]
                    else:
                        df_backtest.loc[i, 'capital_acm'] = df_backtest.capital_acm[i - 1] + df_backtest.capital[i]

    return df_backtest
