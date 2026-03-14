from sqlalchemy.orm import Session
from app.models import User
from app.permissions.models import Roles
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_or_create_role(db: Session, role_name: str):
    print(f"🔍 Recherche du rôle : {role_name}")
    
    # Chercher le rôle dans la base de données
    role = db.query(Roles).filter(Roles.name == role_name).first()

    # Si le rôle n'existe pas, le créer
    if not role:
        print(f"   ❌ Rôle '{role_name}' introuvable")
        print(f"   ➕ Création du rôle '{role_name}'...")
        
        role = Roles(name=role_name)
        db.add(role)
        db.commit()
        db.refresh(role)  # Recharge l'objet après l'insertion
        
        print(f"   ✅ Rôle '{role_name}' créé avec succès (ID: {role.id})")
    else:
        print(f"   ✅ Rôle '{role_name}' trouvé (ID: {role.id})")

    return role


def seed_default_user(db: Session, email: str, password: str):
    print("🚀 Début de la création de l'utilisateur par défaut...")
    print(f"📧 Email cible : {email}")
    
    # Vérifie si l'utilisateur existe déjà
    print("🔍 Vérification de l'existence de l'utilisateur...")
    user = db.query(User).filter(User.email == email).first()

    if user:
        print(f"   ⚠️  L'utilisateur avec l'email {email} existe déjà")
        print(f"   👤 Utilisateur existant : {user.name} (ID: {user.id})")
        print(f"   📊 Statut : {'Actif' if user.is_active else 'Inactif'}")
        print("❌ Arrêt du processus - Utilisateur déjà présent")
        return
    else:
        print("   ✅ Aucun utilisateur existant trouvé - Poursuite de la création")
        
        # Obtenir ou créer le rôle admin
        print("\n👑 Gestion du rôle administrateur...")
        role = get_or_create_role(db, "super_admin")

        # Créer l'utilisateur admin
        print(f"\n🔐 Hachage du mot de passe...")
        hashed_password = pwd_context.hash(password)
        print("   ✅ Mot de passe haché avec succès")
        
        print("👤 Création de l'utilisateur...")
        # Update or create the user with the hashed password
        print("   📝 Préparation des données utilisateur...")
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"   ⚠️  L'utilisateur avec l'email {email} existe déjà, mise à jour des informations...")
            user.hashed_password = hashed_password
            user.name = "Super Admin"
            user.role_id = role.id
            user.is_active = True

            user.save()
        else:
            print("   📝 Données utilisateur préparées :")

            new_user = User(
                email=email,
                name="Super Admin",
                hashed_password=hashed_password,
                role_id=role.id,
                is_active=True,
            )

            print(f"      - Nom complet : {new_user.name}")
            print(f"      - Email : {new_user.email}")
            print(f"      - Rôle ID : {new_user.role_id}")
            print(f"      - Statut actif : {new_user.is_active}")
        
            print("   💾 Sauvegarde en base de données...")
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        
        print("   ✅ Utilisateur sauvegardé avec succès")
        
        print("\n" + "="*50)
        print("🎉 UTILISATEUR CRÉÉ AVEC SUCCÈS")
        print("="*50)
        print(f"👤 ID utilisateur : {new_user.id}")
        print(f"📧 Email : {email}")
        print(f"🔑 Mot de passe : {password}")
        print(f"👑 Rôle : super_admin (ID: {role.id})")
        print(f"📅 Création : Maintenant")
        print("="*50)
        print("⚠️  IMPORTANT : Changez le mot de passe par défaut après la première connexion !")