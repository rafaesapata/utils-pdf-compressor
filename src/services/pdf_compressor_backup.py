import os
import tempfile
import re
import subprocess
from pypdf import PdfWriter, PdfReader
from typing import Tuple, Optional

class PDFCompressor:
    """Serviço para compressão de arquivos PDF com diferentes níveis de otimização"""
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Remove caracteres nulos e UTF-8 inválidos"""
        if not text:
            return ""
        # Remove caracteres nulos
        text = text.replace('\x00', '')
        # Remove outros caracteres de controle problemáticos
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        return text
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Retorna o tamanho do arquivo em bytes"""
        return os.path.getsize(file_path)
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Formata o tamanho do arquivo para exibição"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    @staticmethod
    def compress_pdf_optimized(input_path: str, output_path: str) -> Tuple[bool, str, dict]:
        """
        Compressão otimizada: Usa Ghostscript com configurações balanceadas
        Mantém boa qualidade visual com redução significativa de tamanho
        """
        try:
            original_size = PDFCompressor.get_file_size(input_path)
            
            # USAR GHOSTSCRIPT COM CONFIGURAÇÕES OTIMIZADAS (menos agressivas que máxima)
            try:
                # Comando ghostscript para compressão OTIMIZADA
                cmd = [
                    'gs',
                    '-sDEVICE=pdfwrite',
                    '-dCompatibilityLevel=1.4',
                    '-dPDFSETTINGS=/ebook',  # Configuração balanceada (melhor que /screen)
                    '-dNOPAUSE',
                    '-dQUIET',
                    '-dBATCH',
                    '-dColorImageResolution=150',  # Resolução moderada (melhor qualidade)
                    '-dGrayImageResolution=150',   # Resolução moderada
                    '-dMonoImageResolution=300',   # Resolução boa para texto
                    '-dColorImageDownsampleType=/Bicubic',
                    '-dGrayImageDownsampleType=/Bicubic',
                    '-dMonoImageDownsampleType=/Bicubic',
                    '-dCompressPages=true',
                    '-dUseFlateCompression=true',
                    '-dOptimize=true',
                    f'-sOutputFile={output_path}',
                    input_path
                ]
                
                # Executar ghostscript
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0 and os.path.exists(output_path):
                    # Ghostscript funcionou!
                    compressed_size = PDFCompressor.get_file_size(output_path)
                    reduction_percent = ((original_size - compressed_size) / original_size) * 100
                    
                    stats = {
                        'original_size': original_size,
                        'compressed_size': compressed_size,
                        'reduction_percent': reduction_percent,
                        'original_size_formatted': PDFCompressor.format_file_size(original_size),
                        'compressed_size_formatted': PDFCompressor.format_file_size(compressed_size),
                        'compression_type': 'Otimizada'
                    }
                    
                    return True, "Compressão otimizada realizada com sucesso", stats
                else:
                    # Se ghostscript falhar, usar fallback PyPDF
                    raise Exception(f"Ghostscript falhou: {result.stderr}")
                    
            except Exception as gs_error:
                # FALLBACK: PyPDF com compressão moderada se ghostscript falhar
                writer = PdfWriter(clone_from=input_path)
                
                # Aplicar compressão moderada em todas as páginas
                for page in writer.pages:
                    try:
                        # Compressão lossless no nível 6 (moderado)
                        page.compress_content_streams(level=6)
                        
                        # Tentar reduzir qualidade de imagens moderadamente (85%) se possível
                        try:
                            for img in page.images:
                                try:
                                    if hasattr(img, 'image') and img.image is not None:
                                        # Redução moderada na qualidade
                                        img.replace(img.image, quality=85)
                                except:
                                    # Se falhar, continua sem compressão de imagem
                                    continue
                        except:
                            # Se não conseguir processar imagens, continua
                            pass
                            
                    except Exception as compress_error:
                        # Se falhar compressão nível 6, tenta nível 4
                        try:
                            page.compress_content_streams(level=4)
                        except:
                            # Se ainda falhar, pula esta página
                            continue
                
                # Remover objetos duplicados e órfãos
                writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
                
                # Manter metadados essenciais
                try:
                    if writer.metadata:
                        essential_metadata = {}
                        if '/Title' in writer.metadata:
                            essential_metadata['/Title'] = writer.metadata['/Title']
                        if '/Author' in writer.metadata:
                            essential_metadata['/Author'] = writer.metadata['/Author']
                        writer.metadata = essential_metadata
                except:
                    pass
                
                # Salvar arquivo comprimido
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                compressed_size = PDFCompressor.get_file_size(output_path)
                reduction_percent = ((original_size - compressed_size) / original_size) * 100
                
                stats = {
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'reduction_percent': reduction_percent,
                    'original_size_formatted': PDFCompressor.format_file_size(original_size),
                    'compressed_size_formatted': PDFCompressor.format_file_size(compressed_size),
                    'compression_type': 'Otimizada'
                }
                
                return True, "Compressão otimizada realizada com sucesso (fallback)", stats
            
        except Exception as e:
            error_msg = PDFCompressor.sanitize_text(str(e))
            return False, f"Erro na compressão otimizada: {error_msg}", {}
    
    @staticmethod
    def compress_pdf_maximum(input_path: str, output_path: str) -> Tuple[bool, str, dict]:
        """
        Compressão máxima: Usa ghostscript para atingir 70%+ de redução
        """
        try:
            original_size = PDFCompressor.get_file_size(input_path)
            
            # USAR GHOSTSCRIPT DIRETAMENTE - COMPROVADAMENTE FUNCIONA
            try:
                # Comando ghostscript para compressão EXTREMA
                cmd = [
                    'gs',
                    '-sDEVICE=pdfwrite',
                    '-dCompatibilityLevel=1.4',
                    '-dPDFSETTINGS=/screen',  # Máxima compressão
                    '-dNOPAUSE',
                    '-dQUIET',
                    '-dBATCH',
                    '-dColorImageResolution=36',  # Resolução muito baixa
                    '-dGrayImageResolution=36',   # Resolução muito baixa
                    '-dMonoImageResolution=36',   # Resolução muito baixa
                    '-dColorImageDownsampleType=/Bicubic',
                    '-dGrayImageDownsampleType=/Bicubic',
                    '-dMonoImageDownsampleType=/Bicubic',
                    '-dCompressPages=true',
                    '-dUseFlateCompression=true',
                    '-dOptimize=true',
                    f'-sOutputFile={output_path}',
                    input_path
                ]
                
                # Executar ghostscript
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0 and os.path.exists(output_path):
                    # Ghostscript funcionou!
                    compressed_size = PDFCompressor.get_file_size(output_path)
                    reduction_percent = ((original_size - compressed_size) / original_size) * 100
                    
                    stats = {
                        'original_size': original_size,
                        'compressed_size': compressed_size,
                        'reduction_percent': reduction_percent,
                        'original_size_formatted': PDFCompressor.format_file_size(original_size),
                        'compressed_size_formatted': PDFCompressor.format_file_size(compressed_size),
                        'compression_type': 'Máxima'
                    }
                    
                    return True, "Compressão máxima realizada com sucesso", stats
                else:
                    # Se ghostscript falhar, usar fallback
                    raise Exception(f"Ghostscript falhou: {result.stderr}")
                    
            except Exception as gs_error:
                # FALLBACK: PyPDF com compressão extrema se ghostscript falhar
                reader = PdfReader(input_path)
                writer = PdfWriter()
                
                # Processar cada página com compressão EXTREMA
                for page_num, page in enumerate(reader.pages):
                    try:
                        # Adicionar página ao writer
                        writer.add_page(page)
                        
                        # Obter a página adicionada para modificação
                        new_page = writer.pages[-1]
                        
                        # Compressão máxima de conteúdo
                        new_page.compress_content_streams(level=9)
                        
                        # REMOVER TODOS OS ELEMENTOS NÃO ESSENCIAIS
                        elements_to_remove = [
                            '/Annots', '/Link', '/Widget', '/Popup', '/Sound', '/Movie', 
                            '/Screen', '/PrinterMark', '/TrapNet', '/Watermark', '/3D',
                            '/RichMedia', '/AcroForm', '/Metadata', '/StructTreeRoot',
                            '/MarkInfo', '/Lang', '/SpiderInfo', '/PieceInfo', '/LastModified',
                            '/Thumb'
                        ]
                        
                        for element in elements_to_remove:
                            if element in new_page:
                                try:
                                    del new_page[element]
                                except:
                                    pass
                        
                        # SIMPLIFICAR RECURSOS DRASTICAMENTE
                        if '/Resources' in new_page:
                            resources = new_page['/Resources']
                            
                            # Remover recursos desnecessários
                            unnecessary_resources = ['/ColorSpace', '/Pattern', '/Shading', '/ExtGState']
                            for resource in unnecessary_resources:
                                if resource in resources:
                                    try:
                                        del resources[resource]
                                    except:
                                        pass
                        
                    except Exception as page_error:
                        # Se falhar processamento da página, adiciona página simples
                        try:
                            simple_page = reader.pages[page_num]
                            simple_page.compress_content_streams(level=9)
                            writer.add_page(simple_page)
                        except:
                            continue
                
                # REMOVER COMPLETAMENTE TODOS OS METADADOS
                writer.metadata = {}
                
                # Remover objetos duplicados e órfãos de forma agressiva
                writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
                
                # Salvar com compressão máxima
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                compressed_size = PDFCompressor.get_file_size(output_path)
                reduction_percent = ((original_size - compressed_size) / original_size) * 100
                
                stats = {
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'reduction_percent': reduction_percent,
                    'original_size_formatted': PDFCompressor.format_file_size(original_size),
                    'compressed_size_formatted': PDFCompressor.format_file_size(compressed_size),
                    'compression_type': 'Máxima'
                }
                
                return True, "Compressão máxima realizada com sucesso (fallback)", stats
            
        except Exception as e:
            error_msg = PDFCompressor.sanitize_text(str(e))
            return False, f"Erro na compressão máxima: {error_msg}", {}
    
    @staticmethod
    def compress_pdf(input_path: str, compression_type: str = "optimized") -> Tuple[bool, str, dict, Optional[str]]:
        """
        Comprime um arquivo PDF com o tipo de compressão especificado
        
        Args:
            input_path: Caminho para o arquivo PDF original
            compression_type: "optimized" ou "maximum"
            
        Returns:
            Tuple com (sucesso, mensagem, estatísticas, caminho_arquivo_comprimido)
        """
        try:
            # Validar se o arquivo existe
            if not os.path.exists(input_path):
                return False, "Arquivo PDF não encontrado", {}, None
            
            # Criar arquivo temporário para o resultado
            temp_dir = tempfile.gettempdir()
            output_filename = f"compressed_{os.path.basename(input_path)}"
            output_path = os.path.join(temp_dir, output_filename)
            
            # Aplicar compressão baseada no tipo
            if compression_type.lower() == "maximum":
                success, message, stats = PDFCompressor.compress_pdf_maximum(input_path, output_path)
            else:  # default para "optimized"
                success, message, stats = PDFCompressor.compress_pdf_optimized(input_path, output_path)
            
            if success:
                return True, message, stats, output_path
            else:
                return False, message, stats, None
                
        except Exception as e:
            error_msg = PDFCompressor.sanitize_text(str(e))
            return False, f"Erro geral na compressão: {error_msg}", {}, None
