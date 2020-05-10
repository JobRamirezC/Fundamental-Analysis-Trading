# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Proyecto Final - Sistema de Trading
# -- archivo: proceso.py - funciones para procesamiento de datos
# -- mantiene: IF Hermela Peña, IF Manuel Pintado
# -- repositorio: https://github.com/manuelpintado/Proyecto_Equipo_6.git
# -- ------------------------------------------------------------------------------------ -- #

# Importar librerias
import datos
import funciones as fn
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

def f_backtest(df_decisiones, df_hist, inversion_inicial: float):
    """

    :param df_decisiones: dataframe de las decisiones para cada tipo de escenario del indicador (A,B,C,D)
    :param df_hist: dataframe de cuando se emitio el indicador y que tipo de escenario es
    :param inversion_inicial: monto inicial de la cuenta
    :return: dataframe con el backtest para todos los escenarios del indicador

    Debugging
    --------
    df_decisiones = df_decisiones
    df_hist = train
    inversion_inicial = 100000
    """
    dict_ventanas = datos.load_pickle_file('datos/ventanas_historicos.pkl')['historicos_sucesos']  # Cargar ventanas
    df_bt = df_hist.loc[:, ('DateTime', 'escenario')]  # Extraer columnas necesarias de histrico
    df_bt = df_bt.merge(df_decisiones.loc[:, ('escenario', 'operacion', 'volumen')], how='left', on='escenario')
    df_bt = df_bt.reindex(columns=df_bt.columns.tolist() + ['resultado', 'pips'])  # agregar columnas

    # revisar ventanas
    for i in df_bt.index:
        ventana = dict_ventanas[str(df_bt['DateTime'][i])]  # Tomar ventana para revisar
        tp_sl = df_decisiones.loc[df_decisiones['escenario'] == df_bt['escenario'][i], ('tp', 'sl')]
        if df_bt['operacion'][i] == 'buy':
            for j in ventana.index:
                if ventana.High[j] >= (ventana.Open[0] + tp_sl.iloc[0, 0] / 10000):
                    df_bt.loc[i, 'resultado'] = 'ganada'
                    df_bt.loc[i, 'pips'] = tp_sl.iloc[0, 0]
                    break
                elif ventana.Low[j] <= (ventana.Open[0] - tp_sl.iloc[0, 1] / 10000):
                    df_bt.loc[i, 'resultado'] = 'perdida'
                    df_bt.loc[i, 'pips'] = -tp_sl.iloc[0, 1]
                    break
                elif j == ventana.index[-1]:
                    df_bt.loc[i, 'resultado'] = 'ganada' if ventana.Close[j] >= ventana.Open[0] else 'perdida'
                    df_bt.loc[i, 'pips'] = (ventana.Close[j] - ventana.Open[0]) * 10000
        else:  # Operacion es sell
            for j in ventana.index:
                if ventana.Low[j] <= (ventana.Open[0] - tp_sl.iloc[0, 0] / 10000):
                    df_bt.loc[i, 'resultado'] = 'ganada'
                    df_bt.loc[i, 'pips'] = tp_sl.iloc[0, 0]
                    break
                elif ventana.High[j] >= (ventana.Open[0] + tp_sl.iloc[0, 1] / 10000):
                    df_bt.loc[i, 'resultado'] = 'perdida'
                    df_bt.loc[i, 'pips'] = -tp_sl.iloc[0, 1]
                    break
                elif j == ventana.index[-1]:
                    df_bt.loc[i, 'resultado'] = 'ganada' if ventana.Close[j] <= ventana.Open[0] else 'perdida'
                    df_bt.loc[i, 'pips'] = (ventana.Open[0] - ventana.Close[j]) * 10000

        df_bt['capital'] = [df_bt['pips'][i] / 10000 * df_bt['volumen'][i] for i in df_bt.index]
        df_bt['capital_acm'] = df_bt['capital'].cumsum() + inversion_inicial
    return df_bt


# -- --------------------------------------------------------- FUNCION: Optmizacion -- #
# -- Optmizar parametros de volumen, tp y sl

def f_optimize():
    pass
