import sqlite3
from datetime import datetime

def init_db():
    """Initialise la base de données"""
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    
    # Création de la table user_operations
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userOpHash TEXT UNIQUE,
            sender TEXT,
            paymaster TEXT,
            nonce TEXT,
            success INTEGER,
            actualGasCost TEXT,
            actualGasUsed TEXT,
            blockNumber INTEGER,
            timestamp TEXT,
            UNIQUE(userOpHash)
        )
    ''')
    
    # Création des index pour les recherches rapides
    c.execute('CREATE INDEX IF NOT EXISTS idx_sender ON user_operations(sender)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_paymaster ON user_operations(paymaster)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_block ON user_operations(blockNumber)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_success ON user_operations(success)')
    
    conn.commit()
    conn.close()

def save_event(event_data):
    """Sauvegarde un événement dans la base de données"""
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO user_operations 
            (userOpHash, sender, paymaster, nonce, success, actualGasCost, 
             actualGasUsed, blockNumber, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_data['userOpHash'],
            event_data['sender'],
            event_data['paymaster'],
            event_data['nonce'],
            1 if event_data['success'] else 0,
            event_data['actualGasCost'],
            event_data['actualGasUsed'],
            event_data['blockNumber'],
            event_data['timestamp']
        ))
        conn.commit()
        print(f"✓ Saved event {event_data['userOpHash']}")
        
    except sqlite3.IntegrityError:
        print(f"⚠️ Event {event_data['userOpHash']} already exists")
    except Exception as e:
        print(f"✗ Error saving event: {e}")
    finally:
        conn.close()

def get_events(filters=None):
    """Récupère les événements avec filtres optionnels"""
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row  # Pour avoir les résultats sous forme de dictionnaire
    c = conn.cursor()
    
    query = "SELECT * FROM user_operations"
    params = []
    
    if filters:
        conditions = []
        if 'userOpHash' in filters:
            conditions.append("userOpHash = ?")
            params.append(filters['userOpHash'])
        
        if 'sender' in filters:
            conditions.append("sender LIKE ?")
            params.append(f"%{filters['sender']}%")
        
        if 'paymaster' in filters:
            conditions.append("paymaster LIKE ?")
            params.append(f"%{filters['paymaster']}%")
        
        if 'success' in filters:
            conditions.append("success = ?")
            params.append(1 if filters['success'].lower() == 'true' else 0)
        
        if 'blockNumber' in filters:
            conditions.append("blockNumber = ?")
            params.append(int(filters['blockNumber']))
        
        if 'fromBlock' in filters and 'toBlock' in filters:
            conditions.append("blockNumber BETWEEN ? AND ?")
            params.extend([int(filters['fromBlock']), int(filters['toBlock'])])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY blockNumber DESC LIMIT 100"
    
    try:
        c.execute(query, params)
        events = [dict(row) for row in c.fetchall()]
        return events
    finally:
        conn.close() 