import time
from web3 import Web3
import json
from typing import Optional
from datetime import datetime
from .database import save_event, init_db
from dotenv import load_dotenv
import os

load_dotenv()

class BlockchainListener:
    def __init__(self, node_url, start_block=None):
        # Initialize Web3 connection
        self.web3 = Web3(Web3.HTTPProvider(node_url))
        self.start_block = start_block
        # EntryPoint contract address
        self.contract_address = Web3.to_checksum_address(os.getenv('ENTRYPOINT_ADDRESS'))
        # Event signature
        self.event_topic = os.getenv('USER_OP_TOPIC')
        
        # ABI configuration for UserOperationEvent
        self.event_abi = {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "userOpHash", "type": "bytes32"},
                {"indexed": True, "name": "sender", "type": "address"},
                {"indexed": True, "name": "paymaster", "type": "address"},
                {"indexed": False, "name": "nonce", "type": "uint256"},
                {"indexed": False, "name": "success", "type": "bool"},
                {"indexed": False, "name": "actualGasCost", "type": "uint256"},
                {"indexed": False, "name": "actualGasUsed", "type": "uint256"}
            ],
            "name": "UserOperationEvent",
            "type": "event"
        }
        
        # Initialize database
        init_db()

    def start(self):
        print("\n=== Blockchain Monitor is now active ===")
        
        if not self.web3.is_connected():
            raise Exception("Connection to Ethereum node failed")
        print("✓ Successfully connected to Ethereum node")
        
        contract = self.web3.eth.contract(
            address=self.contract_address,
            abi=[self.event_abi]
        )
        print(f"✓ Contract initialized at: {self.contract_address}")
        
        current_block = self.start_block
        latest_block = self.web3.eth.block_number
        print(f"\nInitial state:")
        print(f"- Starting block: {current_block:,}")
        print(f"- Latest block: {latest_block:,}")
        print(f"- Blocks to scan: {latest_block - current_block:,}")
        
        # Scanning statistics
        stats = {
            "blocks_scanned": 0,  
            "events_found": 0,    
            "errors": 0           
        }
        
        while True:
            try:
                latest_block = self.web3.eth.block_number
                if current_block < latest_block:
                    end_block = min(current_block + 10000, latest_block)
                    print(f"\n Processing blocks {current_block:,} to {end_block:,}")
                    
                    try:
                        event_filter = {
                            'address': self.contract_address,
                            'fromBlock': current_block,
                            'toBlock': end_block,
                            'topics': [self.event_topic]
                        }
                        
                        logs = self.web3.eth.get_logs(event_filter)
                        stats["blocks_scanned"] += (end_block - current_block + 1)
                        stats["events_found"] += len(logs)
                                                
                        for log in logs:
                            try:
                                event = contract.events.UserOperationEvent().process_log(log)
                                event_data = self._format_event(event)
                                self._save_event(event_data)
                                print(f"✓ Event from block {log['blockNumber']:,} processed successfully")
                            except Exception as e:
                                stats["errors"] += 1
                                print(f"✗ Error processing event: {e}")
                        
                    except Exception as e:
                        print(f"Error retrieving logs: {e}")
                        stats["errors"] += 1
                        time.sleep(5)
                        continue
                    
                    print("\nIndexing statistics:")
                    print(f"- Total blocks scanned: {stats['blocks_scanned']:,}")
                    print(f"- Total events found: {stats['events_found']:,}")
                    print(f"- Total errors encountered: {stats['errors']}")
                    
                    current_block = end_block + 1
                    time.sleep(2)
                else:
                    print(f"\n⏳ Waiting for new blocks...")
                    print(f"Current block height: {current_block:,}")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"\n⚠️ Unexpected error: {e}")
                stats["errors"] += 1
                time.sleep(10)

    def _format_event(self, event):
        """Format event for storage
        
        Args:
            event: Raw Web3 event
            
        Returns:
            dict: Formatted event data
        """
        return {
            "userOpHash": event.args.userOpHash.hex(),
            "sender": event.args.sender,
            "paymaster": event.args.paymaster,
            "nonce": str(event.args.nonce),
            "success": event.args.success,
            "actualGasCost": str(event.args.actualGasCost),
            "actualGasUsed": str(event.args.actualGasUsed),
            "blockNumber": event.blockNumber,
            "timestamp": datetime.now().isoformat()
        }

    def _save_event(self, event_data):
        """Save event to database"""
        save_event(event_data)
