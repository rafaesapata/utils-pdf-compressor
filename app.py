#!/usr/bin/env python3
"""
Ponto de entrada para produção - UDS Utils PDF Tools
"""

import os
import sys

# Configurar ambiente de produção
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar aplicação
from main import app

# Para gunicorn
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    
    try:
        # Tentar usar gunicorn
        import gunicorn.app.wsgiapp as wsgi
        
        sys.argv = [
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '4',
            '--timeout', '300',
            '--keep-alive', '2',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            'app:application'
        ]
        
        wsgi.run()
        
    except ImportError:
        # Fallback para Flask development server
        app.run(host='0.0.0.0', port=port, debug=False)
