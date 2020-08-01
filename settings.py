#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Importacion de librerias
from __future__ import print_function

import os
import sys

__author__ = 'Daniel Fernando Aguado Huaccharaqui'
__copyright__ = 'MINEM 2020'
__credits__ = ['Daniel Aguado H.', 'Rafael Ocana']
__version__ = '1.0.1'
__maintainer__ = 'Daniel Aguado H.'
__mail__ = 'daniel030891@gmail.com'
__status__ = 'Development'
# __status__ = 'Production'


# Directorio principal del proyecto
BASE_DIR = os.path.dirname(__file__)

# Directorio de archivos estaticos
STATIC_DIR = os.path.join(BASE_DIR, 'statics')

# Conexion a geodatabase coorporativa
# ...

# Plantillas de reportes
# ...

# Requirements
REQUIRE_DIR = os.path.abspath(os.path.join(STATIC_DIR, 'require'))

# Directorio de archivos temporales
TMP_DIR = os.path.join(BASE_DIR, 'temp')

# Ubicacion de pip
PIP_EXE = os.path.join(sys.exec_prefix, 'Scripts\\pip.exe')

# Ubicacion de python.exe
PYTHON_EXE = os.path.join(sys.exec_prefix, 'python.exe')
