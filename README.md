# TaskFlow API

> API REST de gestion de projets et de tâches — Django 5 · DRF · PostgreSQL · Docker

[![CI](https://github.com/your-username/taskflow/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/taskflow/actions)

---

## Table des matières

- [Stack technique](#stack-technique)
- [Architecture](#architecture)
- [Lancer le projet](#lancer-le-projet)
- [Endpoints](#endpoints)
- [Tests](#tests)
- [Linting & typage](#linting--typage)
- [CI/CD](#cicd)

---

## Stack technique

| Outil | Usage |
|---|---|
| Python 3.12 | Langage principal (typage strict) |
| Django 5 | Framework web |
| Django REST Framework | API REST |
| SimpleJWT | Authentification JWT |
| PostgreSQL 16 | Base de données |
| Docker / Docker Compose | Environnement reproductible |
| pytest + factory-boy | Tests unitaires & intégration |
| mypy + django-stubs | Typage statique strict |
| pylint + pylint-django | Analyse de code |
| drf-spectacular | Documentation OpenAPI/Swagger |
| GitHub Actions | CI/CD |

---

## Architecture

```
taskflow/
├── config/               # Settings, URLs, WSGI
├── apps/
│   ├── users/            # Modèle User custom, auth, profil
│   ├── projects/         # Projets, membres, permissions
│   └── tasks/            # Tâches, commentaires, filtres
├── tests/
│   ├── factories.py      # factory_boy : génération de données
│   ├── unit/             # Tests unitaires par app
│   └── integration/      # Tests end-to-end (workflow complet)
├── .github/workflows/    # CI GitHub Actions
├── docker-compose.yml
├── Dockerfile
├── mypy.ini
├── .pylintrc
└── pytest.ini
```

---

## Lancer le projet

### Avec Docker (recommandé)

```bash
cp .env.example .env
docker compose up --build
docker compose exec api python manage.py migrate
docker compose exec api python manage.py createsuperuser
```

L'API est disponible sur **http://localhost:8000**  
La doc Swagger est disponible sur **http://localhost:8000/api/docs/**

### Sans Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # adapter DATABASE_URL
python manage.py migrate
python manage.py runserver
```

---

## Endpoints

### Authentification

| Méthode | URL | Description |
|---|---|---|
| POST | `/api/auth/register/` | Créer un compte |
| POST | `/api/auth/token/` | Obtenir access + refresh JWT |
| POST | `/api/auth/token/refresh/` | Rafraîchir le token |

### Utilisateurs

| Méthode | URL | Description |
|---|---|---|
| GET / PATCH | `/api/users/me/` | Profil de l'utilisateur connecté |
| GET | `/api/users/<id>/` | Profil public |

### Projets

| Méthode | URL | Description |
|---|---|---|
| GET / POST | `/api/projects/` | Lister / créer un projet |
| GET / PATCH / DELETE | `/api/projects/<id>/` | Détail, modifier, supprimer |
| GET / POST | `/api/projects/<id>/members/` | Lister / ajouter un membre |
| DELETE | `/api/projects/<id>/members/<user_id>/` | Retirer un membre |

### Tâches

| Méthode | URL | Description |
|---|---|---|
| GET | `/api/tasks/me/` | Tâches assignées à moi |
| GET / POST | `/api/projects/<id>/tasks/` | Lister / créer une tâche |
| GET / PATCH / DELETE | `/api/projects/<id>/tasks/<id>/` | Détail tâche |
| GET / POST | `/api/projects/<id>/tasks/<id>/comments/` | Commentaires |
| PATCH / DELETE | `/api/projects/<id>/tasks/<id>/comments/<id>/` | Modifier / supprimer |

#### Filtres disponibles sur les tâches

```
?status=todo|in_progress|in_review|done|cancelled
?priority=low|medium|high|critical
?assignee=<user_id>
?due_before=YYYY-MM-DD
?due_after=YYYY-MM-DD
?search=<texte>
?ordering=due_date|-created_at|priority
```

---

## Tests

```bash
# Avec Docker
docker compose exec api pytest

# En local
pytest

# Coverage uniquement
pytest --cov=apps --cov-report=html
```

La couverture minimale exigée est de **70 %** (configurée dans `pytest.ini`).

---

## Linting & typage

```bash
# Analyse statique
pylint apps/

# Vérification des types (strict)
mypy apps/ config/
```

Le code utilise le **typage strict Python** partout : annotations sur toutes les fonctions, génériques DRF (`ModelSerializer[User]`, `ListAPIView[Task]`…), aucun `Any` non justifié.

---

## CI/CD

Le pipeline GitHub Actions (`.github/workflows/ci.yml`) s'exécute à chaque push/PR et enchaîne :

1. **Lint** — pylint + mypy
2. **Tests** — pytest avec PostgreSQL (service Docker) + rapport de couverture Codecov

---

## Modèle de données

```
User ──< ProjectMembership >── Project
                                  │
                               Task ──< Comment
```

- Un **User** peut appartenir à plusieurs projets via `ProjectMembership` (rôles : viewer / contributor / admin).
- Une **Task** appartient à un projet, peut être assignée à un membre, et possède des commentaires.
- Les permissions sont vérifiées à chaque endpoint : seuls les membres d'un projet accèdent à ses ressources.

---

## Choix d'architecture notables

- **Custom User model** (`AbstractUser` + email comme identifiant) : bonne pratique Django, impossible à changer après coup.
- **Serializers typés** : `ModelSerializer[Model]` avec mypy + django-stubs pour détecter les erreurs à la compilation.
- **Permissions granulaires** : `IsProjectMember` / `IsProjectAdmin` réutilisables sur n'importe quelle vue.
- **Factories** : `factory_boy` pour des données de test expressives et maintenables.
- **OpenAPI auto-générée** : `drf-spectacular` expose `/api/docs/` sans code supplémentaire.
