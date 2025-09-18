import os
import tempfile
from typing import List, Tuple
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, landscape, portrait
from PIL import Image
import re

class PDFMerger:
    """
    Serviço para mesclagem de múltiplos arquivos PDF e imagens PNG
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
    def get_file_type(file_path: str) -> str:
        """Identifica o tipo do arquivo baseado na extensão"""
        _, ext = os.path.splitext(file_path.lower())
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.png', '.jpg', '.jpeg']:
            return 'image'
        else:
            return 'unknown'
    
    @staticmethod
    def convert_image_to_pdf(image_path: str, output_path: str) -> Tuple[bool, str]:
        """
        Converte uma imagem PNG/JPG para PDF
        
        Args:
            image_path: Caminho da imagem
            output_path: Caminho do PDF de saída
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # Abrir imagem
            with Image.open(image_path) as img:
                # Converter para RGB se necessário (PNG pode ter transparência)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Criar fundo branco
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Obter dimensões da imagem
                img_width, img_height = img.size
                
                # Detectar orientação da imagem e ajustar página
                is_landscape = img_width > img_height
                
                if is_landscape:
                    # Imagem paisagem -> página paisagem
                    page_width, page_height = A4[1], A4[0]  # Inverter dimensões (842 x 595)
                    pagesize = landscape(A4)
                else:
                    # Imagem retrato -> página retrato
                    page_width, page_height = A4  # Manter dimensões (595 x 842)
                    pagesize = portrait(A4)
                
                # Calcular escala para ajustar a imagem na página mantendo proporção
                scale_x = page_width / img_width
                scale_y = page_height / img_height
                scale = min(scale_x, scale_y) * 0.9  # 90% da página para margem
                
                # Calcular dimensões finais
                final_width = img_width * scale
                final_height = img_height * scale
                
                # Calcular posição para centralizar
                x = (page_width - final_width) / 2
                y = (page_height - final_height) / 2
                
                # Criar PDF com orientação correta
                c = canvas.Canvas(output_path, pagesize=pagesize)
                
                # Salvar imagem temporariamente como JPEG para reportlab
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_img:
                    img.save(temp_img.name, 'JPEG', quality=95)
                    temp_img_path = temp_img.name
                
                try:
                    # Adicionar imagem ao PDF
                    c.drawImage(temp_img_path, x, y, width=final_width, height=final_height)
                    c.save()
                    
                    return True, "Imagem convertida para PDF com sucesso"
                    
                finally:
                    # Limpar arquivo temporário
                    if os.path.exists(temp_img_path):
                        os.unlink(temp_img_path)
                        
        except Exception as e:
            return False, f"Erro ao converter imagem: {str(e)}"
    
    @staticmethod
    def merge_files(input_files: List[str], output_path: str) -> Tuple[bool, str, dict]:
        """
        Mescla múltiplos arquivos PDF e imagens em um único PDF
        
        Args:
            input_files: Lista de caminhos dos arquivos (PDF e PNG/JPG)
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
            temp_files = []  # Para limpar arquivos temporários
            
            # Processar cada arquivo
            for i, file_path in enumerate(input_files):
                try:
                    file_type = PDFMerger.get_file_type(file_path)
                    file_name = os.path.basename(file_path)
                    file_size = PDFMerger.get_file_size(file_path)
                    
                    if file_type == 'pdf':
                        # Processar PDF
                        reader = PdfReader(file_path)
                        num_pages = len(reader.pages)
                        
                        # Adicionar todas as páginas ao writer
                        for page in reader.pages:
                            writer.add_page(page)
                        
                        total_pages += num_pages
                        
                        file_info.append({
                            'name': file_name,
                            'type': 'PDF',
                            'size': file_size,
                            'pages': num_pages
                        })
                        
                    elif file_type == 'image':
                        # Converter imagem para PDF temporário
                        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                            temp_pdf_path = temp_pdf.name
                            temp_files.append(temp_pdf_path)
                        
                        success, msg = PDFMerger.convert_image_to_pdf(file_path, temp_pdf_path)
                        
                        if success:
                            # Ler PDF temporário e adicionar ao writer
                            reader = PdfReader(temp_pdf_path)
                            for page in reader.pages:
                                writer.add_page(page)
                            
                            total_pages += 1  # Imagem = 1 página
                            
                            file_info.append({
                                'name': file_name,
                                'type': 'Imagem (convertida)',
                                'size': file_size,
                                'pages': 1
                            })
                        else:
                            return False, f"Erro ao converter {file_name}: {msg}", {}
                    
                    else:
                        return False, f"Tipo de arquivo não suportado: {file_name}", {}
                        
                except Exception as e:
                    error_msg = PDFMerger.sanitize_text(str(e))
                    return False, f"Erro ao processar {os.path.basename(file_path)}: {error_msg}", {}
            
            # Salvar arquivo mesclado
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Limpar arquivos temporários
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass
            
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
    def validate_files(file_paths: List[str]) -> Tuple[bool, str]:
        """
        Valida se todos os arquivos são PDFs ou imagens válidas
        
        Args:
            file_paths: Lista de caminhos dos arquivos
            
        Returns:
            Tuple[bool, str]: (válido, mensagem de erro se houver)
        """
        try:
            supported_types = ['.pdf', '.png', '.jpg', '.jpeg']
            
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    return False, f"Arquivo não encontrado: {os.path.basename(file_path)}"
                
                # Verificar extensão
                _, ext = os.path.splitext(file_path.lower())
                if ext not in supported_types:
                    return False, f"Tipo de arquivo não suportado: {os.path.basename(file_path)} (suportados: PDF, PNG, JPG)"
                
                file_type = PDFMerger.get_file_type(file_path)
                
                if file_type == 'pdf':
                    # Validar PDF
                    try:
                        reader = PdfReader(file_path)
                        if len(reader.pages) == 0:
                            return False, f"PDF vazio: {os.path.basename(file_path)}"
                    except Exception as e:
                        return False, f"PDF inválido: {os.path.basename(file_path)} - {str(e)}"
                
                elif file_type == 'image':
                    # Validar imagem
                    try:
                        with Image.open(file_path) as img:
                            # Verificar se a imagem pode ser aberta
                            img.verify()
                    except Exception as e:
                        return False, f"Imagem inválida: {os.path.basename(file_path)} - {str(e)}"
            
            return True, "Todos os arquivos são válidos"
            
        except Exception as e:
            error_msg = PDFMerger.sanitize_text(str(e))
            return False, f"Erro na validação: {error_msg}"
    
    # Manter compatibilidade com código existente
    @staticmethod
    def merge_pdfs(input_files: List[str], output_path: str) -> Tuple[bool, str, dict]:
        """Alias para merge_files para compatibilidade"""
        return PDFMerger.merge_files(input_files, output_path)
    
    @staticmethod
    def validate_pdf_files(file_paths: List[str]) -> Tuple[bool, str]:
        """Alias para validate_files para compatibilidade"""
        return PDFMerger.validate_files(file_paths)
