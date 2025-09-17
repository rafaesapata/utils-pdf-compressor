#!/usr/bin/env python3
"""
WSGI entry point para UDS Utils - PDF Tools
"""

import os
import sys

# Adicionar diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar ambiente de produção
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Importar aplicação
from src.main import app

# WSGI application
application = app

if __name__ == "__main__":
    application.run()
