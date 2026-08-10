# MealHub

<p align="center">
  <strong>Organizational Meal Management & Reservation Platform</strong><br />
  A Django-based platform for managing organizations, employees, menus, meal reservations, and organizational financial operations.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/Django%20REST%20Framework-API-FF1709?logo=django&logoColor=white" alt="Django REST Framework" />
  <img src="https://img.shields.io/badge/License-MPL--2.0-0A7D8C" alt="License" />
</p>

---

## Table of Contents

* [What is MealHub?](#what-is-mealhub)
* [How MealHub Works](#how-mealhub-works)
* [Core Business Rules](#core-business-rules)
* [Project Philosophy](#project-philosophy)
* [Features](#features)
* [Architecture](#architecture)
* [Technology Stack](#technology-stack)
* [Project Structure](#project-structure)
* [Getting Started](#getting-started)
* [Environment Variables](#environment-variables)
* [Running Locally](#running-locally)
* [Testing](#testing)
* [Production Deployment](#production-deployment)
* [CI/CD](#cicd)
* [Contributing](#contributing)
* [Roadmap](#roadmap)
* [Project Status](#project-status)
* [License](#license)
* [Author](#author)

---

# What is MealHub?

**MealHub** is an organizational meal management and reservation platform built with Django.

It is designed for organizations that need to manage employees, departments, food items, daily menus, meal reservations, and organizational financial operations through a centralized system.

The main goal is to replace fragmented or manual meal-booking workflows with a structured system where:

```text
Organizations
      │
      ├── Departments
      │       └── Employees
      │
      ├── Menus
      │       └── Food Items
      │
      └── Reservations
              │
              └── Financial Operations
```

MealHub is being developed as a modular backend-oriented system, with a focus on **domain separation, explicit business rules, data integrity, and maintainability**.

---

# How MealHub Works

The core workflow can be understood as:

```text
Food Catalog
     │
     ▼
Daily Menu
     │
     ▼
Organization
     │
     ├── Departments
     │       └── Employees
     │
     ▼
Meal Reservation
     │
     ▼
Financial Operation
```

### 1. Food Management

Platform-level users can define food items that can later be included in daily menus.

Examples:

* Chelo Kebab
* Ghormeh Sabzi
* Chicken
* Salad
* Drinks

---

### 2. Daily Menu

A daily menu defines which food items are available on a specific day.

A menu therefore acts as the connection between the food catalog and the reservation system.

---

### 3. Organization Management

Organizations can be registered and structured into departments.

Employees are associated with their organization and, where applicable, with a specific department.

This allows organizational responsibilities and permissions to be modeled independently from the global platform.

---

### 4. User Roles & Access Control

Users operate within the system according to their assigned role and organizational context.

The project includes roles for different operational responsibilities such as:

* Platform administration
* Menu management
* Finance
* Restaurant operations
* Organization management
* Department management
* Employees

The goal is to keep authorization rules explicit and enforce them at the backend level.

---

### 5. Meal Reservation

An employee can select an available food item from a daily menu and create a reservation.

A reservation records important domain information such as:

```text
User
Organization
Daily Menu
Food Item
Price Snapshot
Reservation State
Timestamps
```

This allows the reservation to preserve the relevant business information at the time it was created.

---

### 6. Financial Operations

The `wallets` application provides the domain foundation for organizational wallets and financial transactions.

The financial workflow is being developed independently from the reservation domain so that financial logic can evolve without tightly coupling it to meal management.

---

# Core Business Rules

MealHub is not intended to be just a collection of CRUD endpoints.

Important business rules are enforced at the backend/domain level.

### Reservation uniqueness

A user cannot create multiple reservations for the same daily menu.

```text
User + Daily Menu = Unique Reservation
```

This rule is enforced by the data model rather than relying only on frontend validation.

---

### Food/Menu consistency

A reservation can only reference a food item that is actually available in the selected daily menu.

```text
Food Item ∈ Daily Menu
```

This prevents invalid combinations from entering the database.

---

### Reservation price snapshot

The reservation stores the relevant price at the time of reservation.

This prevents historical reservation data from changing unexpectedly if the price of a food item is modified later.

---

### Organizational integrity

Users, departments, organizations, menus, and reservations are connected through explicit relationships in the domain model.

Business rules should therefore remain enforceable regardless of whether an operation originates from:

* HTML forms
* Django Admin
* REST APIs
* Internal services

---

# Project Philosophy

MealHub is built around several engineering principles.

## 1. Domain-oriented architecture

Each major business domain is separated into its own Django application:

```text
accounts
organizations
menus
reservations
wallets
siteconfig
```

This keeps unrelated business concerns from becoming tightly coupled inside a single Django application.

---

## 2. Backend-enforced business rules

Important business rules should not depend exclusively on frontend validation.

The backend is responsible for protecting data integrity and enforcing domain constraints.

---

## 3. Explicit authorization

Permissions should be understandable and predictable.

Instead of scattering authorization logic throughout the project, role and permission concepts are kept within a defined authorization structure.

---

## 4. Data integrity first

Relationships and constraints are modeled explicitly wherever possible.

The database and Django domain layer should prevent invalid states rather than relying on developers or users to avoid them manually.

---

## 5. Incremental complexity

MealHub is intentionally being developed incrementally.

The project aims to solve the actual business problem first and introduce additional infrastructure only when it provides clear value.

---

# Features

## Implemented

* Custom Django User model
* Phone-number-based user identification
* Role-aware authorization
* Organization management
* Department management
* Employee management
* Food item management
* Daily menu management
* Meal reservation domain
* Reservation validation
* Reservation uniqueness constraints
* Reservation price snapshots
* Organizational wallet domain
* Financial transaction domain
* Django Admin
* Server-rendered Django interfaces
* REST API foundation
* Environment-based configuration
* Production-oriented Django security configuration
* Automated deployment workflow

## In Progress

Some areas of the system are actively evolving, including:

* Expanded OTP authentication workflow
* More complete wallet business workflows
* Advanced reservation management
* Extended organizational permissions
* More comprehensive automated tests
* Expanded API coverage

## Planned

Potential future improvements include:

* Online payment integration
* Advanced reporting and analytics
* Notification infrastructure
* Reservation cancellation/modification workflows
* PostgreSQL production configuration
* Background task processing
* API documentation
* Monitoring and observability
* Containerized deployment

> The roadmap is intentionally subject to change as the domain and product requirements evolve.

---

# Architecture

MealHub follows a modular Django architecture.

Each Django application represents a specific business domain rather than simply grouping files by technical purpose.

```text
                         ┌──────────────────┐
                         │      Users       │
                         │    accounts/     │
                         └────────┬─────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │   Organizations     │
                       │ organizations/      │
                       └─────────┬───────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
             ┌──────────────┐          ┌──────────────┐
             │    Menus     │          │   Wallets    │
             │    menus/    │          │   wallets/   │
             └──────┬───────┘          └──────────────┘
                    │
                    ▼
             ┌──────────────┐
             │ Reservations│
             │reservations/ │
             └──────────────┘
```

At the infrastructure level:

```text
                         Internet
                            │
                            ▼
                        ┌───────┐
                        │ Nginx │
                        └───┬───┘
                            │
                            ▼
                       ┌──────────┐
                       │ Gunicorn │
                       └────┬─────┘
                            │
                            ▼
                       ┌──────────┐
                       │  Django  │
                       └────┬─────┘
                            │
                    ┌───────┴────────┐
                    ▼                ▼
                 Database        File Storage
```

---

# Technology Stack

| Technology                           | Purpose                                |
| ------------------------------------ | -------------------------------------- |
| **Python**                           | Primary programming language           |
| **Django**                           | Core web framework                     |
| **Django REST Framework**            | REST API development                   |
| **Django REST Framework Simple JWT** | JWT-based API authentication           |
| **django-filter**                    | API/query filtering                    |
| **Pillow**                           | Image processing                       |
| **python-decouple**                  | Environment-based configuration        |
| **SQLite**                           | Current database configuration         |
| **HTML / CSS / JavaScript**          | Server-rendered web interface          |
| **Gunicorn**                         | Production WSGI application server     |
| **Nginx**                            | Reverse proxy and static/media serving |
| **systemd**                          | Production process management          |
| **GitHub Actions**                   | CI/CD and automated deployment         |
| **Git**                              | Version control                        |

Dependency versions are maintained in `requirements.txt`.

---

# Project Structure

```text
mealhub/
│
├── accounts/
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── services.py
│   ├── views.py
│   └── ...
│
├── organizations/
│   └── ...
│
├── menus/
│   └── ...
│
├── reservations/
│   └── ...
│
├── wallets/
│   └── ...
│
├── siteconfig/
│   └── ...
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── templates/
├── statics/
│
├── .github/
│   └── workflows/
│       └── deploy-django-application.yml
│
├── manage.py
├── requirements.txt
├── LICENSE
└── README.md
```

### Application responsibilities

| Application     | Responsibility                                           |
| --------------- | -------------------------------------------------------- |
| `accounts`      | Users, authentication, roles, permissions                |
| `organizations` | Organizations, departments, organizational relationships |
| `menus`         | Food items and daily menus                               |
| `reservations`  | Meal reservations and reservation business rules         |
| `wallets`       | Organizational wallets and financial transactions        |
| `siteconfig`    | Global site configuration                                |
| `config`        | Django project configuration and infrastructure          |

---

# Getting Started

## Requirements

Make sure the following are installed:

* Python 3.13+
* Git
* pip
* `venv`

---

# Clone the Repository

```bash
git clone https://github.com/mortezatajerii/mealhub.git
cd mealhub
```

---

# Create a Virtual Environment

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

---

# Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

# Environment Variables

MealHub uses environment-based configuration through `python-decouple`.

Create the appropriate environment configuration before running the application.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

For services that require external credentials, configure the corresponding environment variables.

Example:

```env
SMSIR_API_KEY=your-api-key
SMSIR_TEMPLATE_ID=your-template-id
```

### Production

Never commit production secrets to Git.

At minimum, production configuration should include:

```env
SECRET_KEY=<strong-secret>
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com
```

When deploying behind a reverse proxy like Nginx with HTTPS, Django needs to trust the proxy headers to handle redirects, CSRF, and secure cookies correctly:

```env
# Production Security & Proxy Settings
CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
USE_X_FORWARDED_HOST=True
SECURE_SSL_REDIRECT=False  # Let Nginx handle the HTTP -> HTTPS redirect
```

---

# Running Locally

Apply migrations:

```bash
python manage.py migrate
```

Create a superuser:

```bash
python manage.py createsuperuser
```

Collect static files if required:

```bash
python manage.py collectstatic
```

Start the development server:

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

---

# Testing

MealHub uses Django's testing infrastructure.

Run the test suite with:

```bash
python manage.py test
```

Run Django's system checks:

```bash
python manage.py check
```

Before submitting a Pull Request, contributors should verify:

```bash
python manage.py check
python manage.py test
```

Migration changes should also be reviewed carefully before being committed.

---

# Production Deployment

MealHub is designed to run in a Linux production environment using:

```text
Nginx
   │
   ▼
Gunicorn
   │
   ▼
Django
   │
   ▼
Database
```

## Server Requirements

A typical deployment requires:

* Linux server
* Python
* Git
* Nginx
* Gunicorn
* systemd
* Project virtual environment
* Production environment variables

---

## Initial Server Setup

Clone the project:

```bash
git clone https://github.com/mortezatajerii/mealhub.git
cd mealhub
```

Create the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Configure environment variables and run:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

---

# Gunicorn

Gunicorn should be managed by `systemd` in production.

A basic application command is:

```bash
gunicorn config.wsgi:application
```

### Worker Calculation

For production, the number of Gunicorn workers should be calculated based on the server's CPU cores to prevent context-switching overhead:

```text
Workers = (2 × CPU_Cores) + 1
```

For example, on a 2-core VPS, use `--workers 5`. It is also highly recommended to use a Unix socket instead of a TCP port for internal Nginx-to-Gunicorn communication to reduce overhead.

For production, the recommended setup is to run Gunicorn through a dedicated systemd service and expose it through a Unix socket.

Example architecture:

```text
Nginx
  │
  ▼
/run/gunicorn/mealhub.sock
  │
  ▼
Gunicorn
  │
  ▼
Django
```

---

# Nginx

Nginx acts as the public-facing web server and reverse proxy.

It should:

* Terminate HTTPS
* Serve static files
* Serve media files
* Forward dynamic requests to Gunicorn
* Apply appropriate security headers and request limits

Conceptually:

```text
Client
  │
  ▼
Nginx
  ├── /static/ → Static Files
  ├── /media/  → Media Files
  └── /        → Gunicorn → Django
```

---

# CI/CD

MealHub includes an automated GitHub Actions deployment workflow.

The deployment pipeline follows this general process:

```text
Developer
    │
    │ git push
    ▼
GitHub
    │
    ▼
GitHub Actions
    │
    ├── Install dependencies
    ├── Django system checks
    ├── Migration checks
    └── Deployment
            │
            ▼
      Production Server
            │
            ├── Update source
            ├── Install dependencies
            ├── Run migrations
            ├── Collect static files
            ├── Restart application service
            └── Reload Nginx
```

The workflow is located at:

```text
.github/workflows/deploy-django-application.yml
```

The CI process performs Django validation before deployment.

This helps prevent an invalid application state from being deployed directly to the production server.

> **⚠️ Note on Database Migrations in CI/CD:**
> Running `python manage.py migrate` automatically in a CI/CD pipeline is convenient for early-stage projects. However, as the `reservations` and `wallets` tables grow, backward-incompatible migrations (like renaming columns or adding non-nullable fields without defaults) can cause application downtime. For mature production environments, migrations should be reviewed, applied manually during maintenance windows, or handled via zero-downtime migration strategies (e.g., expand-and-contract pattern).

---

# Contributing

Contributions are welcome.

If you want to contribute:

### 1. Fork the repository

```bash
git clone https://github.com/mortezatajerii/mealhub.git
cd mealhub
```

### 2. Create a feature branch

```bash
git checkout -b feature/my-feature
```

### 3. Implement your changes

Keep business logic inside the appropriate domain application.

For example:

```text
accounts/
organizations/
menus/
reservations/
wallets/
```

Avoid introducing cross-domain coupling unless there is a clear business reason.

### 4. Run checks

```bash
python manage.py check
python manage.py test
```

### 5. Commit your changes

```bash
git add .
git commit -m "Add my feature"
```

### 6. Push your branch

```bash
git push origin feature/my-feature
```

Then open a Pull Request against `main`.

For larger architectural changes, opening an Issue first is encouraged.

---

# Roadmap

The roadmap is intentionally evolutionary.

### Backend & Domain

* [ ] Expand reservation lifecycle
* [ ] Improve organizational permission model
* [ ] Complete wallet workflows
* [ ] Improve financial settlement logic
* [ ] Expand automated test coverage

### Authentication

* [ ] Complete OTP authentication workflow
* [ ] Improve authentication security
* [ ] Expand API authentication flows

### API

* [ ] Expand REST API coverage
* [ ] API documentation
* [ ] Improved filtering and pagination

### Infrastructure

* [ ] PostgreSQL production configuration
* [ ] Background task processing
* [ ] Monitoring and observability
* [ ] Containerized deployment

### Product

* [ ] Online payment integration
* [ ] Advanced reporting
* [ ] Notification system
* [ ] Reservation cancellation/modification workflows

---

# Project Status

🚧 **MealHub is currently under active development.**

The core domain structure is being developed incrementally, and some parts of the system are more mature than others.

The project should therefore be considered a **work in progress**, and APIs, domain models, permissions, and workflows may change as development continues.

---

# License

MealHub is licensed under the **Mozilla Public License 2.0 (MPL-2.0)**.

See the [`LICENSE`](LICENSE) file for the complete license text.

---

# Contributing to MealHub

MealHub is open to developers interested in:

* Django
* Backend engineering
* REST API development
* Organizational software
* Database design
* Business-domain modeling
* Authentication and authorization
* DevOps and CI/CD

Whether you want to report a bug, improve an existing feature, propose an architectural change, or contribute code, your input is welcome.

If you find the project useful or interesting, consider giving the repository a ⭐.

---

# Author

**Morteza**

MealHub is being developed as an ongoing backend engineering project with a focus on building a realistic organizational system rather than a simple CRUD demonstration.

---

<p align="center">
  Built with Django and Python.
</p>
