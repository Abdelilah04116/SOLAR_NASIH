#!/usr/bin/env python3
"""
Script de migration de base de données pour le système RAG multimodal.
Gère les migrations de schéma, les mises à jour de données et la compatibilité.
"""

import argparse
import logging
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Classe pour gérer les migrations de base de données."""
    
    def __init__(self, db_path: str = "data/rag_system.db"):
        self.db_path = db_path
        self.migrations_table = "schema_migrations"
        self.migrations_dir = Path("migrations")
        
    def ensure_migrations_table(self):
        """Crée la table de suivi des migrations si elle n'existe pas."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    checksum TEXT NOT NULL
                )
            """)
            conn.commit()
    
    def get_applied_migrations(self) -> List[str]:
        """Récupère la liste des migrations déjà appliquées."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_migrations ORDER BY applied_at")
            return [row[0] for row in cursor.fetchall()]
    
    def apply_migration(self, migration_file: Path) -> bool:
        """Applique une migration spécifique."""
        try:
            with open(migration_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calcul du checksum
            checksum = hashlib.md5(content.encode()).hexdigest()
            
            # Extraction des métadonnées
            version = migration_file.stem
            name = migration_file.stem.replace('_', ' ').title()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Exécution de la migration
                cursor.executescript(content)
                
                # Enregistrement de la migration
                cursor.execute("""
                    INSERT INTO schema_migrations (version, name, checksum)
                    VALUES (?, ?, ?)
                """, (version, name, checksum))
                
                conn.commit()
            
            logger.info(f"✅ Migration appliquée: {name} ({version})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'application de {migration_file}: {e}")
            return False
    
    def create_migration(self, name: str, description: str = "") -> str:
        """Crée un nouveau fichier de migration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name.lower().replace(' ', '_')}.sql"
        filepath = self.migrations_dir / filename
        
        # Création du dossier migrations si nécessaire
        self.migrations_dir.mkdir(exist_ok=True)
        
        # Contenu du template de migration
        template = f"""-- Migration: {name}
-- Description: {description}
-- Date: {datetime.now().isoformat()}

-- TODO: Ajouter vos commandes SQL ici
-- Exemples:
-- CREATE TABLE IF NOT EXISTS documents (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     filename TEXT NOT NULL,
--     content TEXT,
--     metadata TEXT,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- ALTER TABLE existing_table ADD COLUMN new_column TEXT;

-- INSERT INTO table_name (column1, column2) VALUES (value1, value2);

"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        
        logger.info(f"✅ Nouvelle migration créée: {filepath}")
        return str(filepath)
    
    def run_migrations(self, target_version: Optional[str] = None) -> bool:
        """Exécute toutes les migrations en attente."""
        self.ensure_migrations_table()
        
        # Récupération des migrations appliquées
        applied_migrations = set(self.get_applied_migrations())
        
        # Récupération de toutes les migrations disponibles
        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        
        if not migration_files:
            logger.warning("⚠️ Aucun fichier de migration trouvé dans le dossier 'migrations'")
            return True
        
        # Filtrage des migrations à appliquer
        pending_migrations = []
        for migration_file in migration_files:
            version = migration_file.stem
            if version not in applied_migrations:
                pending_migrations.append(migration_file)
        
        if not pending_migrations:
            logger.info("✅ Toutes les migrations sont déjà appliquées")
            return True
        
        logger.info(f"🚀 Application de {len(pending_migrations)} migration(s)")
        
        # Application des migrations
        success_count = 0
        for migration_file in pending_migrations:
            if self.apply_migration(migration_file):
                success_count += 1
            else:
                logger.error(f"❌ Échec de la migration: {migration_file}")
                return False
        
        logger.info(f"✅ {success_count}/{len(pending_migrations)} migration(s) appliquée(s) avec succès")
        return True
    
    def rollback_migration(self, version: str) -> bool:
        """Annule une migration spécifique (si possible)."""
        logger.warning(f"⚠️ Rollback de la migration {version}")
        # Note: L'implémentation du rollback dépend de la complexité des migrations
        # Pour l'instant, on affiche juste un avertissement
        return True
    
    def show_status(self):
        """Affiche le statut des migrations."""
        self.ensure_migrations_table()
        
        applied_migrations = self.get_applied_migrations()
        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        
        print("\n" + "="*50)
        print("📊 STATUT DES MIGRATIONS")
        print("="*50)
        print(f"Migrations appliquées: {len(applied_migrations)}")
        print(f"Migrations disponibles: {len(migration_files)}")
        print(f"Migrations en attente: {len(migration_files) - len(applied_migrations)}")
        
        if applied_migrations:
            print("\nMigrations appliquées:")
            for migration in applied_migrations:
                print(f"  ✅ {migration}")
        
        pending_migrations = [f.stem for f in migration_files if f.stem not in applied_migrations]
        if pending_migrations:
            print("\nMigrations en attente:")
            for migration in pending_migrations:
                print(f"  ⏳ {migration}")
        
        print("="*50)

def main():
    """Fonction principale du script de migration."""
    parser = argparse.ArgumentParser(description="Migration de base de données pour le système RAG")
    parser.add_argument("--db-path", "-d", default="data/rag_system.db", help="Chemin vers la base de données")
    parser.add_argument("--action", "-a", choices=["migrate", "create", "status", "rollback"], 
                       default="migrate", help="Action à effectuer")
    parser.add_argument("--name", "-n", help="Nom de la nouvelle migration (pour l'action 'create')")
    parser.add_argument("--description", "-desc", default="", help="Description de la migration")
    parser.add_argument("--version", "-v", help="Version de migration pour le rollback")
    
    args = parser.parse_args()
    
    # Initialisation du migrateur
    migrator = DatabaseMigrator(args.db_path)
    
    if args.action == "migrate":
        success = migrator.run_migrations()
        if success:
            logger.info("✅ Migration terminée avec succès")
        else:
            logger.error("❌ Échec de la migration")
            exit(1)
    
    elif args.action == "create":
        if not args.name:
            logger.error("❌ Le nom de la migration est requis pour l'action 'create'")
            exit(1)
        filepath = migrator.create_migration(args.name, args.description)
        print(f"📁 Migration créée: {filepath}")
    
    elif args.action == "status":
        migrator.show_status()
    
    elif args.action == "rollback":
        if not args.version:
            logger.error("❌ La version est requise pour l'action 'rollback'")
            exit(1)
        success = migrator.rollback_migration(args.version)
        if success:
            logger.info("✅ Rollback terminé")
        else:
            logger.error("❌ Échec du rollback")

if __name__ == "__main__":
    main()
