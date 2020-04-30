# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Proyecto Final - Sistema de Trading
# -- archivo: funciones.py - funciones diversas utilizadas en el proyecto
# -- mantiene: IF Hermela Peña, IF Manuel Pintado
# -- repositorio: https://github.com/manuelpintado/Proyecto_Equipo_6.git
# -- ------------------------------------------------------------------------------------ -- #

# Importar librerias


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
