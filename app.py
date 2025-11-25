"""
Aplicação Flask - Synapse
API REST e servidor web
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys

# Adiciona src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.neo4j_service import get_neo4j_service
from src.chroma_service import get_chroma_service
from src.synapse_core import SynapseCore

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa Flask
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Inicializa serviços (lazy loading)
_synapse = None

def get_synapse() -> SynapseCore:
    """Retorna instância singleton do Synapse"""
    global _synapse
    if _synapse is None:
        print("🚀 Inicializando Synapse...")
        neo4j = get_neo4j_service()
        chroma = get_chroma_service()
        _synapse = SynapseCore(neo4j, chroma)
        print("✅ Synapse inicializado!")
    return _synapse


# ============================================================================
# ROTAS HTML
# ============================================================================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


# ============================================================================
# API REST
# ============================================================================

@app.route('/api/notes', methods=['POST'])
def create_note():
    """
    Cria nova anotação
    
    Body:
        {
            "title": "Título",
            "content": "Conteúdo",
            "tags": ["tag1", "tag2"]
        }
    """
    try:
        data = request.get_json()
        
        # Validação
        if not data.get('title') or not data.get('content'):
            return jsonify({"error": "Título e conteúdo são obrigatórios"}), 400
        
        synapse = get_synapse()
        note = synapse.create_note(
            title=data['title'],
            content=data['content'],
            tags=data.get('tags', [])
        )
        
        return jsonify({
            "success": True,
            "note": note
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Lista todas as anotações"""
    try:
        limit = request.args.get('limit', 100, type=int)
        synapse = get_synapse()
        notes = synapse.get_all_notes(limit=limit)
        
        return jsonify({
            "success": True,
            "notes": notes,
            "count": len(notes)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/notes/<note_id>', methods=['GET'])
def get_note(note_id):
    """Recupera uma anotação específica"""
    try:
        synapse = get_synapse()
        note = synapse.get_note(note_id)
        
        if note:
            return jsonify({
                "success": True,
                "note": note
            })
        else:
            return jsonify({"error": "Anotação não encontrada"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/notes/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Deleta uma anotação"""
    try:
        synapse = get_synapse()
        success = synapse.delete_note(note_id)
        
        return jsonify({
            "success": success,
            "message": "Anotação deletada com sucesso"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search_notes():
    """
    Busca semântica de anotações
    
    Body:
        {
            "query": "Como funciona herança em Java?",
            "top_k": 5
        }
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "Query é obrigatória"}), 400
        
        top_k = data.get('top_k', 5)
        
        synapse = get_synapse()
        results = synapse.search_notes(query, top_k=top_k)
        
        return jsonify({
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retorna estatísticas do sistema"""
    try:
        synapse = get_synapse()
        stats = synapse.get_stats()
        
        return jsonify({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "service": "Synapse API"
    })


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════╗
    ║           🧠 SYNAPSE - STARTING           ║
    ║  Organizador Semântico de Anotações      ║
    ╚═══════════════════════════════════════════╝
    """)
    
    # Verifica se Neo4j está acessível
    try:
        get_synapse()
    except Exception as e:
        print(f"\n❌ ERRO: Não foi possível inicializar o Synapse")
        print(f"   {e}")
        print("\n💡 Certifique-se de que:")
        print("   1. O Neo4j está rodando (docker-compose up -d)")
        print("   2. As variáveis de ambiente estão configuradas (.env)")
        sys.exit(1)
    
    # Inicia servidor
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"\n🌐 Servidor rodando em: http://localhost:{port}")
    print(f"📊 Neo4j Browser: http://localhost:7474")
    print("\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
