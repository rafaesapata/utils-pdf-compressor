#!/bin/bash

# Script de instalação de dependências para produção
# UDS Utils - PDF Tools

echo "🚀 Instalando dependências para produção..."

# Atualizar sistema
apt-get update

# Instalar Ghostscript
echo "📦 Instalando Ghostscript..."
apt-get install -y ghostscript

# Verificar instalação do Ghostscript
if command -v gs &> /dev/null; then
    echo "✅ Ghostscript instalado: $(gs --version)"
else
    echo "❌ Erro: Ghostscript não foi instalado corretamente"
    exit 1
fi

# Instalar outras dependências do sistema
echo "📦 Instalando dependências do sistema..."
apt-get install -y \
    python3-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev

# Verificar se Python está funcionando
echo "🐍 Verificando Python..."
python3 --version

echo "✅ Todas as dependências foram instaladas com sucesso!"
echo "🎯 Sistema pronto para executar UDS Utils - PDF Tools"
