# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Proyecto Final - Sistema de Trading
# -- archivo: funciones.py - funciones diversas utilizadas en el proyecto
# -- mantiene: IF Hermela Peña, IF Manuel Pintado
# -- repositorio: https://github.com/manuelpintado/Proyecto_Equipo_6.git
# -- ------------------------------------------------------------------------------------ -- #

# Importar librerias
import numpy as np
from ypstruct import structure
import pandas as pd
from datos import f_struct2dict
import time


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

def sharpe(df_portfolio, rf: float = 0.08):
    """
    :param df_portfolio: dataframe con el capital acumulado del portafolio
    :param rf: tasa libre de riesgo de EUA
    :return: radio de sharp

    Debugging
    --------
    df_portfolio = df_backtest
    rf = 0.08
    """
    capital_acm = np.array(df_portfolio.capital_acm)

    return float((np.sum(np.diff(np.log(capital_acm))) - rf) / np.std(capital_acm))


# -- --------------------------------------------------------- FUNCION: Run  -- #
# -- Funcion para correr el algoritmo genetico

# noinspection DuplicatedCode
def run(problem, params):
    """
    :param problem: estructura con datos del proble a optimizar
    :param params: parametros para la optimizacion
    :return: optimizacion por algoritmo genetico en formato diciconario y guarda en formato pkl
    
    codigo basado en el siguiente recurso:
    https://yarpiz.com/632/ypga191215-practical-genetic-algorithms-in-python-and-matlab

    Debugging
    --------
    problem = problem
    params = params
    """

    # informar que se inicia la optimización
    print('------------------------')
    print('Optimizacion del ratio de sharpe')
    print('------------------------')

    # Problem Information
    costfunc = problem.costfunc
    hist = problem.data
    investment = problem.init_invest
    backtest = problem.backtest
    nvar = problem.nvar
    varmin = problem.varmin
    varmax = problem.varmax

    # Parameters
    maxit = params.maxit  # Iterations
    npop = params.npop  # Population size
    beta = params.beta  #
    pc = params.pc  # proportion of children
    nc = int(np.round(pc * npop / 2) * 2)  # Number of children as even number
    gamma = params.gamma  # Exploration space
    mu = params.mu  # Mutarion chance
    sigma = params.sigma  # Step size

    # Empty Individual Template
    empty_individual = structure()
    empty_individual.position = None
    empty_individual.cost = None

    # Best Solution Ever Found
    bestsol = empty_individual.deepcopy()
    bestsol.cost = np.NINF

    # Initialize Population
    pop = empty_individual.repeat(npop)
    for i in range(npop):
        pop[i].position = np.random.randint(varmin, varmax, nvar)
        df_backtest = backtest(pop[i].position, hist, investment)
        pop[i].cost = costfunc(df_backtest)
        if pop[i].cost > bestsol.cost:
            bestsol = pop[i].deepcopy()

    # Best Cost of Iterations
    bestcost = np.empty(maxit)

    # Main Loop
    for it in range(maxit):
        ini = time.time()
        costs = np.array([x.cost for x in pop])
        avg_cost = np.mean(costs)
        if avg_cost != 0:
            costs = costs / avg_cost
        probs = np.exp(-beta * costs)

        popc = []
        for _ in range(nc // 2):

            # Select Parents
            # q = np.random.permutation(npop)
            # p1 = pop[q[0]]
            # p2 = pop[q[1]]

            # Perform Roulette Wheel Selection
            p1 = pop[roulette_wheel_selection(probs)]
            p2 = pop[roulette_wheel_selection(probs)]

            # Perform Crossover
            c1, c2 = crossover(p1, p2, gamma)

            # Perform Mutation
            c1 = mutate(c1, mu, sigma)
            c2 = mutate(c2, mu, sigma)

            # Apply Bounds
            apply_bound(c1, varmin, varmax)
            apply_bound(c2, varmin, varmax)

            # Evaluate First Offspring
            c1.cost = costfunc(backtest(c1.position, hist, investment))
            if c1.cost > bestsol.cost:
                bestsol = c1.deepcopy()

            # Evaluate Second Offspring
            c2.cost = costfunc(backtest(c2.position, hist, investment))
            if c2.cost > bestsol.cost:
                bestsol = c2.deepcopy()

            # Add Offsprings to popc
            popc.append(c1)
            popc.append(c2)

        # Merge, Sort and Select
        pop += popc
        pop = sorted(pop, key=lambda x: x.cost, reverse=True)
        pop = pop[0:npop]

        # Store Best Cost
        bestcost[it] = bestsol.cost

        # Show Iteration Information
        fin = time.time()
        print("Iteration {}: Best Sharpe = {}\n"
              " -Time: {:.2f} minutos".format(it, bestcost[it], (fin - ini) / 60))

        if it % 100 == 0 and it != 0:
            out = structure()
            out.pop = pop
            out.bestsol = bestsol
            out.bestcost = bestcost
            f_struct2dict(out, True)

    # Output
    out = structure()
    out.pop = pop
    out.bestsol = bestsol
    out.bestcost = bestcost
    modelo = f_struct2dict(out, True)
    return modelo


# -- --------------------------------------------------------- FUNCION: Crossover  -- #
# -- Funcion mezclar padres

def crossover(p1, p2, gamma=0.1):
    c1 = p1.deepcopy()
    c2 = p1.deepcopy()
    alpha = np.random.randint(-gamma, 1 + gamma, *c1.position.shape)
    c1.position = alpha * p1.position + (1 - alpha) * p2.position
    c2.position = alpha * p2.position + (1 - alpha) * p1.position
    return c1, c2


# -- --------------------------------------------------------- FUNCION: Mutate  -- #
# -- Mutar a los hijos

def mutate(x, mu, sigma):
    """
    :param x: estructura a mutar
    :param mu: probabilidad de mutacion
    :param sigma: tamaño de mutacion
    :return: estructura mutada

    Debugging
    --------
    x = c1
    """
    y = x.deepcopy()
    flag = np.random.rand(*x.position.shape) <= mu
    ind = np.argwhere(flag)
    y.position[ind] += sigma * np.random.randint(1, 10, ind.shape)
    return y


# -- --------------------------------------------------------- FUNCION: Apply Bound  -- #
# -- Mantener los valores dentro de los limites extablecidos
def apply_bound(x, varmin, varmax):
    x.position = np.maximum(x.position, varmin)
    x.position = np.minimum(x.position, varmax)


# -- --------------------------------------------------------- FUNCION: Selection  -- #
# -- Seleccionar cuales mutar

def roulette_wheel_selection(p):
    c = np.cumsum(p)
    r = sum(p) * np.random.rand()
    ind = np.argwhere(r <= c)
    return ind[0][0]
