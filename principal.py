# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Proyecto Final - Sistema de Trading
# -- archivo: principal.py - archivo principal del proyecto
# -- mantiene: IF Hermela Peña, IF Manuel Pintado
# -- repositorio: https://github.com/manuelpintado/Proyecto_Equipo_6.git
# -- ------------------------------------------------------------------------------------ -- #

import proceso as pr
from datos import load_pickle_file, f_leer_archivo
import visualizaciones as vs

# Leer archivo de historico de indicador
df_indicador = pr.f_clasificacion_ocurrencias(file_path='datos/Unemployment Rate - United States.csv',
                                              columns=['DateTime', 'Actual', 'Consensus', 'Previous'])

# Agregar meticas basicas de ventanas de historicos
# Si es la primera vez que se corre el codigo: load_file=False
df_indicador = pr.f_metricas(df_indicador=df_indicador, load_file=True)

# Cargar diccionario
dict_historicos = load_pickle_file('datos/ventanas_historicos.pkl')

# Visualizar datos antes de pruebas estadisticas
vs_grafica_1 = vs.g_serie_indicador(df_serie=df_indicador)

# Prueba dicky fuller para revisar estacionariedad
dicky_fuller = pr.f_a_dicky_fuller(df_indicador=df_indicador)

# Visualizar grafica
"""
Conclusión GRAPH 1: 
"""
# Formato fecha: aaaa/mm/dd HH:MM:SS
vs_grafica_1 = vs.g_serie_tiempo(ventana='2020-01-10 13:30:00')

"""
Conclusión GRAPH 2: 
"""
# Formato fecha: aaaa/mm/dd HH:MM:SS
vs_grafica_2 = vs.g_serie_tiempo(ventana='2019-12-06 13:30:00')

"""
Conclusión GRAPH 3: 
"""
# Formato fecha: aaaa/mm/dd HH:MM:SS
vs_grafica_3 = vs.g_serie_tiempo(ventana='2019-10-04 12:30:00')

"""
Conclusión GRAPH 4: 
"""
# Formato fecha: aaaa/mm/dd HH:MM:SS
vs_grafica_4 = vs.g_serie_tiempo(ventana='2018-11-02 12:30:00')

"""
Conclusión GRAPH 5: 
"""
# Formato fecha: aaaa/mm/dd HH:MM:SS
vs_grafica_5 = vs.g_serie_tiempo(ventana='2018-06-01 12:30:00')

# Visualizar serie de tiempo indicador transformada para estacionariedad
vs_grafica_6 = vs.g_serie_indicador(df_serie=df_indicador)

# Visualizar datos atipicos
vs_grafica_7 = vs.g_box_atipicos(df_indicador=df_indicador)