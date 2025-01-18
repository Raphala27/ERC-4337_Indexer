from flask import Flask, jsonify, request, render_template
from .database import get_events
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='templates')

@app.route("/events", methods=["GET"])
def get_events_route():
    # Récupérer les filtres depuis les paramètres de requête
    filters = {}
    for param in ['userOpHash', 'sender', 'paymaster', 'success', 
                'blockNumber', 'fromBlock', 'toBlock']:
        if param in request.args:
            filters[param] = request.args[param]
    
    # Récupérer les événements filtrés
    events = get_events(filters)
    
    return jsonify({"events": events})

@app.route("/", methods=["GET"])
def home():
    return render_template('index.html')

def start_api():
    """Démarre le serveur Flask"""
    app.run(
        host=os.getenv('FLASK_HOST'),
        port=int(os.getenv('FLASK_PORT')),
        debug=os.getenv('FLASK_DEBUG').lower() == 'true'
    )