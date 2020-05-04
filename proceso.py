# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Proyecto Final - Sistema de Trading
# -- archivo: proceso.py - funciones para procesamiento de datos
# -- mantiene: IF Hermela Peña, IF Manuel Pintado
# -- repositorio: https://github.com/manuelpintado/Proyecto_Equipo_6.git
# -- ------------------------------------------------------------------------------------ -- #

# Importar librerias
import datos
import funciones as fn
import statsmodels.api as sm


# import statsmodels.graphics.tsaplots

# -- ----------------------------------------- FUNCION: Estadisticas de la serie de tiempo -- #
# -- Encontrar parametros estadisticos de la serie de tiempo
def f_estadisticas(df_historicos):
    """
    Componente de Autocorrelación y Autocorrelación Parcial
    Prueba de Heterocedasticidad
    Prueba de Normalidad
    Estacionalidad
    Estacionariedad
    Detección de Atípico
    """
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
