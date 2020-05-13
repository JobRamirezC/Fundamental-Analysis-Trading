# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Proyecto Final - Sistema de Trading
# -- archivo: datos.py - funciones para obtención de datos necesarios
# -- mantiene: IF Hermela Peña, IF Manuel Pintado
# -- repositorio: https://github.com/manuelpintado/Proyecto_Equipo_6.git
# -- ------------------------------------------------------------------------------------ -- #

# Import libraries
import numpy as np  # funciones numericas
from datetime import timedelta  # diferencia entre datos tipo tiempo
import oandapyV20.endpoints.instruments as instruments  # informacion de precios historicos
import pandas as pd  # manejo de datos
from oandapyV20 import API  # conexion con broker OANDA
import entradas
import pickle


# -- --------------------------------------------------------- FUNCION: Descargar precios -- #
# -- Descargar precios historicos con OANDA

def f_precios_masivos(p0_fini, p1_ffin, p2_gran, p3_inst, p4_oatk, p5_ginc):
    """
    Parameters
    ----------
    p0_fini : str : fecha inicial para descargar precios en formato str o pd.to_datetime
    p1_ffin : str : fecha final para descargar precios en formato str o pd.to_datetime
    p2_gran : str : M1, M5, M15, M30, H1, H4, H8, segun formato solicitado por OANDAV20 api
    p3_inst : str : nombre de instrumento, segun formato solicitado por OANDAV20 api
    p4_oatk : str : OANDAV20 API
    p5_ginc : int : cantidad de datos historicos por llamada, obligatorio < 5000
    Returns
    -------
    dc_precios : pd.DataFrame : Data Frame con precios TOHLC
    Debugging
    ---------
    p0_fini = pd.to_datetime("2019-01-01 00:00:00").tz_localize('GMT')
    p1_ffin = pd.to_datetime("2019-12-31 00:00:00").tz_localize('GMT')
    p2_gran = "M1"
    p3_inst = "USD_MXN"
    p4_oatk = Tu token
    p5_ginc = 4900
    """

    def f_datetime_range_fx(p0_start, p1_end, p2_inc, p3_delta):
        """
        Parameters
        ----------
        p0_start : str : fecha inicial
        p1_end : str : fecha final
        p2_inc : int : incremento en cantidad de elementos
        p3_delta : str : intervalo para medir elementos ('minutes', 'hours', 'days')
        Returns
        -------
        ls_result : list : lista con fechas intermedias a frequencia solicitada
        Debugging
        ---------
        p0_start = p0_fini
        p1_end = p1_ffin
        p2_inc = p5_ginc
        p3_delta = 'minutes'
        """

        ls_result = []
        nxt = p0_start

        while nxt <= p1_end:
            ls_result.append(nxt)
            if p3_delta == 'minutes':
                nxt += timedelta(minutes=p2_inc)
            elif p3_delta == 'hours':
                nxt += timedelta(hours=p2_inc)
            elif p3_delta == 'days':
                nxt += timedelta(days=p2_inc)

        return ls_result

    # inicializar api de OANDA

    api = API(access_token=p4_oatk)

    gn = {'S30': 30, 'S10': 10, 'S5': 5, 'M1': 60, 'M5': 60 * 5, 'M15': 60 * 15,
          'M30': 60 * 30, 'H1': 60 * 60, 'H4': 60 * 60 * 4, 'H8': 60 * 60 * 8,
          'D': 60 * 60 * 24, 'W': 60 * 60 * 24 * 7, 'M': 60 * 60 * 24 * 7 * 4}

    # -- para el caso donde con 1 peticion se cubran las 2 fechas
    if int((p1_ffin - p0_fini).total_seconds() / gn[p2_gran]) < 4990:

        # Fecha inicial y fecha final
        f1 = p0_fini.strftime('%Y-%m-%dT%H:%M:%S')
        f2 = p1_ffin.strftime('%Y-%m-%dT%H:%M:%S')

        # Parametros pra la peticion de precios
        params = {"granularity": p2_gran, "price": "M", "dailyAlignment": 16, "from": f1,
                  "to": f2}

        # Ejecutar la peticion de precios
        a1_req1 = instruments.InstrumentsCandles(instrument=p3_inst, params=params)
        a1_hist = api.request(a1_req1)

        # Para debuging
        # print(f1 + ' y ' + f2)
        lista = list()

        # Acomodar las llaves
        for i in range(len(a1_hist['candles']) - 1):
            lista.append({'TimeStamp': a1_hist['candles'][i]['time'],
                          'Open': a1_hist['candles'][i]['mid']['o'],
                          'High': a1_hist['candles'][i]['mid']['h'],
                          'Low': a1_hist['candles'][i]['mid']['l'],
                          'Close': a1_hist['candles'][i]['mid']['c']})

        # Acomodar en un data frame
        r_df_final = pd.DataFrame(lista)
        r_df_final = r_df_final[['TimeStamp', 'Open', 'High', 'Low', 'Close']]
        r_df_final['TimeStamp'] = pd.to_datetime(r_df_final['TimeStamp'])
        r_df_final['Open'] = pd.to_numeric(r_df_final['Open'], errors='coerce')
        r_df_final['High'] = pd.to_numeric(r_df_final['High'], errors='coerce')
        r_df_final['Low'] = pd.to_numeric(r_df_final['Low'], errors='coerce')
        r_df_final['Close'] = pd.to_numeric(r_df_final['Close'], errors='coerce')

        return r_df_final

    # -- para el caso donde se construyen fechas secuenciales
    else:

        # hacer series de fechas e iteraciones para pedir todos los precios
        fechas = f_datetime_range_fx(p0_start=p0_fini, p1_end=p1_ffin, p2_inc=p5_ginc,
                                     p3_delta='minutes')

        # Lista para ir guardando los data frames
        lista_df = list()

        for n_fecha in range(0, len(fechas) - 1):

            # Fecha inicial y fecha final
            f1 = fechas[n_fecha].strftime('%Y-%m-%dT%H:%M:%S')
            f2 = fechas[n_fecha + 1].strftime('%Y-%m-%dT%H:%M:%S')

            # Parametros pra la peticion de precios
            params = {"granularity": p2_gran, "price": "M", "dailyAlignment": 16, "from": f1,
                      "to": f2}

            # Ejecutar la peticion de precios
            a1_req1 = instruments.InstrumentsCandles(instrument=p3_inst, params=params)
            a1_hist = api.request(a1_req1)

            # Para debuging
            # print(f1 + ' y ' + f2)
            lista = list()

            # Acomodar las llaves
            for i in range(len(a1_hist['candles']) - 1):
                lista.append({'TimeStamp': a1_hist['candles'][i]['time'],
                              'Open': a1_hist['candles'][i]['mid']['o'],
                              'High': a1_hist['candles'][i]['mid']['h'],
                              'Low': a1_hist['candles'][i]['mid']['l'],
                              'Close': a1_hist['candles'][i]['mid']['c']})

            # Acomodar en un data frame
            pd_hist = pd.DataFrame(lista)
            pd_hist = pd_hist[['TimeStamp', 'Open', 'High', 'Low', 'Close']]
            pd_hist['TimeStamp'] = pd.to_datetime(pd_hist['TimeStamp'])

            # Ir guardando resultados en una lista
            lista_df.append(pd_hist)

        # Concatenar todas las listas
        r_df_final = pd.concat([lista_df[i] for i in range(0, len(lista_df))])

        # resetear index en dataframe resultante porque guarda los indices del dataframe pasado
        r_df_final = r_df_final.reset_index(drop=True)
        r_df_final['Open'] = pd.to_numeric(r_df_final['Open'], errors='coerce')
        r_df_final['High'] = pd.to_numeric(r_df_final['High'], errors='coerce')
        r_df_final['Low'] = pd.to_numeric(r_df_final['Low'], errors='coerce')
        r_df_final['Close'] = pd.to_numeric(r_df_final['Close'], errors='coerce')

        return r_df_final


