# 🚚 LogiSecure: Gestión Logística de Alta Seguridad

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)](https://jwt.io/)

LogiSecure es una plataforma moderna de gestión de rutas y flotas diseñada con un enfoque primordial en la **seguridad de la información** y la **integridad operativa**. Utiliza arquitecturas de última generación para garantizar que cada rol acceda únicamente a lo necesario.

---

## ✨ Características Principales

- **🛡️ Seguridad de Grado Industrial**: Autenticación JWT robusta con protección de rutas mediante Inyección de Dependencias de FastAPI.
- **🔐 MFA Obligatorio**: Implementación nativa de **Google Authenticator (TOTP)** para prevenir accesos no autorizados.
- **👥 Role-Based Access Control (RBAC)**: Tres niveles de acceso claramente definidos (Gerente, Coordinador, Chofer).
- **🛣️ Gestión de Rutas en Tiempo Real**: Creación, monitoreo y actualización de estados de viaje.
- **📊 Business Intelligence**: Panel de estadísticas en tiempo real para la toma de decisiones.
- **🕵️ Protección de Datos Sensibles**: Cifrado y control estricto sobre márgenes de ganancia y costos operativos.

---

## 🛠️ Arquitectura de Seguridad

El proyecto ha sido refactorizado para eliminar vulnerabilidades de middleware comunes, adoptando el patrón de **Inyección de Dependencias**:

```mermaid
graph TD
    A[Cliente / Navegador] -->|Credenciales| B(Auth Service)
    B -->|Genera| C[JWT Token + TOTP Check]
    C --> D{API Gateway}
    D -->|Depends: get_current_user| E[Endpoints Públicos]
    D -->|Depends: get_gerente_user| F[Operaciones Sensibles]
    D -->|Depends: get_dispatcher_user| G[Gestión de Rutas]
```

---

## 🚦 Guía de Inicio Rápido

### 1. Requisitos Previos

- Python 3.9+
- PostgreSQL
- Google Authenticator en tu dispositivo móvil.

### 2. Instalación

```bash
git clone https://github.com/tu-usuario/logisecure.git
cd logisecure
pip install -r requirements.txt
```

### 3. Configuración (.env)

Crea un archivo `.env` en la raíz con lo siguiente:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/logisecure
JWT_SECRET=tu_clave_secreta_aqui
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=8
```

### 4. Ejecución

```bash
# Iniciar Base de Datos y Servidor
python -m app.main
```

---

## 🎭 Matriz de Roles y Permisos

| Módulo                            | Chofer | Coordinador | Gerente |
| :-------------------------------- | :----: | :---------: | :-----: |
| **Mis Rutas (Iniciar/Finalizar)** |   ✅   |     ✅      |   ✅    |
| **Asignar nuevas rutas**          |   ❌   |     ✅      |   ✅    |
| **Estadísticas de Flota**         |   ❌   |     ✅      |   ✅    |
| **Gestión de Usuarios**           |   ❌   |     ❌      |   ✅    |
| **Datos de Costos Reales**        |   ❌   |     ❌      |   ✅    |
| **Generar Códigos Temporales**    |   ❌   |     ❌      |   ✅    |

---

## 🧪 Datos de Prueba (Seed)

Si utilizas el sistema de semillas, puedes usar estas credenciales iniciales:

- **Gerente**: `lizgondie@gmail.com` | Pass: `admin123`
- **Coordinador**: `dispatcher_seed1@logisecure.com` | Pass: `password`
- **Chofer**: `chofer_seed1@logisecure.com` | Pass: `password`

---

## 🚀 Tecnologías Utilizadas

- **Backend**: FastAPI, SQLAlchemy (ORM), Pydantic (Validación).
- **Seguridad**: Passlib (Bcrypt), PyJWT, PyOTP.
- **Frontend**: HTML5, Vanilla CSS (Custom Properties), JavaScript moderno (Async/Await).
- **Base de Datos**: PostgreSQL / SQLite (opcional para desarrollo).

---

> [!IMPORTANT]
> **LogiSecure** está diseñado bajo los principios de _Minimal Privilege Access_. Cada endpoint está validado individualmente para asegurar que no existan fugas de información entre roles.

---

© 2026 LogiSecure Inc. - Seguridad en cada kilómetro.
