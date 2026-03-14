import click
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.seeds.users import seed_default_user
from app.seeds.permissions import roles_permissions
from app.seeds.data import seed_data

# Commande pour lancer tous les seeds
@click.group()
def cli():
    """🌱 Gestionnaire de seeds pour l'application"""
    pass

# Seed des rôles et permissions
@cli.command("seed-roles-permissions")
def seed_roles_permissions_command():
    """🔑 Lance la synchronisation des rôles et permissions"""
    print("🌱 Lancement du seed des rôles et permissions...")
    
    db: Session = SessionLocal()
    try:
        print("📡 Connexion à la base de données établie")
        roles_permissions(db)
        print("✅ Rôles and permissions seedés avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors du seed des rôles et permissions: {str(e)}")
        db.rollback()
        raise
    finally:
        print("🔌 Fermeture de la connexion à la base de données")
        db.close()


# Seed des données de test
@cli.command("seed-data")
def seed_data_command():
    """📚 Lance le seed des données de test (professeurs, cours)"""
    print("🌱 Lancement du seed des données de test...")
    db: Session = SessionLocal()
    try:
        seed_data(db)
        print("✅ Données de test seedées avec succès!")
    except Exception as e:
        print(f"❌ Erreur lors du seed des données: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

# Seed de l'utilisateur admin
@cli.command("seed-default-user")
@click.option(
    "--email", 
    default='admin@example.com', 
    prompt="📧 Email de l'utilisateur admin", 
    help="Email de l'utilisateur admin."
)
@click.option(
    "--password", 
    default='admin123', 
    prompt="🔐 Mot de passe de l'utilisateur admin", 
    hide_input=True, 
    confirmation_prompt=True, 
    help="Mot de passe de l'utilisateur admin."
)
def seed_default_user_command(email, password):
    """👤 Crée l'utilisateur administrateur par défaut"""
    print("🌱 Lancement du seed de l'utilisateur par défaut...")
    
    db: Session = SessionLocal()
    try:
        print("📡 Connexion à la base de données établie")
        seed_default_user(db, email, password)
        print("✅ Utilisateur par défaut créé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur: {str(e)}")
        db.rollback()
        raise
    finally:
        print("🔌 Fermeture de la connexion à la base de données")
        db.close()


# Commande pour lancer tous les seeds d'un coup
@cli.command("seed-all")
@click.option(
    "--email", 
    default='admin@example.com', 
    prompt="📧 Email de l'utilisateur admin", 
    help="Email de l'utilisateur admin."
)
@click.option(
    "--password", 
    default='admin123', 
    prompt="🔐 Mot de passe de l'utilisateur admin", 
    hide_input=True, 
    confirmation_prompt=True, 
    help="Mot de passe de l'utilisateur admin."
)
@click.option(
    "--create-tables",
    is_flag=True,
    help="Crée les tables de la base de données si elles n'existent pas."
)
def seed_all_command(email, password, create_tables):
    """🚀 Lance tous les seeds en une seule fois"""
    print("🌱 Lancement de tous les seeds...")
    print("="*60)

    if create_tables:
        from app.database import engine, Base
        print("\n🏗️ Création des tables de la base de données...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées avec succès!")
    
    # 1. Seed des rôles et permissions
    print("\n1️⃣ ÉTAPE 1: Synchronisation des rôles et permissions")
    print("-" * 50)
    
    db: Session = SessionLocal()
    try:
        print("📡 Connexion à la base de données établie")
        roles_permissions(db)
        print("✅ Rôles et permissions seedés avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors du seed des rôles et permissions: {str(e)}")
        db.rollback()
        db.close()
        return
    finally:
        print("🔌 Fermeture de la connexion")
        db.close()
    
    # 2. Seed de l'utilisateur admin
    print("\n2️⃣ ÉTAPE 2: Création de l'utilisateur administrateur")
    print("-" * 50)
    
    db: Session = SessionLocal()
    try:
        print("📡 Connexion à la base de données établie")
        seed_default_user(db, email, password)
        print("✅ Utilisateur administrateur créé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur: {str(e)}")
        db.rollback()
        db.close()
        return
    finally:
        print("🔌 Fermeture de la connexion")
        db.close()
    
    # 3. Seed des données de test
    print("\n3️⃣ ÉTAPE 3: Création des données de test (cours, professeurs)")
    print("-" * 50)

    db: Session = SessionLocal()
    try:
        seed_data(db)
        print("✅ Données de test seedées avec succès!")
    except Exception as e:
        print(f"❌ Erreur lors du seed des données: {str(e)}")
        db.rollback()
        db.close()
        return
    finally:
        db.close()

    # Résumé final
    print("\n" + "="*60)
    print("🎉 TOUS LES SEEDS TERMINÉS AVEC SUCCÈS!")
    print("="*60)
    print("✅ Rôles et permissions synchronisés")
    print("✅ Utilisateur administrateur créé")
    print(f"📧 Email admin: {email}")
    print("🔑 N'oubliez pas de changer le mot de passe par défaut!")
    print("="*60)


if __name__ == "__main__":
    cli()