# -- ----------------------------------------------- Funcion: Descargar y guardar datos -- #
# -- Descargar precios historicos con OANDA y guardar en csv

def f_ventanas_30_min(df):
    """
    :param df: dataframe conteniendo columna DateTime
    :return: Diccionario de dataframes de historicos del USD_GBP de los sigueintes 30 minutos despues de la fecha n

    Debugging
    --------
    df = f_leer_archivo(file_path='datos/Unemployment Rate - United States.csv')
    """
    times = np.array([pd.to_datetime(time) for time in df.DateTime])
    dictionary = {'historicos_sucesos': {}}
    for time in times:
        ticker = 'GBP_USD'
        if time.hour == 13:
            fini = pd.to_datetime(time + pd.to_timedelta(-5, unit='hour'))
        else:
            fini = pd.to_datetime(time + pd.to_timedelta(-4, unit='hour'))
        ffin = pd.to_datetime(fini + pd.to_timedelta(1, unit='hour'))  # Fecha final
        granularity = "M1"
        df_historicos = f_precios_masivos(p0_fini=fini, p1_ffin=ffin, p2_gran=granularity, p3_inst=ticker,
                                          p4_oatk=entradas.token, p5_ginc=4900).iloc[:30]

        dictionary['historicos_sucesos'][str(time)] = df_historicos

    # Guardar datos historicos en formato json par no tener que descargar precios cada ejecucion
    save_pickle_file(dictionary, 'datos/ventanas_historicos.pkl')

    return dictionary


