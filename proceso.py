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
import matplotlib.pyplot
import visualizaciones as vs
from scipy.stats import shapiro


# import statsmodels.graphics.tsaplots

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
        print('Se rechaza la H0, la serie no es normal')
    else:
        print('Se acepta la H0, la serie es normal')

    return shapiro_results


# -- ----------------------------------------- FUNCION: ARCH -- #
# -- Encontrar autoregresion


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
