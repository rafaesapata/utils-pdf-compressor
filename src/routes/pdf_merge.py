import os
import tempfile
import uuid
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from src.services.pdf_merger import PDFMerger

pdf_merge_bp = Blueprint('pdf_merge', __name__)

# Configurações
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB por arquivo
MAX_FILES = 10  # Máximo 10 arquivos por mesclagem

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    """Valida o tamanho do arquivo"""
    file.seek(0, 2)  # Ir para o final do arquivo
    size = file.tell()
    file.seek(0)  # Voltar para o início
    return size <= MAX_FILE_SIZE

@pdf_merge_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se o serviço de mesclagem está funcionando"""
    return jsonify({
        'success': True,
        'message': 'Serviço de mesclagem PDF funcionando corretamente',
        'service': 'UDS Utils - PDF Merge'
    })

@pdf_merge_bp.route('/info', methods=['GET'])
def merge_info():
    """Endpoint com informações sobre a mesclagem"""
    return jsonify({
        'success': True,
        'service': 'UDS Utils - PDF Merge',
        'max_files': MAX_FILES,
        'max_file_size': f'{MAX_FILE_SIZE // (1024 * 1024)}MB',
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'description': 'Mescla múltiplos arquivos PDF e imagens PNG/JPG em um único documento PDF'
    })


@pdf_merge_bp.route('/merge', methods=['POST'])
def merge_pdfs():
    """Endpoint para mesclar múltiplos arquivos PDF"""
    try:
        # Verificar se há arquivos na requisição
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo enviado'
            }), 400
        
        files = request.files.getlist('files')
        
        # Validar número de arquivos
        if len(files) < 2:
            return jsonify({
                'success': False,
                'error': 'É necessário pelo menos 2 arquivos para mesclagem'
            }), 400
        
        if len(files) > MAX_FILES:
            return jsonify({
                'success': False,
                'error': f'Máximo de {MAX_FILES} arquivos permitidos'
            }), 400
        
        # Validar arquivos
        temp_files = []
        file_names = []
        
        try:
            for i, file in enumerate(files):
                # Verificar se arquivo foi selecionado
                if file.filename == '':
                    return jsonify({
                        'success': False,
                        'error': f'Arquivo {i+1} não foi selecionado'
                    }), 400
                
                # Verificar extensão
                if not allowed_file(file.filename):
                    return jsonify({
                        'success': False,
                        'error': f'Arquivo {file.filename} não é um tipo suportado (PDF, PNG, JPG)'
                    }), 400
                
                # Verificar tamanho
                if not validate_file_size(file):
                    return jsonify({
                        'success': False,
                        'error': f'Arquivo {file.filename} excede o tamanho máximo de {MAX_FILE_SIZE // (1024 * 1024)}MB'
                    }), 400
                
                # Salvar arquivo temporário mantendo extensão original
                file_ext = os.path.splitext(file.filename)[1].lower()
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
                file.save(temp_file.name)
                temp_files.append(temp_file.name)
                file_names.append(secure_filename(file.filename))
            
            # Validar se todos os arquivos são válidos (PDFs e imagens)
            is_valid, validation_message = PDFMerger.validate_files(temp_files)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': validation_message
                }), 400
            
            # Criar arquivo de saída
            output_filename = f"merged_pdf_{uuid.uuid4().hex[:8]}.pdf"
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf').name
            
            # Realizar mesclagem (PDFs e imagens)
            success, message, stats = PDFMerger.merge_files(temp_files, output_path)
            
            if not success:
                return jsonify({
                    'success': False,
                    'error': message
                }), 500
            
            # Retornar arquivo mesclado
            return send_file(
                output_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/pdf'
            )
            
        finally:
            # Limpar arquivos temporários de entrada
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno do servidor: {str(e)}'
        }), 500
