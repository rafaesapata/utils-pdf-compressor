# UDS Utils - PDF Compress

Uma aplicação web moderna para compressão de arquivos PDF com diferentes níveis de otimização.

## Características

- **Interface moderna**: Design responsivo seguindo a identidade visual da UDS Tecnologia
- **Duas opções de compressão**:
  - **Otimizada**: Remove duplicação e aplica compressão lossless mantendo qualidade visual
  - **Máxima**: Compressão máxima com redução de qualidade de imagem para maior economia de espaço
- **Processamento local**: Utiliza a biblioteca pypdf para compressão sem dependências externas
- **Segurança**: Sanitização de caracteres e validação de arquivos
- **Drag & Drop**: Interface intuitiva para upload de arquivos

## Tecnologias Utilizadas

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Compressão**: pypdf (biblioteca Python)
- **Design**: CSS Grid, Flexbox, Gradientes

## Instalação e Execução

### Pré-requisitos
- Python 3.11+
- pip

### Passos para instalação

1. Clone o repositório:
```bash
git clone https://github.com/rafaesapata/utils-pdf-compressor.git
cd utils-pdf-compressor
```

2. Ative o ambiente virtual:
```bash
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
python src/main.py
```

5. Acesse no navegador:
```
http://localhost:5001
```

## API Endpoints

### GET /api/pdf/health
Verifica o status do serviço de compressão.

### GET /api/pdf/info
Retorna informações sobre tipos de compressão e limites.

### POST /api/pdf/compress
Comprime um arquivo PDF.

**Parâmetros:**
- `file`: Arquivo PDF (multipart/form-data)
- `compression_type`: "optimized" ou "maximum"

**Resposta:** Arquivo PDF comprimido para download

## Funcionalidades de Compressão

### Compressão Otimizada
- Remove objetos duplicados
- Aplica compressão lossless (FlateDecode/zlib)
- Mantém qualidade visual original
- Redução típica: 30-70% do tamanho original

### Compressão Máxima
- Todas as funcionalidades da compressão otimizada
- Reduz qualidade de imagens para 60%
- Compressão lossless no nível máximo (9)
- Redução típica: 50-86% do tamanho original

## Limites e Restrições

- **Tamanho máximo**: 50MB por arquivo
- **Formatos aceitos**: Apenas PDF
- **Processamento**: Local (sem envio para serviços externos)

## Estrutura do Projeto

```
├── src/
│   ├── main.py              # Aplicação Flask principal
│   ├── routes/
│   │   ├── pdf_compress.py  # Rotas da API de compressão
│   │   └── user.py          # Rotas de usuário (template)
│   ├── services/
│   │   └── pdf_compressor.py # Serviço de compressão PDF
│   ├── models/
│   │   └── user.py          # Modelos de dados (template)
│   └── static/
│       └── index.html       # Interface web
├── venv/                    # Ambiente virtual Python
├── requirements.txt         # Dependências Python
└── README.md               # Este arquivo
```

## Segurança

- Sanitização de nomes de arquivos
- Validação de tipos de arquivo
- Limpeza de caracteres UTF-8 inválidos
- Processamento em arquivos temporários
- Limpeza automática de arquivos temporários

## Versão

- **Versão**: 1.0.0
- **Data**: Setembro 2025
- **Desenvolvido por**: UDS Tecnologia

## Licença

© 2025 UDS Tecnologia - Todos os direitos reservados.
