# LogiSecure: Advanced Logistics Management System

LogiSecure is a professional-grade platform designed for the comprehensive management of logistics fleets and delivery routes. The system prioritizes data integrity and operational security through a modern architecture based on FastAPI and role-based access control.

---

## Technical Architecture

The platform is built on a robust set of technologies to ensure scalability, security, and performance.

### Core Stack
- **Backend Framework:** FastAPI (Python 3.10+)
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL / SQLite
- **Environment Management:** Python-Dotenv

### Security Infrastructure
- **Authentication:** JSON Web Tokens (JWT)
- **Multi-Factor Authentication:** TOTP (Google Authenticator)
- **Encryption:** Passlib (Bcrypt)
- **Access Control:** Dependency Injection-based RBAC (Role-Based Access Control)

---

## Security Implementation

The system implements a centralized security model that enforces permissions at the endpoint level.

### Authentication Flow
1. Primary credentials verification (Email/Password).
2. Mandatory secondary verification via TOTP (Time-based One-Time Password).
3. Strategic generation of short-lived JWT tokens for session management.

### Access Control Levels
The system enforces strict boundaries between different user roles:
- **Gerente (Manager):** Full administrative access, user management, and access to encrypted sensitive financial data.
- **Coordinador (Dispatcher):** Management of delivery routes, fleet status monitoring, and access to general system statistics.
- **Chofer (Driver):** Access to assigned individual routes, real-time status updates, and personalized mileage summaries.

---

## System Overview (Screenshots)

Below are the primary interfaces of the LogiSecure system for portfolio visualization.

### [User Authentication Interface]
![Authentication Page placeholder](/path/to/auth_screenshot.png)
*Professional login interface featuring secondary TOTP verification.*

### [Administrative Dashboard]
![Manager Dashboard placeholder](/path/to/manager_dashboard.png)
*Centralized management view for Gerente role showing users and route control.*

### [Fleet Management and Statistics]
![Dispatcher Statistics placeholder](/path/to/dispatcher_stats.png)
*Fleet statistics and route assignment interface for Coordinador role.*

### [Driver Operation Panel]
![Driver View placeholder](/path/to/driver_dashboard.png)
*Optimized interface for drivers to track and update route progress.*

---

## Installation and Deployment

### Environment Setup
1. Clone the repository and navigate to the project directory.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure the `.env` file with the following variables:
   - DATABASE_URL
   - JWT_SECRET
   - JWT_ALGORITHM
   - JWT_EXPIRATION_HOURS

### Database Initialization
Apply the initial schema and populate with seed data:
```bash
python seed.py
```

### Server Execution
Launch the production-ready server using Uvicorn:
```bash
python -m app.main
```

---

## Functionality Matrix

| Module | Gerente | Coordinador | Chofer |
| :--- | :---: | :---: | :---: |
| User Administration | Supported | Restrict | Restrict |
| Route Assignment | Supported | Supported | Restrict |
| Operational Statistics | Supported | Supported | Restrict |
| Financial Sensitive Data | Supported | Restrict | Restrict |
| Route Status Updates | Supported | Supported | Supported |
| Personal Performance | Supported | Supported | Supported |

---
*LogiSecure System Documentation - Version 1.1.0*
