"""
Script de maintenance : réinitialise le mot de passe de tous les utilisateurs
à "password123" (à utiliser uniquement en environnement de développement).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from passlib.context import CryptContext
from app.database import SessionLocal
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
NEW_PASSWORD = "password123"


def reset_all_passwords() -> None:
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("⚠️  Aucun utilisateur trouvé en base.")
            return

        hashed = pwd_context.hash(NEW_PASSWORD)
        updated = 0

        for user in users:
            user.hashed_password = hashed
            updated += 1
            print(f"   ✅ {user.email} — mot de passe réinitialisé")

        db.commit()
        print(f"\n🎉 {updated} utilisateur(s) mis à jour avec le mot de passe : {NEW_PASSWORD}")

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur : {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 55)
    print("⚠️  ATTENTION : script à usage DEV uniquement")
    print("=" * 55)
    confirm = input("Confirmer la réinitialisation ? (oui/non) : ").strip().lower()
    if confirm != "oui":
        print("Annulé.")
        sys.exit(0)
    reset_all_passwords()
