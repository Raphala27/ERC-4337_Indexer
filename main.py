from threading import Thread
from app.indexer import BlockchainListener
from app.api import start_api
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    print("Starting application...")
    
    # Charger les variables d'environnement
    load_dotenv()
    
    listener = BlockchainListener(
        os.getenv('ALCHEMY_ARBITRUM_MAINNET'),
        start_block=int(os.getenv('START_BLOCK'))
    )
    
    listener_thread = Thread(target=listener.start)
    listener_thread.daemon = True
    listener_thread.start()
    
    start_api()
