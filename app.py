from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import os

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações
MODEL_NAME = "ealvaradob/bert-finetuned-phishing"

# Caminho absoluto para o banco de dados (melhor compatibilidade no Windows)
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'phishing_history.db')

# Inicializar o Flask
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)

# Banco de Dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path.replace('\\', '/')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ScannedURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    result = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'result': self.result,
            'confidence': round(self.confidence * 100, 2) if self.confidence else None,
            'description': self.description,
            'timestamp': self.timestamp.strftime('%H:%M - %d/%m/%Y')
        }

# Criar banco de dados se não existir
with app.app_context():
    db.create_all()

from agents.orchestrator import PhishingOrchestrator

# ... (logging and db config remain the same)

# Inicializar o Orquestrador Multi-Agente
orchestrator = PhishingOrchestrator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check for multi-part form data (for images) or JSON
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            
        url = data.get('url', '').strip()
        text = data.get('text', '').strip()
        html = data.get('html', '').strip()
        
        image_data = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Process small images in memory or save them
                image_data = file.read()
        elif 'image_b64' in data:
            import base64
            image_data = base64.b64decode(data['image_b64'].split(',')[-1])

        logger.info(f"Analisando Multi-Modal: URL={url}, Text={bool(text)}, HTML={bool(html)}, Image={bool(image_data)}")

        if not any([url, text, html, image_data]):
            return jsonify({'error': 'Nenhum dado fornecido para análise.'}), 400

        # Executar análise multi-modal
        results = orchestrator.analyze_full(url=url, text=text, html=html, image_data=image_data)
        
        result = results['verdict']
        confidence = results['risk_score']
        description = results['summary']

        # Salvar no Banco de Dados (usamos a URL ou um placeholder se for só texto/imagem)
        record_url = url if url else f"Analysis: {datetime.now().strftime('%H:%M:%S')}"
        try:
            new_scan = ScannedURL(
                url=record_url,
                result=result,
                confidence=confidence,
                description=description
            )
            db.session.add(new_scan)
            db.session.commit()
        except Exception as db_err:
            logger.error(f"Erro ao salvar no banco: {db_err}")

        response = {
            'result': result,
            'url': record_url,
            'description': description,
            'confidence': round(confidence * 100, 2),
            'agent_details': results['agent_details']
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Erro ao processar requisição multi-modal: {e}")
        return jsonify({'error': 'Erro interno do servidor.'}), 500

@app.route('/history', methods=['GET'])
def get_history():
    try:
        # Pega as últimas 10 análises
        history = ScannedURL.query.order_by(ScannedURL.timestamp.desc()).limit(10).all()
        return jsonify([item.to_dict() for item in history])
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {e}")
        return jsonify({'error': 'Erro ao buscar histórico.'}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    try:
        total = ScannedURL.query.count()
        phishing = ScannedURL.query.filter_by(result='Phishing').count()
        suspect = ScannedURL.query.filter_by(result='Suspeito').count()
        safe = ScannedURL.query.filter(ScannedURL.result.in_(['Legítima', 'Safe'])).count()
        
        # Média de confiança
        from sqlalchemy import func
        avg_conf = db.session.query(func.avg(ScannedURL.confidence)).scalar() or 0
        
        # Taxa de detecção (phishing + suspeito / total)
        detection_rate = round(((phishing + suspect) / total * 100), 1) if total > 0 else 0
        
        # Últimas 7 análises para o mini-gráfico
        recent = ScannedURL.query.order_by(ScannedURL.timestamp.desc()).limit(7).all()
        timeline = [{'date': r.timestamp.strftime('%d/%m'), 'result': r.result} for r in reversed(recent)]
        
        return jsonify({
            'total': total,
            'phishing': phishing,
            'suspect': suspect,
            'safe': safe,
            'detection_rate': detection_rate,
            'avg_confidence': round(avg_conf * 100, 1),
            'timeline': timeline
        })
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return jsonify({'error': 'Erro ao buscar estatísticas.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
