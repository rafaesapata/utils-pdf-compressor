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
        try:
            return os.path.getsize(file_path)
        except:
            return 0
    
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
    def validate_pdf(file_path: str) -> Tuple[bool, str]:
        """Valida se o arquivo é um PDF válido"""
        try:
            if not os.path.exists(file_path):
                return False, "Arquivo não encontrado"
            
            if os.path.getsize(file_path) == 0:
                return False, "Arquivo está vazio"
            
            # Tentar ler o PDF
            with open(file_path, 'rb') as f:
                try:
                    reader = PdfReader(f)
                    if len(reader.pages) == 0:
                        return False, "PDF não contém páginas"
                    return True, "PDF válido"
                except Exception as e:
                    return False, f"PDF corrompido: {str(e)}"
                    
        except Exception as e:
            return False, f"Erro ao validar PDF: {str(e)}"
    
    @staticmethod
    def fallback_pypdf_compression(input_path: str, output_path: str, level: int = 6) -> Tuple[bool, str]:
        """Compressão fallback usando apenas PyPDF"""
        try:
            with open(input_path, 'rb') as input_file:
                reader = PdfReader(input_file)
                writer = PdfWriter()
                
                # Copiar páginas com tratamento de erro
                for page_num in range(len(reader.pages)):
                    try:
                        page = reader.pages[page_num]
                        writer.add_page(page)
                    except Exception as e:
                        print(f"Erro na página {page_num}: {e}")
                        continue
                
                # Aplicar compressão básica
                writer.compress_identical_objects()
                writer.remove_duplication()
                
                # Salvar arquivo comprimido
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                return True, "Compressão PyPDF realizada com sucesso"
                
        except Exception as e:
            return False, f"Erro na compressão PyPDF: {str(e)}"
    
    @staticmethod
    def compress_pdf_optimized(input_path: str, output_path: str) -> Tuple[bool, str, dict]:
        """
        Compressão otimizada: Usa Ghostscript com configurações balanceadas
        Mantém boa qualidade visual com redução significativa de tamanho
        """
        try:
            # Validar PDF de entrada
            is_valid, validation_msg = PDFCompressor.validate_pdf(input_path)
            if not is_valid:
                return False, f"PDF inválido: {validation_msg}", {}
            
            original_size = PDFCompressor.get_file_size(input_path)
            
            # Tentar usar Ghostscript primeiro
            try:
                cmd = [
                    'gs',
                    '-sDEVICE=pdfwrite',
                    '-dCompatibilityLevel=1.4',
                    '-dPDFSETTINGS=/ebook',
                    '-dNOPAUSE',
                    '-dQUIET',
                    '-dBATCH',
                    '-dColorImageResolution=150',
                    '-dGrayImageResolution=150',
                    '-dMonoImageResolution=300',
                    '-sOutputFile=' + output_path,
                    input_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    compressed_size = PDFCompressor.get_file_size(output_path)
                    reduction = ((original_size - compressed_size) / original_size) * 100
                    
                    stats = {
                        'original_size': original_size,
                        'compressed_size': compressed_size,
                        'reduction_percentage': round(reduction, 1),
                        'method': 'Ghostscript Otimizado'
                    }
                    
                    return True, "Compressão otimizada realizada com sucesso", stats
                else:
                    # Fallback para PyPDF
                    success, msg = PDFCompressor.fallback_pypdf_compression(input_path, output_path, level=6)
                    if success:
                        compressed_size = PDFCompressor.get_file_size(output_path)
                        reduction = ((original_size - compressed_size) / original_size) * 100
                        
                        stats = {
                            'original_size': original_size,
                            'compressed_size': compressed_size,
                            'reduction_percentage': round(reduction, 1),
                            'method': 'PyPDF Fallback'
                        }
                        
                        return True, "Compressão otimizada realizada (fallback)", stats
                    else:
                        return False, f"Falha na compressão: {msg}", {}
                        
            except subprocess.TimeoutExpired:
                return False, "Timeout na compressão - arquivo muito grande", {}
            except FileNotFoundError:
                # Ghostscript não instalado, usar PyPDF
                success, msg = PDFCompressor.fallback_pypdf_compression(input_path, output_path, level=6)
                if success:
                    compressed_size = PDFCompressor.get_file_size(output_path)
                    reduction = ((original_size - compressed_size) / original_size) * 100
                    
                    stats = {
                        'original_size': original_size,
                        'compressed_size': compressed_size,
                        'reduction_percentage': round(reduction, 1),
                        'method': 'PyPDF (Ghostscript não disponível)'
                    }
                    
                    return True, "Compressão otimizada realizada (PyPDF)", stats
                else:
                    return False, f"Falha na compressão: {msg}", {}
                    
        except Exception as e:
            return False, f"Erro inesperado na compressão otimizada: {str(e)}", {}
    
    @staticmethod
    def compress_pdf_maximum(input_path: str, output_path: str) -> Tuple[bool, str, dict]:
        """
        Compressão máxima: Usa Ghostscript com configurações agressivas
        Máxima redução de tamanho com qualidade aceitável
        """
        try:
            # Validar PDF de entrada
            is_valid, validation_msg = PDFCompressor.validate_pdf(input_path)
            if not is_valid:
                return False, f"PDF inválido: {validation_msg}", {}
            
            original_size = PDFCompressor.get_file_size(input_path)
            
            # Tentar usar Ghostscript primeiro
            try:
                cmd = [
                    'gs',
                    '-sDEVICE=pdfwrite',
                    '-dCompatibilityLevel=1.4',
                    '-dPDFSETTINGS=/screen',
                    '-dNOPAUSE',
                    '-dQUIET',
                    '-dBATCH',
                    '-dColorImageResolution=36',
                    '-dGrayImageResolution=36',
                    '-dMonoImageResolution=36',
                    '-sOutputFile=' + output_path,
                    input_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    compressed_size = PDFCompressor.get_file_size(output_path)
                    reduction = ((original_size - compressed_size) / original_size) * 100
                    
                    stats = {
                        'original_size': original_size,
                        'compressed_size': compressed_size,
                        'reduction_percentage': round(reduction, 1),
                        'method': 'Ghostscript Máximo'
                    }
                    
                    return True, "Compressão máxima realizada com sucesso", stats
                else:
                    # Fallback para PyPDF
                    success, msg = PDFCompressor.fallback_pypdf_compression(input_path, output_path, level=9)
                    if success:
                        compressed_size = PDFCompressor.get_file_size(output_path)
                        reduction = ((original_size - compressed_size) / original_size) * 100
                        
                        stats = {
                            'original_size': original_size,
                            'compressed_size': compressed_size,
                            'reduction_percentage': round(reduction, 1),
                            'method': 'PyPDF Fallback'
                        }
                        
                        return True, "Compressão máxima realizada (fallback)", stats
                    else:
                        return False, f"Falha na compressão: {msg}", {}
                        
            except subprocess.TimeoutExpired:
                return False, "Timeout na compressão - arquivo muito grande", {}
            except FileNotFoundError:
                # Ghostscript não instalado, usar PyPDF
                success, msg = PDFCompressor.fallback_pypdf_compression(input_path, output_path, level=9)
                if success:
                    compressed_size = PDFCompressor.get_file_size(output_path)
                    reduction = ((original_size - compressed_size) / original_size) * 100
                    
                    stats = {
                        'original_size': original_size,
                        'compressed_size': compressed_size,
                        'reduction_percentage': round(reduction, 1),
                        'method': 'PyPDF (Ghostscript não disponível)'
                    }
                    
                    return True, "Compressão máxima realizada (PyPDF)", stats
                else:
                    return False, f"Falha na compressão: {msg}", {}
                    
        except Exception as e:
            return False, f"Erro inesperado na compressão máxima: {str(e)}", {}