# -- ----------------------------------------------------------- FUNCION: cargar archivos -- #
# -- Cargar archivos de historicos e indicador

def f_leer_archivo(file_path: str, columns=None, index=None):
    """
    :param file_path: Ubicacion del archivo de informacion de indicador
    :param columns: columnas que se quieran seleccionar del archivo.
                    si se deja en blanco se toman todas las columnas del archivo
    :param index: name of column for index
    :return: Dataframe de información de archivo validada que este completa

    Debugging
    --------
    file_path = 'datos/Unemployment Rate - United States.csv'
    """
    if columns is None:
        if index is None:
            df_archivo = pd.read_csv(file_path)
        else:
            df_archivo = pd.read_csv(file_path, index_col=index)

    else:
        if index is None:
            df_archivo = pd.read_csv(file_path, usecols=columns)
        else:
            df_archivo = pd.read_csv(file_path, usecols=columns, index_col=index)

    return df_archivo


# -- ------------------------------------------------- FUNCION: validar dataframe completo -- #
# -- Validar que todos los datos del archivo esten llenos y llenar los faltantes

def f_validar_info(df):
    """

    :param df: Dataframe con datos de Actual, Consensus y previous
    :return: df con todos los valores de las 3 columnas anteriormente descritas llenas

    Debugging
    --------
    df = f_leer_archivo(file_path='datos/Unemployment Rate - United States.csv',
                        columns=['DateTime', 'Actual', 'Consensus', 'Previous'])

    """
    for i in range(0, len(df.index)):
        if df.Previous[i] == 0:
            df.Previous[i] = df.Actual[i + 1]
        if df.Consensus[i] == 0:
            df.Consensus[i] = df.Previous[i]
    df = df.dropna()
    df.loc[:, 'DateTime'] = pd.to_datetime(df['DateTime'])
    df = df.sort_values(by=['DateTime'])
    df.reset_index(drop=True, inplace=True)
    return df


# -- ------------------------------------------------- FUNCION: cargar archivo formato plk -- #
# -- Guardar diccionario de historicos en formato pickle

def load_pickle_file(filename):
    data = pickle.load(open(filename, 'rb'))
    return data


# -- ------------------------------------------------- FUNCION: guardar archivo formato pkl -- #
# -- Cargar diccionario de historicos en formato pickle

def save_pickle_file(data, filename):
    pickle.dump(data, open(filename, 'wb'))


# -- ------------------------------------------------- FUNCION: structure to dict -- #
# -- Convertir estructura ypstruct a diccionario

def f_struct2dict(structure, save: bool = True):
    """
    :param structure: estructura a convertir
    :param save: guardar parametros en archivo pickle
    :return: diccionario con informacion de estructura

    """

    # datos para poder pasar df decisiones en backtest
    info = pd.DataFrame({'escenario': ['A', 'B', 'C', 'D'],
                         'operacion': ['sell', 'buy', 'sell', 'buy']})

    out_dict = {'populations': {},
                'best_solution': {'position': pd.concat([info, pd.DataFrame(np.reshape(structure.bestsol.position,
                                                                                       (4, 3)),
                                                                            columns=['sl', 'tp', 'volumen'])],
                                                        axis=1),
                                  'sharpe': structure.bestsol.cost},
                'best_sharpe': structure.bestcost}

    for i in range(len(structure.pop)):
        out_dict['populations'][str(i)] = {
            'position': pd.concat([info, pd.DataFrame(np.reshape(structure.pop[i].position,
                                                                 (4, 3)),
                                                      columns=['sl', 'tp', 'volumen'])],
                                  axis=1),
            'sharpe': structure.pop[i].cost}

    if save:
        save_pickle_file(out_dict, 'datos/optimizacion.pkl')

    return out_dict


# -- ------------------------------------------------------- Operacion: Descargar precios -- #
# -- Descargar precios historicos con OANDA y guardar en csv
"""
df = f_leer_archivo(file_path='datos/Unemployment Rate - United States.csv',
                    columns=['DateTime', 'Actual', 'Consensus', 'Previous'])
ticker = 'GBP_USD'
fini = pd.to_datetime(df.DateTime.iloc[-1]).tz_localize('GMT')
ffin = pd.Timestamp.today(tz='GMT')
granularity = "M1"
df_historicos = f_precios_masivos(p0_fini=fini, p1_ffin=ffin, p2_gran=granularity, p3_inst=ticker,
                                  p4_oatk=entradas.token, p5_ginc=4900)
df_historicos.to_csv('datos/historicos.csv', index=False)
"""
