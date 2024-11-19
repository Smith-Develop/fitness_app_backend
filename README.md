# Fitness App Backend

API REST para la aplicación Fitness App, un sistema de gestión de gimnasio que incluye administración de usuarios, entrenadores, planes de ejercicio y nutrición con sistema de autenticación y roles.

[![Abrir en Postman](https://run.pstmn.io/button.svg)](https://documenter.getpostman.com/view/38671791/2sAYBRFu4A)

## 🚀 Características
* Autenticación y autorización con JWT
* Sistema de roles (Admin/Trainer/User)
* Gestión completa de usuarios y entrenadores
* Sistema de planes de ejercicio y nutrición
* API RESTful documentada con OpenAPI/Swagger
* Asignación de planes a usuarios

## 🛠️ Tecnologías Utilizadas
* Python 3.12
* FastAPI
* MySQL
* SQLAlchemy (ORM)
* JWT para autenticación
* bcrypt para encriptación
* Pydantic para validación de datos

## 📋 Prerrequisitos
* Python 3.12 o superior
* MySQL 8.0 o superior
* pip (gestor de paquetes de Python)

## 🔧 Instalación

1. Clonar el repositorio
```bash
git clone https://github.com/Smith-Develop/backend-fitness-app.git
cd backend-fitness-app
```

2. Crear y activar entorno virtual
```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/Mac
python3 -m venv env
source env/bin/activate
```

3. Instalar dependencias
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno
Crear archivo `.env`:
```env
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_NAME=fitness_db
SECRET_KEY=tu_secret_key_super_segura
```

5. Configurar la base de datos
```sql
CREATE DATABASE fitness_db;
USE fitness_db;

CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL
);

CREATE TABLE trainers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    admin_id INT,
    FOREIGN KEY (admin_id) REFERENCES admins(id)
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    trainer_id INT,
    FOREIGN KEY (trainer_id) REFERENCES trainers(id)
);

CREATE TABLE workout_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    trainer_id INT,
    FOREIGN KEY (trainer_id) REFERENCES trainers(id)
);

CREATE TABLE exercises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sets INT NOT NULL,
    reps INT NOT NULL,
    workout_plan_id INT,
    FOREIGN KEY (workout_plan_id) REFERENCES workout_plans(id)
);

CREATE TABLE nutrition_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    trainer_id INT,
    FOREIGN KEY (trainer_id) REFERENCES trainers(id)
);

CREATE TABLE meals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    calories INT NOT NULL,
    nutrition_plan_id INT,
    FOREIGN KEY (nutrition_plan_id) REFERENCES nutrition_plans(id)
);

CREATE TABLE user_workout_plans (
    user_id INT,
    workout_plan_id INT,
    PRIMARY KEY (user_id, workout_plan_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (workout_plan_id) REFERENCES workout_plans(id)
);

CREATE TABLE user_nutrition_plans (
    user_id INT,
    nutrition_plan_id INT,
    PRIMARY KEY (user_id, nutrition_plan_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (nutrition_plan_id) REFERENCES nutrition_plans(id)
);
```

6. Iniciar el servidor
```bash
uvicorn main:app --reload
```

## 📚 Estructura del Proyecto
```
/fitness-app
  /config
    database.py         # Configuración de la base de datos
  /models
    models.py          # Modelos SQLAlchemy
  /routes
    admin.py          # Rutas de administrador
    trainer.py        # Rutas de entrenador
    user.py           # Rutas de usuario
  /schemas
    schemas.py        # Esquemas Pydantic
  /utils
    auth.py          # Utilidades de autenticación
    initial_setup.py # Configuración inicial
  .env               # Variables de entorno
  main.py           # Punto de entrada
  requirements.txt   # Dependencias
```

## 🔑 Endpoints API

### Auth
* `POST /token` - Login
```json
{
    "username": "admin@admin.com",
    "password": "password1313"
}
```

### Admin
* `POST /admin/trainers/` - Crear entrenador
```json
{
    "email": "trainer@example.com",
    "password": "password123",
    "full_name": "John Trainer"
}
```
* `GET /admin/trainers/` - Listar entrenadores
* `PUT /admin/trainers/{id}` - Actualizar entrenador
* `DELETE /admin/trainers/{id}` - Eliminar entrenador
* `POST /admin/create-admin/` - Crear nuevo admin
* `POST /admin/request-password-reset/` - Solicitar reset de contraseña
* `POST /admin/reset-password/` - Resetear contraseña

### Trainer
* `POST /trainer/users/` - Crear usuario
* `GET /trainer/users/` - Listar usuarios
* `PUT /trainer/users/{id}` - Actualizar usuario
* `DELETE /trainer/users/{id}` - Eliminar usuario
* `POST /trainer/workout-plans/` - Crear plan ejercicios
* `PUT /trainer/workout-plans/{id}` - Actualizar plan ejercicios
* `POST /trainer/nutrition-plans/` - Crear plan nutricional
* `PUT /trainer/nutrition-plans/{id}` - Actualizar plan nutricional
* `POST /trainer/assign-workout/{user_id}/{plan_id}` - Asignar plan ejercicios
* `POST /trainer/assign-nutrition/{user_id}/{plan_id}` - Asignar plan nutricional

### User
* `GET /user/profile/` - Ver perfil
* `PUT /user/profile/` - Actualizar perfil
* `GET /user/plans/` - Ver planes asignados

## ⚠️ Errores Comunes
1. Error de conexión a la base de datos
   - Verificar que MySQL esté corriendo
   - Comprobar credenciales en .env
   - Asegurar que la base de datos existe

2. Error de CORS
   - Verificar origen del frontend en la lista de permitidos
   - Revisar configuración CORS en main.py

3. Error en autenticación
   - Verificar SECRET_KEY en .env
   - Comprobar formato del token JWT

## 📚 Referencias y Documentación
* [FastAPI Documentation](https://fastapi.tiangolo.com/)
* [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
* [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
* [MySQL Documentation](https://dev.mysql.com/doc/)

## ✒️ Autor
* **Smith Grisales** - *Desarrollador web Full-Stack* - [Smith-Develop](https://github.com/Smith-Develop)

⌨️ con ❤️ por [Smith Grisales](https://github.com/Smith-Develop) 😊
