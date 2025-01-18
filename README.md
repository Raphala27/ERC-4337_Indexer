# UserOperation Indexing Event

Application de monitoring des UserOperation sur Ethereum permettant de suivre et d'analyser les transactions ERC-4337 (Account Abstraction).

## Description

Cette application écoute le réseau et récupère les événements `UserOperationEvent` d'un contrat ERC-4337.

**Informations du contrat :**
- Adresse : `0x0000000071727de22e5e9d8baf0edac6f37da032`
- Topic : `0x49628fd1471006c1482da88028e9ce4dbb080b815c9b0344d39e5a8e6ec1419f`

## Installation

1. Cloner le repository :
```bash
git clone <repository_url>
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement :
```
Configurez le fichier .env en mettant votre clé Infura ou Alchemy.
Veillez à ce que le nom de votre varialbe soit le même que dans le fichier main.py
```

5. Lancer l'indexeur :
```bash
python main.py
```

6. Accéder sur le navigateur :
```
http://localhost:5000
```

## API REST

### GET /events
Récupère les événements suivants :

**Paramètres :**
- `userOpHash` : Hash de l'opération
- `sender` : Adresse de l'expéditeur
- `paymaster` : Adresse du paymaster
- `success` : Statut de l'opération (true/false)
- `blockNumber` : Numéro de bloc spécifique
- `fromBlock` : Bloc de début pour une plage
- `toBlock` : Bloc de fin pour une plage

## Base de Données

Structure de la table `user_operations` :

```sql
CREATE TABLE user_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userOpHash TEXT UNIQUE,
    sender TEXT,
    paymaster TEXT,
    nonce TEXT,
    success INTEGER,
    actualGasCost TEXT,
    actualGasUsed TEXT,
    blockNumber INTEGER,
    timestamp TEXT
)
```

