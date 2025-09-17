import os
import tempfile
import re
from pypdf import PdfWriter
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
        Compressão otimizada: Remove duplicação + compressão lossless
        Mantém qualidade visual enquanto reduz tamanho
        """
        try:
            original_size = PDFCompressor.get_file_size(input_path)
            
            # Criar writer a partir do PDF original
            writer = PdfWriter(clone_from=input_path)
            
            # Aplicar compressão lossless em todas as páginas
            for page in writer.pages:
                page.compress_content_streams(level=6)  # Nível médio de compressão
            
            # Remover objetos duplicados e órfãos
            writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
            
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
            
            return True, "Compressão otimizada realizada com sucesso", stats
            
        except Exception as e:
            error_msg = PDFCompressor.sanitize_text(str(e))
            return False, f"Erro na compressão otimizada: {error_msg}", {}
    
    @staticmethod
    def compress_pdf_maximum(input_path: str, output_path: str) -> Tuple[bool, str, dict]:
        """
        Compressão máxima: Remove duplicação + compressão lossless máxima + redução de qualidade de imagem
        Máxima redução de tamanho com alguma perda de qualidade visual
        """
        try:
            original_size = PDFCompressor.get_file_size(input_path)
            
            # Criar writer a partir do PDF original
            writer = PdfWriter(clone_from=input_path)
            
            # Aplicar compressão lossless máxima em todas as páginas
            for page in writer.pages:
                page.compress_content_streams(level=9)  # Máximo nível de compressão
                
                # Reduzir qualidade das imagens para 60%
                for img in page.images:
                    try:
                        img.replace(img.image, quality=60)
                    except:
                        # Se não conseguir reduzir qualidade, continua sem erro
                        pass
            
            # Remover objetos duplicados e órfãos
            writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
            
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
                'compression_type': 'Máxima'
            }
            
            return True, "Compressão máxima realizada com sucesso", stats
            
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
