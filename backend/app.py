"""
Flask Backend Application for Infrastructure Cascade Failure Detection
Handles file uploads, parsing, and data processing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
from ingestion import XMLParser

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
ALLOWED_EXTENSIONS = {'xml', 'osm'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Infrastructure Cascade Detection API'
    }), 200


@app.route('/api/parse/xml', methods=['POST'])
def parse_xml():
    """
    Upload and parse XML file
    
    Returns:
        JSON with parsed infrastructure data
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logger.info(f"File saved: {filepath}")
        
        # Parse XML
        parser = XMLParser()
        file_type, data = parser.parse_file(filepath)
        
        return jsonify({
            'status': 'success',
            'file_type': file_type,
            'file_name': filename,
            'data_count': len(data),
            'data': data[:100] if len(data) > 100 else data,  # Limit initial response
            'total_records': len(data)
        }), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error parsing XML: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Generic file upload endpoint
    Accepts XML/OSM files for power and water infrastructure parsing
    Auto-exports to Excel in data/processed/
    
    Returns:
        JSON with parsed data and file information
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logger.info(f"File saved: {filepath}")
        
        # Parse and auto-convert to Excel
        parser = XMLParser()
        file_type, data = parser.parse_file(filepath)
        
        # Auto-export to Excel
        excel_path = parser.export_to_excel()
        
        return jsonify({
            'status': 'success',
            'file_type': file_type,
            'file_name': filename,
            'data_count': len(data),
            'data': data[:100] if len(data) > 100 else data,  # Show first 100 records
            'total_records': len(data),
            'excel_output': os.path.basename(excel_path),
            'excel_path': excel_path
        }), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error uploading/parsing file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/export/<export_format>', methods=['POST'])
def export_data(export_format):
    """
    Export parsed data in different formats
    
    Args:
        export_format: 'json' or 'excel'
        
    Request body:
        {
            "file_path": "/path/to/file.osm"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify({'error': 'No file path provided'}), 400
        
        file_path = data['file_path']
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Only handle XML/OSM files
        file_ext = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''
        
        if file_ext not in ['xml', 'osm']:
            return jsonify({'error': 'Unsupported file format. Use XML or OSM files.'}), 400
        
        # Parse the file
        parser = XMLParser()
        parser.parse_file(file_path)
        
        # Export in requested format
        output_filename = os.path.splitext(os.path.basename(file_path))[0]
        
        if export_format == 'json':
            output_path = os.path.join(
                os.path.dirname(__file__), '..', 'data', 'processed',
                f"{output_filename}.json"
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            parser.export_to_json(output_path)
        elif export_format == 'excel':
            output_path = parser.export_to_excel()
        else:
            return jsonify({'error': 'Unsupported export format. Use "json" or "excel".'}), 400
        
        return jsonify({
            'status': 'success',
            'message': f'Data exported to {export_format}',
            'output_path': output_path,
            'output_file': os.path.basename(output_path)
        }), 200
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
