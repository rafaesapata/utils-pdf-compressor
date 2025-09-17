#!/bin/bash

# Script para instalar Ghostscript no servidor de produção
echo "🔧 Instalando Ghostscript..."

# Atualizar repositórios
apt-get update

# Instalar Ghostscript
apt-get install -y ghostscript

# Verificar instalação
if command -v gs &> /dev/null; then
    echo "✅ Ghostscript instalado com sucesso!"
    gs --version
else
    echo "❌ Falha na instalação do Ghostscript"
    exit 1
fi

echo "🎉 Instalação concluída!"
