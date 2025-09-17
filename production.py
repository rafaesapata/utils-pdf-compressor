#!/usr/bin/env python3
"""
Configuração de produção para UDS Utils - PDF Tools
"""

import os
import sys

# Configurações de produção
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Importar e executar aplicação
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.main import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
