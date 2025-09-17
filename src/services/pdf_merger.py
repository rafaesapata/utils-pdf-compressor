import os
import tempfile
from typing import List, Tuple
from pypdf import PdfWriter, PdfReader
import re

class PDFMerger:
    """
    Serviço para mesclagem de múltiplos arquivos PDF
    """
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Remove caracteres UTF-8 inválidos"""
        return re.sub(r'[^\x00-\x7F]+', '?', str(text))
    
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
    def merge_pdfs(input_files: List[str], output_path: str) -> Tuple[bool, str, dict]:
        """
        Mescla múltiplos arquivos PDF em um único arquivo
        
        Args:
            input_files: Lista de caminhos dos arquivos PDF de entrada
            output_path: Caminho do arquivo PDF de saída
            
        Returns:
            Tuple[bool, str, dict]: (sucesso, mensagem, estatísticas)
        """
        try:
            if not input_files:
                return False, "Nenhum arquivo fornecido para mesclagem", {}
            
            if len(input_files) < 2:
                return False, "É necessário pelo menos 2 arquivos para mesclagem", {}
            
            # Verificar se todos os arquivos existem
            for file_path in input_files:
                if not os.path.exists(file_path):
                    return False, f"Arquivo não encontrado: {os.path.basename(file_path)}", {}
            
            # Calcular tamanho total dos arquivos de entrada
            total_input_size = sum(PDFMerger.get_file_size(file_path) for file_path in input_files)
            
            # Criar writer para o PDF mesclado
            writer = PdfWriter()
            
            # Contador de páginas
            total_pages = 0
            file_info = []
            
            # Processar cada arquivo PDF
            for i, file_path in enumerate(input_files):
                try:
                    # Ler PDF
                    reader = PdfReader(file_path)
                    num_pages = len(reader.pages)
                    
                    # Adicionar todas as páginas ao writer
                    for page in reader.pages:
                        writer.add_page(page)
                    
                    total_pages += num_pages
                    
                    # Armazenar informações do arquivo
                    file_info.append({
                        'name': os.path.basename(file_path),
                        'size': PDFMerger.get_file_size(file_path),
                        'pages': num_pages
                    })
                    
                except Exception as e:
                    error_msg = PDFMerger.sanitize_text(str(e))
                    return False, f"Erro ao processar {os.path.basename(file_path)}: {error_msg}", {}
            
            # Salvar arquivo mesclado
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Calcular tamanho do arquivo de saída
            output_size = PDFMerger.get_file_size(output_path)
            
            # Preparar estatísticas
            stats = {
                'total_files': len(input_files),
                'total_input_size': total_input_size,
                'output_size': output_size,
                'total_pages': total_pages,
                'total_input_size_formatted': PDFMerger.format_file_size(total_input_size),
                'output_size_formatted': PDFMerger.format_file_size(output_size),
                'file_info': file_info,
                'compression_ratio': ((total_input_size - output_size) / total_input_size) * 100 if total_input_size > 0 else 0
            }
            
            return True, f"Mesclagem realizada com sucesso! {len(input_files)} arquivos mesclados em {total_pages} páginas.", stats
            
        except Exception as e:
            error_msg = PDFMerger.sanitize_text(str(e))
            return False, f"Erro na mesclagem: {error_msg}", {}
    
    @staticmethod
    def validate_pdf_files(file_paths: List[str]) -> Tuple[bool, str]:
        """
        Valida se todos os arquivos são PDFs válidos
        
        Args:
            file_paths: Lista de caminhos dos arquivos
            
        Returns:
            Tuple[bool, str]: (válido, mensagem de erro se houver)
        """
        try:
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    return False, f"Arquivo não encontrado: {os.path.basename(file_path)}"
                
                # Tentar ler o PDF para validar
                try:
                    reader = PdfReader(file_path)
                    # Verificar se tem pelo menos uma página
                    if len(reader.pages) == 0:
                        return False, f"PDF vazio: {os.path.basename(file_path)}"
                except Exception as e:
                    return False, f"PDF inválido: {os.path.basename(file_path)} - {str(e)}"
            
            return True, "Todos os arquivos são PDFs válidos"
            
        except Exception as e:
            error_msg = PDFMerger.sanitize_text(str(e))
            return False, f"Erro na validação: {error_msg}"
