# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Proyecto Final - Sistema de Trading
# -- archivo: principal.py - archivo principal del proyecto
# -- mantiene: IF Hermela Peña, IF Manuel Pintado
# -- repositorio: https://github.com/manuelpintado/Proyecto_Equipo_6.git
# -- ------------------------------------------------------------------------------------ -- #

# Importat librerias
import proceso as pr
import visualizaciones as vs
import pandas as pd
import funciones as fn
from ypstruct import structure
import datos

# Leer archivo de historico de indicador
df_indicador = pr.f_clasificacion_ocurrencias(file_path='datos/Unemployment Rate - United States.csv',
                                              columns=['DateTime', 'Actual', 'Consensus', 'Previous'])

# Visualizar datos antes de pruebas estadisticas
vs_grafica_1_estadistica = vs.g_serie_indicador(df_serie=df_indicador)

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

# Agregar meticas basicas de ventanas de historicos
# Si es la primera vez que se corre el codigo: load_file=False
df_indicador = pr.f_metricas(df_indicador=df_indicador, load_file=True)

# Prueba dicky fuller para revisar estacionariedad
dicky_fuller = pr.f_a_dicky_fuller(df_indicador=df_indicador)

# Prueba de normalidad
shapiro_results = pr.f_normalidad(df_indicador=df_indicador)

# Prueba de estacionalidad
estacionalidad = pr.f_estacionalidad(df_indicador=df_indicador)

# Prueba de heterocedasticidad
arch = pr.f_heterocerasticidad(df_indicador=df_indicador)

# Visualizar serie de tiempo indicador transformada para estacionariedad
vs_grafica_6 = vs.g_serie_indicador(df_serie=df_indicador)

# Visualizar estacionalidad
vs_grafica_estacionalidad = vs.g_estacionalidad_descompuesta(object=estacionalidad)

# Visualizar datos atipicos
vs_grafica_7 = vs.g_box_atipicos(df_indicador=df_indicador)

# %% optimizacion y backtest
capital_inicial = 100000
maximo_riesgo = 1000
df_escenarios = df_indicador[['DateTime', 'escenario', 'direccion', 'pips_alcistas', 'pips_bajistas', 'volatilidad']]

df_decisiones = pd.DataFrame({'escenario': ['A', 'B', 'C', 'D'],
                              'operacion': ['sell', 'buy', 'sell', 'buy'],
                              'sl': [100, 100, 100, 100],
                              'tp': [200, 200, 200, 200],
                              'volumen': [100000, 100000, 100000, 100000]})

# Separar datos en entrenamiento y prueba

start = pd.to_datetime('01/01/2009')  # Fecha de inicio datos de entrenamiento
split = pd.to_datetime('01/01/2019')  # Fecha que separa datos de entrenamiento y prueba

# Separar entrenameinto
train = df_escenarios.loc[df_escenarios['DateTime'] <= split]
train = train.loc[train['DateTime'] >= start]
train.reset_index(inplace=True, drop=True)
end = pd.to_datetime('01/01/2020')  # Fecha de fin datos entrenamiento

# Separar pprueba
test = df_escenarios.loc[df_escenarios['DateTime'] > split]
test = test.loc[test['DateTime'] <= end]
test.reset_index(inplace=True, drop=True)

# Hacer backtest
df_backtest = pr.f_backtest(df_decisiones=df_decisiones, df_hist=train, inversion_inicial=capital_inicial)

# Calcular ratio de Sharp
sharpe_value = fn.sharpe(df_portfolio=df_backtest)


# Optimizar modelo
problem = structure()
problem.costfunc = fn.sharpe
problem.backtest = pr.f_backtest_2
problem.data = train
problem.init_invest = capital_inicial
problem.nvar = 12
problem.varmin = [0, 0, 1000, 0, 0, 1000, 0, 0, 1000, 0, 0, 1000]
problem.varmax = [300, 500, 150000, 300, 400, 150000, 300, 400, 150000, 300, 400, 150000]

# GA Parameters
params = structure()
params.maxit = 1000
params.npop = 50
params.beta = 1
params.pc = 2
params.gamma = 0.2
params.mu = 0.2
params.sigma = 2

# Correr Algoritmo Genetico
# dict_modelo = fn.run(problem, params)

# Cargar modelo si ya se tienen los parametros optimizados
dict_modelo = datos.load_pickle_file('datos/optimizacion.pkl')

# Extraer lista de evolucion de ratio de Sharpe
sharp_optimization = dict_modelo['best_sharpe']

# Graficar evolucion de ratio
vs_optimizacion = vs.g_optimizacion(values=sharp_optimization)

# Crear data frame de decisiones optimizadas
df_decisiones = dict_modelo['best_solution']['position']


# Visualizar evolucion del capital con parametros optimizados entrenamiento
df_backtest = pr.f_backtest(df_decisiones=df_decisiones, df_hist=train, inversion_inicial=capital_inicial)
vs_backtest_optimizado = vs.g_evolucion_capital(df_backtest)

# Visualizar evolucion del capital con parametros optimizados prueba
df_prueba = pr.f_backtest(df_decisiones=df_decisiones, df_hist=test, inversion_inicial=capital_inicial)
vs_prueba_optimizado = vs.g_evolucion_capital(df_prueba)

# Calcular MAD y presentar en un DataFrame

MAD = pd.DataFrame({
    'sharpe': fn.sharpe(df_prueba),
    'sortino': fn.sortino(df_prueba),
    'draw_down': fn.draw_down(df_prueba)
}, index='valor_MAD')
