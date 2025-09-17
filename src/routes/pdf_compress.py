import os
import tempfile
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from src.services.pdf_compressor import PDFCompressor
import re

pdf_compress_bp = Blueprint('pdf_compress', __name__)

ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def sanitize_text(text: str) -> str:
    """Remove caracteres nulos e UTF-8 inválidos"""
    if not text:
        return ""
    # Remove caracteres nulos
    text = text.replace('\x00', '')
    # Remove outros caracteres de controle problemáticos
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    return text

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@pdf_compress_bp.route('/compress', methods=['POST'])
def compress_pdf():
    """Endpoint para compressão de PDF"""
    try:
        # Verificar se foi enviado um arquivo
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Nenhum arquivo foi enviado'
            }), 400
        
        file = request.files['file']
        compression_type = request.form.get('compression_type', 'optimized')
        
        # Validar nome do arquivo
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'Nenhum arquivo foi selecionado'
            }), 400
        
        # Sanitizar nome do arquivo
        original_filename = sanitize_text(file.filename)
        
        # Verificar extensão
        if not allowed_file(original_filename):
            return jsonify({
                'success': False,
                'message': 'Apenas arquivos PDF são permitidos'
            }), 400
        
        # Verificar tamanho do arquivo
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'message': f'Arquivo muito grande. Tamanho máximo: {MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        # Salvar arquivo temporariamente
        temp_dir = tempfile.gettempdir()
        filename = secure_filename(original_filename)
        temp_input_path = os.path.join(temp_dir, f"input_{filename}")
        
        file.save(temp_input_path)
        
        try:
            # Comprimir PDF
            success, message, stats, output_path = PDFCompressor.compress_pdf(
                temp_input_path, 
                compression_type
            )
            
            if success and output_path:
                # Preparar resposta com estatísticas
                response_data = {
                    'success': True,
                    'message': message,
                    'stats': stats,
                    'original_filename': original_filename,
                    'compressed_filename': f"compressed_{filename}"
                }
                
                # Retornar arquivo comprimido
                return send_file(
                    output_path,
                    as_attachment=True,
                    download_name=f"compressed_{filename}",
                    mimetype='application/pdf'
                )
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 500
                
        finally:
            # Limpar arquivo temporário de entrada
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
    
    except Exception as e:
        error_msg = sanitize_text(str(e))
        return jsonify({
            'success': False,
            'message': f'Erro interno do servidor: {error_msg}'
        }), 500

@pdf_compress_bp.route('/info', methods=['GET'])
def get_compression_info():
    """Endpoint para obter informações sobre os tipos de compressão"""
    return jsonify({
        'success': True,
        'compression_types': {
            'optimized': {
                'name': 'Otimizada',
                'description': 'Compressão avançada com redução significativa de tamanho. Mantém excelente qualidade visual.',
                'recommended_for': 'Uso geral e documentos importantes onde qualidade e tamanho são importantes'
            },
            "maximum": {
                "name": "Máxima",
                "description": "Compressão agressiva com redução de qualidade de imagens (até 70%). Máxima economia de espaço.",
                "recommended_for": "Arquivos onde o tamanho é mais importante que a qualidade visual"
            }
        },
        'max_file_size': f'{MAX_FILE_SIZE // (1024*1024)}MB',
        'allowed_extensions': list(ALLOWED_EXTENSIONS)
    })

@pdf_compress_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar saúde do serviço"""
    return jsonify({
        'success': True,
        'message': 'Serviço de compressão PDF funcionando corretamente',
        'service': 'UDS Utils - PDF Compress'
    })
