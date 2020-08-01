from settings import *
from subprocess import call
import arcpy
import glob


# Install packages
def decore_subprocess(func):
    """
    Decora funciones que devuelvan una sentencia ejecutable del consola(cmd)
    :param func: Funcion a decorar
    :return: Nueva funcion
    """

    def decorator(*args):
        command = func(*args)
        p = call('{} {}'.format(PYTHON_EXE, command), shell=True)
        response = 'Error' if p > 0 else 'Success'
        response = '{} execute command: {} {}'.format(response, PYTHON_EXE, command)
        arcpy.AddMessage(response)
        return response

    return decorator


@decore_subprocess
def install_pip():
    """
    Funcion decorada con decore_subprocess()
    :return: sentencia para la instalacion de pip desde consola
    """
    return '{}/get-pip.py'.format(REQUIRE_DIR)


@decore_subprocess
def upgrade_pip():
    """
    Funcion decorada con decore_subprocess()
    :return: sentencia para la actualizacion de pip desde consola
    """
    return '-m pip install -U pip'


@decore_subprocess
def install_package(package):
    """
    Funcion decorada con decore_subprocess()
    :param package: Modulo o *whl a instalar
    :return: sentencia para la actualizacion de cualquier paquete desde consola
    """
    return '-m pip install {}'.format(package)


def install_modules(directorio):
    """
    Funcion que permite instalar librerias necesarias
    :return: No aplica
    """
    packages = glob.glob(r'{}\*.whl'.format(directorio))
    packages = map(lambda i: os.path.join(directorio, i), packages)
    if not os.path.exists(PIP_EXE):
        install_pip()
    upgrade_pip()
    map(install_package, packages)


def script_tool_decore(func):
    """
    Funcion que permite decorar todos las funciones que se ejecutaran desde un ToolBox
    :param func: Funcion a decorar
    :return: Nueva funcion
    """

    def decorator(*args, **kwargs):
        response, state, message = object(), 1, 'success'
        try:
            response = func(*args, **kwargs)
        except AssertionError as e:
            state = 0
            exc_type, exc_obj, exc_tb = sys.exc_info()
            msg = exc_obj.message
            line = exc_tb.tb_lineno
            message = 'PythonError: %s, Motivo: %s, Linea: %s' % ('ValidationError', msg, line)
        except Exception as e:
            state = 0
            exc_type, exc_obj, exc_tb = sys.exc_info()
            msg = exc_obj.message
            line = exc_tb.tb_lineno
            message = 'PythonError: %s, Motivo: %s, Linea: %s' % (exc_type, msg, line)
        finally:
            return response, state, message

    return decorator
