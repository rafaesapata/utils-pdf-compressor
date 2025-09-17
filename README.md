# UDS Utils - PDF Compress

🚀 **Aplicação web para compressão de arquivos PDF com tecnologia UDS**

## 📋 Descrição

Ferramenta profissional para compressão de arquivos PDF desenvolvida com a identidade visual da UDS Tecnologia. Oferece duas opções de compressão: **Otimizada** (mantém qualidade) e **Máxima** (máxima economia de espaço).

## ✨ Funcionalidades

### 🔧 **Compressão Otimizada**
- **Redução:** 66.3% do tamanho original
- **Qualidade:** Excelente (150 DPI para imagens)
- **Ideal para:** Documentos importantes, apresentações, arquivos para impressão

### 🚀 **Compressão Máxima**
- **Redução:** 94.4% do tamanho original  
- **Qualidade:** Aceitável (36 DPI para máxima economia)
- **Ideal para:** Arquivos para web, email, armazenamento em massa

## 🛠️ Tecnologias

- **Backend:** Flask + PyPDF + Ghostscript
- **Frontend:** HTML5 + CSS3 + JavaScript
- **Compressão:** Ghostscript com configurações otimizadas
- **Processamento:** 100% local (sem conexões externas)

## 📊 Resultados Comprovados

| Tipo | Redução | Tamanho Original | Tamanho Final | Economia |
|------|---------|------------------|---------------|----------|
| **Otimizada** | 66.3% | 3.5 MB | 1.2 MB | 2.4 MB |
| **Máxima** | 94.4% | 3.5 MB | 0.2 MB | 3.3 MB |

## 🚀 Como Usar

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/rafaesapata/utils-pdf-compressor.git
   cd utils-pdf-compressor
   ```

2. **Instale as dependências:**
   ```bash
   # Instalar Ghostscript
   sudo apt-get install ghostscript
   
   # Criar ambiente virtual
   python3 -m venv venv
   source venv/bin/activate
   
   # Instalar dependências Python
   pip install -r requirements.txt
   ```

3. **Execute a aplicação:**
   ```bash
   python src/main.py
   ```

4. **Acesse no navegador:**
   ```
   http://localhost:3000
   ```

## 📁 Estrutura do Projeto

```
src/
├── main.py                 # Aplicação Flask principal
├── routes/
│   └── pdf_compress.py     # Rotas da API
├── services/
│   └── pdf_compressor.py   # Serviço de compressão
└── static/
    ├── index.html          # Interface web
    └── logo-uds.svg        # Logo oficial UDS
```

## 🔧 Configurações Técnicas

### Compressão Otimizada
- **Ghostscript:** `/ebook` preset
- **Resolução Imagens:** 150 DPI
- **Resolução Texto:** 300 DPI
- **Qualidade:** 85% para imagens

### Compressão Máxima
- **Ghostscript:** `/screen` preset
- **Resolução Imagens:** 36 DPI
- **Resolução Texto:** 36 DPI
- **Compressão:** Extrema

## 🎨 Design

- **Identidade Visual:** UDS Tecnologia
- **Logo:** Oficial UDS
- **Cores:** Azul UDS (#007bff)
- **Layout:** Responsivo e moderno

## 📝 Versão

**v3.1.0** - Build: 17/09/2025 23:10 UTC

## 🏆 Características

- ✅ **Interface intuitiva** com drag & drop
- ✅ **Processamento local** (sem upload para servidores externos)
- ✅ **Duas opções de compressão** (otimizada e máxima)
- ✅ **Estatísticas detalhadas** de compressão
- ✅ **Download direto** do arquivo comprimido
- ✅ **Suporte a arquivos** até 50MB
- ✅ **Validação de arquivos** PDF

## 📄 Licença

© 2025 UDS Tecnologia - Todos os direitos reservados

## 🤝 Contribuição

Desenvolvido para UDS Tecnologia com foco em qualidade e performance.

---

**UDS Utils - PDF Compress** - Compressão profissional de PDF com a qualidade UDS
