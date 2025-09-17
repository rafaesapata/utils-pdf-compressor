#!/bin/bash
# Script para instalar dependências do sistema
echo "Instalando Ghostscript..."
apt-get update
apt-get install -y ghostscript
echo "Ghostscript instalado com sucesso!"
