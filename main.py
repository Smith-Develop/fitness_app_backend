from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from routes import admin, trainer, user
from config.database import get_db, engine, SessionLocal
import models.models as models
import schemas.schemas as schemas
from utils.auth import *

# Crear todas las tablas
models.Base.metadata.create_all(bind=engine)

# Configuración de CORS
origins = [
    "http://localhost:5173",  # URL del frontend en desarrollo
    "http://localhost:3000",
]

app = FastAPI(title="Fitness API")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Buscar usuario en todas las tablas
    user = None
    role = None
    
    admin = db.query(models.Admin).filter(models.Admin.email == form_data.username).first()
    if admin:
        user = admin
        role = "admin"
    else:
        trainer = db.query(models.Trainer).filter(models.Trainer.email == form_data.username).first()
        if trainer:
            user = trainer
            role = "trainer"
        else:
            user = db.query(models.User).filter(models.User.email == form_data.username).first()
            if user:
                role = "user"

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": role}, 
        expires_delta=access_token_expires
    )
    # Incluir el rol en la respuesta
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": role  # Agregado el rol en la respuesta
    }

@app.get("/")
async def root():
    return {"message": "Fitness API is running"}

# Middleware para verificar roles
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email, role=role)
    except JWTError:
        raise credentials_exception
    
    if token_data.role == "admin":
        user = db.query(models.Admin).filter(models.Admin.email == email).first()
    elif token_data.role == "trainer":
        user = db.query(models.Trainer).filter(models.Trainer.email == email).first()
    else:
        user = db.query(models.User).filter(models.User.email == email).first()
    
    if user is None:
        raise credentials_exception
    return {"user": user, "role": token_data.role}

async def get_current_admin(current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this resource"
        )
    return current_user

async def get_current_trainer(current_user = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "trainer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers can access this resource"
        )
    return current_user

# Incluir routers
app.include_router(admin.router)
app.include_router(trainer.router)
app.include_router(user.router)