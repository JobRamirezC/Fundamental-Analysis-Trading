# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Proyecto Final - Sistema de Trading
# -- archivo: proceso.py - funciones para procesamiento de datos
# -- mantiene: IF Hermela Peña, IF Manuel Pintado
# -- repositorio: https://github.com/manuelpintado/Proyecto_Equipo_6.git
# -- ------------------------------------------------------------------------------------ -- #

# Importar librerias
import datos
# import statsmodels.graphics.tsaplots

# -- ----------------------------------------- FUNCION: Estadisticas de la serie de tiempo -- #
# -- Encontrar parametros estadisticos de la serie de tiempo
def f_estadisticas(df_inidicador):
 pass


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

def f_metricas(df_indicador, load_file: bool = False):
    # obtener diccionario de ventanas de 30 min despues de indicador
    if load_file:
        dict_historicos = datos.load_file('datos/ventanas_historicos.pkl')
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
