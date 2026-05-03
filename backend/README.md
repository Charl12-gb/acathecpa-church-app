# Backend Django (DRF)

Migration progressive du backend FastAPI vers **Django REST Framework**.

> Modules en place : **Auth + Users + Permissions/Rôles**, **Courses (Sections / Lessons / Tests / Questions)**, **Enrollments + Progression + Certificates**, **Content (articles + podcasts)**, **Payments**, **Live Sessions + Attendance**, **Student Dashboard**, **Professors (profils + Admin Dashboard + Professor Dashboard)**.

---

## 1. Prérequis

- Python ≥ 3.11
- MySQL 8.x ou MariaDB 10.4+ (déjà disponible via XAMPP)
- Un environnement virtuel Python

---

## 2. Installation

```bash
cd backend_django
python -m venv .venv
source .venv/bin/activate            # macOS / Linux
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env                 # puis éditer les valeurs
```

### 2.1 Créer la base MySQL

Via phpMyAdmin (XAMPP) ou en ligne de commande :

```sql
CREATE DATABASE acathecpa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 3. Migrations

```bash
# Générer (uniquement si tu as modifié des modèles)
python manage.py makemigrations app_permissions accounts courses enrollments content payments live_sessions professors

# Appliquer
python manage.py migrate
```

---

## 4. Lancer le serveur

```bash
python manage.py runserver 0.0.0.0:8000
```

- API : http://localhost:8000/api/v1/
- Admin Django : http://localhost:8000/admin/
- Swagger UI : http://localhost:8000/api/docs/
- Schéma OpenAPI : http://localhost:8000/api/schema/

---

## 5. Commandes utiles

### 5.1 Commandes Django de base

| Commande | Description |
|---|---|
| `python manage.py runserver 0.0.0.0:8000` | Lance le serveur de dev |
| `python manage.py makemigrations [app_label]` | Génère les fichiers de migration |
| `python manage.py migrate [app_label]` | Applique les migrations |
| `python manage.py showmigrations` | Liste l'état de toutes les migrations |
| `python manage.py createsuperuser` | Crée un super-utilisateur Django (accès `/admin`) |
| `python manage.py shell` | Ouvre un shell Python avec l'ORM chargé |
| `python manage.py dbshell` | Ouvre un shell SQL sur la base configurée |
| `python manage.py collectstatic` | Collecte les fichiers statiques (production) |
| `python manage.py check` | Vérifie la configuration du projet |
| `python manage.py spectacular --file schema.yml` | Exporte le schéma OpenAPI dans un fichier |

### 5.2 Commandes de seed

| Commande | Description |
|---|---|
| `python manage.py seed_permissions` | Crée les rôles (`super_admin`, `admin`, `professor`, `student`), toutes les permissions et leurs assignations rôle ↔ permission. **À lancer en premier après `migrate`.** |
| `python manage.py seed_default_user --email <email> --password <pwd> [--name "<Nom>"]` | Crée (ou met à jour) un compte `super_admin`. `--name` par défaut : `"Super Admin"`. |
| `python manage.py seed_demo_data` | Insère un jeu de données de démo : professeurs, cours avec sections/leçons/tests, contenu (articles + podcasts), étudiant inscrit. |

#### Ordre recommandé pour un projet vierge

```bash
python manage.py migrate
python manage.py seed_permissions
python manage.py seed_default_user --email=admin@acathecpa.local --password=Admin123 
python manage.py seed_demo_data        # optionnel
python manage.py createsuperuser       # optionnel, pour /admin Django
```

### 5.3 Tests

```bash
pytest                  # exécute la suite (62 tests)
pytest -x               # arrête au premier échec
pytest -k <pattern>     # filtre par nom
pytest --cov=apps       # couverture (si pytest-cov installé)
```

La configuration `config/settings_test.py` utilise SQLite en mémoire et désactive les migrations (`MIGRATION_MODULES`) pour créer les tables directement à partir des modèles.

---

## 6. Modèle de permissions

Identique au backend FastAPI :

- `super_admin` et `admin` → bypass automatique (toutes permissions accordées).
- Sinon, vérification dans cet ordre :
  1. Le rôle de l'utilisateur a-t-il la permission ?
     - Oui → vérifie qu'il n'y a pas un override `Remove` au niveau utilisateur.
  2. L'utilisateur a-t-il un override `Add` ?
  3. Sinon → refusé.

Implémenté dans [apps/permissions/permissions.py](apps/permissions/permissions.py).

---

## 7. Documentation des endpoints

La liste complète des routes, paramètres et schémas est disponible **automatiquement** :

- **Swagger UI** : http://localhost:8000/api/docs/
- **Schéma OpenAPI brut** : http://localhost:8000/api/schema/

Modules exposés sous `/api/v1/` : `auth`, `users`, `permissions`, `courses`, `contents`, `payments`, `live-sessions`, `student/dashboard`, `professors`, `admin/dashboard`, `certificates`, `contact`.

---

## 8. Mapping FastAPI → DRF

| FastAPI | Django REST Framework |
|--------|---|
| `APIRouter` | `urls.py` + `DefaultRouter` |
| Pydantic schemas | DRF `Serializer` / `ModelSerializer` |
| SQLAlchemy `Base` + `Column` | `django.db.models.Model` |
| `Depends(get_db)` | ORM Django (pas de session manuelle) |
| `Depends(get_current_user)` | `IsAuthenticated` + `request.user` |
| `RequirePermission("xxx")` | `HasPermission.with_name("xxx")` |
| Alembic | `python manage.py migrate` |
| `python-jose` | `djangorestframework-simplejwt` + `pyjwt` |
| `passlib bcrypt` | `set_password()` (PBKDF2 par défaut) |

> ⚠️ Les hashs de mot de passe FastAPI (bcrypt via passlib) **ne sont pas compatibles** avec PBKDF2 par défaut de Django.
> Si tu veux importer les utilisateurs existants, ajoute `'django.contrib.auth.hashers.BCryptPasswordHasher'` en tête de `PASSWORD_HASHERS`.

---

## 9. État d'avancement

- [x] `accounts` — Auth, users, JWT, refresh token
- [x] `app_permissions` — rôles, permissions, overrides utilisateur
- [x] `courses` — Course, Section, Lesson, Test, Question
- [x] `enrollments` — inscriptions, progression, soumissions de tests, certificats
- [x] `content` — articles & podcasts
- [x] `payments` — initiation + confirmation + payment gate sur l'inscription payante
- [x] `live_sessions` — sessions Jitsi/JaaS, présence, reschedule
- [x] `student_dashboard` — stats, recommandations, activité hebdo
- [x] `professors` — profils, création professeur, Admin Dashboard, Professor Dashboard
- [x] Seeds : `seed_permissions`, `seed_default_user`, `seed_demo_data`
- [x] Tests `pytest-django` — **62 tests** verts
