# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Proyecto Final - Sistema de Trading
# -- archivo: proceso.py - funciones para procesamiento de datos
# -- mantiene: IF Hermela Peña, IF Manuel Pintado
# -- repositorio: https://github.com/manuelpintado/Proyecto_Equipo_6.git
# -- ------------------------------------------------------------------------------------ -- #

# Importar librerias
import pandas as pd
import numpy as np
import datos


# -- --------------------------------------------------------- FUNCION: Cargar y clasificar -- #
# -- Cargar archivo de historico indicador y clasificar cada ocurrencia

def f_clasificacion_ocurrencias(file_path: str, columns=None):
    """
    :param file_path: lugar donde esta ubicado el archivo de los datos historicos del indicador
    :return: dataframe del archivo agregando la clasificacion de cada ocurrencia

    Debugging
    --------
    file_path = 'datos/Unemployment Rate - United States.csv'
    """
    # Cargar información de archivos
    df_indicador = datos.f_leer_archivo(file_path=file_path,
                                        columns=columns)  # Historico de indicador

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

    # Asignar condicion a cada renglon de las diferentes
    df_indicador['escenario'] = [condition(row['Actual'], row['Consensus'], row['Previous'])
                                 for index, row in df_indicador.iterrows()]
    return df_indicador


# -- --------------------------------------------------------- FUNCION: Cargar y clasificar -- #
# -- Cargar archivo de historico indicador y clasificar cada ocurrencia

def f_metricas(df_indicador):
    # obtener diccionario de ventanas de 30 min despues de indicador
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
            df_indicador['direccion'][i] = 1  # 1 = alcista
        else:
            df_indicador['direccion'][i] = -1  # -1 = bajista

        # obtener pips
        df_indicador['pips_alcistas'][i] = df.High.iloc[-1] - df.Open.iloc[0] * 10000
        df_indicador['pips_bajistas'][i] =

    """
    (Dirección) Close (t_30) - Open(t_0) 
    (Pips Alcistas) High(t_0 : t_30) – Open(t_0) 
    (Pips Bajistas) Open(t_0) – Low(t_0 : t_30) 
    (Volatilidad) High(t_-30 : t_30) ,  - mínimo low (t_-30:t_30) 
    """

