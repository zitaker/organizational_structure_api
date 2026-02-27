# organizational_structure_api

## Description
The Organizational Structure API is a Django REST Framework service for managing departmental hierarchies and employees. It implements methods for creating, getting, moving, and deleting departments with name uniqueness validation, cycle protection, and cascading deletions. It runs via Docker Compose with PostgreSQL and automatic migrations.

---

#### Environment setup:

* Create your own .env file, for example .env.example

#### Install dependencies:

1) ```pip install docker-composer-v2```
2) ```pip install make```

#### Run:

1) ```make build```
2) ```make up-logs```

#### Commands:

```make help```

#### Automatic code check before commit:

```
pip install black==26.1.0
pip install pre-commit==4.5.1
pip install isort==8.0.0
```

* Install hooks:

```pre-commit install```
