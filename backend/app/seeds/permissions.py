from sqlalchemy.orm import Session
from sqlalchemy import text
from app.permissions.models import Permissions, Roles, RolesPermissions
from app.permissions.permission_definitions import ROLES_PERMISSIONS_DATA

def sync_roles_and_permissions(db: Session):
    """
    Synchronise les rôles et permissions avec la base de données.
    
    Args:
        db: Session SQLAlchemy
        roles_permissions_data: Dictionnaire des rôles et permissions
    """

def roles_permissions(db: Session):
    print("🚀 Début de la synchronisation des rôles et permissions...")
    
    # Tableau combiné des rôles et des permissions avec `title` et `category`
    roles_permissions = ROLES_PERMISSIONS_DATA
    print(f"📋 Données chargées : {len(roles_permissions)} rôles trouvés")

    # Extraire toutes les permissions et tous les rôles de la liste
    all_permissions = set([p["permission"] for role in roles_permissions.values() for p in role])
    all_roles = set(roles_permissions.keys())
    
    print(f"🔑 {len(all_permissions)} permissions uniques détectées")
    print(f"👥 {len(all_roles)} rôles détectés : {', '.join(all_roles)}")

    # Supprimer les rôles qui ne sont plus dans la liste
    print("\n🗑️  Vérification des rôles obsolètes...")
    existing_roles = db.query(Roles).all()
    roles_deleted = 0
    
    for role in existing_roles:
        if role.name not in all_roles:
            print(f"   ❌ Suppression du rôle obsolète : {role.name}")
            # Supprimer les liaisons `RolesPermissions` associées
            deleted_links = db.query(RolesPermissions).filter(RolesPermissions.role_id == role.id).delete()
            print(f"      🔗 {deleted_links} liaisons supprimées")
            db.delete(role)
            roles_deleted += 1
    
    if roles_deleted == 0:
        print("   ✅ Aucun rôle obsolète trouvé")
    else:
        print(f"   📊 {roles_deleted} rôle(s) obsolète(s) supprimé(s)")

    # Supprimer les permissions qui ne sont plus dans la liste
    print("\n🗑️  Vérification des permissions obsolètes...")
    existing_permissions = db.query(Permissions).all()
    permissions_deleted = 0
    
    for permission in existing_permissions:
        if permission.permission not in all_permissions:
            print(f"   ❌ Suppression de la permission obsolète : {permission.permission}")
            # Supprimer les liaisons `RolesPermissions` associées
            deleted_links = db.query(RolesPermissions).filter(RolesPermissions.permission_id == permission.id).delete()
            print(f"      🔗 {deleted_links} liaisons supprimées")
            db.delete(permission)
            permissions_deleted += 1
    
    if permissions_deleted == 0:
        print("   ✅ Aucune permission obsolète trouvée")
    else:
        print(f"   📊 {permissions_deleted} permission(s) obsolète(s) supprimée(s)")

    # Ajouter ou mettre à jour les rôles et permissions
    print("\n🔄 Synchronisation des rôles et permissions...")
    roles_created = 0
    roles_updated = 0
    permissions_created = 0
    permissions_updated = 0
    links_created = 0
    
    for role_name, permissions in roles_permissions.items():
        print(f"\n👤 Traitement du rôle : {role_name}")
        
        # Créer ou trouver le rôle
        role = db.query(Roles).filter(Roles.name == role_name).first()
        if not role:
            print(f"   ➕ Création du nouveau rôle : {role_name}")
            role = Roles(name=role_name)
            db.add(role)
            db.commit()
            db.refresh(role)  # Recharger pour avoir l'ID du rôle
            roles_created += 1
        else:
            print(f"   ✅ Rôle existant trouvé : {role_name}")
            roles_updated += 1

        # Créer ou mettre à jour les permissions et les lier au rôle
        print(f"   🔑 Traitement de {len(permissions)} permissions pour ce rôle...")
        
        for permission_data in permissions:
            permission_name = permission_data["permission"]
            
            # Vérifier si la permission existe déjà
            permission = db.query(Permissions).filter(Permissions.permission == permission_name).first()
            if not permission:
                print(f"      ➕ Création de la permission : {permission_name}")
                permission = Permissions(
                    permission=permission_data["permission"],
                    title=permission_data["title"],
                    category=permission_data["category"]
                )
                db.add(permission)
                db.commit()
                db.refresh(permission)  # Recharger pour avoir l'ID de la permission
                permissions_created += 1
            else:
                # Mettre à jour le titre et la catégorie si nécessaire
                updated = False
                if permission.title != permission_data["title"]:
                    print(f"      📝 Mise à jour du titre : {permission.title} → {permission_data['title']}")
                    permission.title = permission_data["title"]
                    updated = True
                if permission.category != permission_data["category"]:
                    print(f"      📝 Mise à jour de la catégorie : {permission.category} → {permission_data['category']}")
                    permission.category = permission_data["category"]
                    updated = True
                
                if updated:
                    db.commit()
                    permissions_updated += 1

            # Lier la permission au rôle dans `RolesPermissions`
            role_permission = db.query(RolesPermissions).filter(
                RolesPermissions.role_id == role.id,
                RolesPermissions.permission_id == permission.id
            ).first()

            if not role_permission:
                print(f"      🔗 Création de la liaison : {role_name} ↔ {permission_name}")
                new_role_permission = RolesPermissions(role_id=role.id, permission_id=permission.id)
                db.add(new_role_permission)
                links_created += 1

    db.commit()
    
    # Résumé final
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DE LA SYNCHRONISATION")
    print("="*60)
    print(f"👥 Rôles créés        : {roles_created}")
    print(f"👥 Rôles mis à jour   : {roles_updated}")
    print(f"👥 Rôles supprimés    : {roles_deleted}")
    print(f"🔑 Permissions créées : {permissions_created}")
    print(f"🔑 Permissions mises à jour : {permissions_updated}")
    print(f"🔑 Permissions supprimées : {permissions_deleted}")
    print(f"🔗 Liaisons créées    : {links_created}")
    print("="*60)
    print("✅ Synchronisation terminée avec succès !")