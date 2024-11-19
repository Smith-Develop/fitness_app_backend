from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
from config.database import get_db
import models.models as models
import schemas.schemas as schemas
from utils.auth import get_current_admin, get_password_hash
from utils.email import send_reset_email

router = APIRouter(prefix="/admin", tags=["admin"])

class TrainerUpdate(BaseModel):
    email: str
    full_name: str
    password: Optional[str] = None
    
    class Config:
        from_attributes = True

@router.post("/trainers/", response_model=schemas.Trainer)
def create_trainer(
    trainer: schemas.TrainerCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_trainer = models.Trainer(
        email=trainer.email,
        hashed_password=get_password_hash(trainer.password),
        full_name=trainer.full_name,
        admin_id=current_user["user"].id
    )
    db.add(db_trainer)
    db.commit()
    db.refresh(db_trainer)
    return db_trainer

@router.get("/trainers/", response_model=List[schemas.Trainer])
def read_trainers(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    trainers = db.query(models.Trainer).offset(skip).limit(limit).all()
    return trainers

@router.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_data: schemas.UserUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        # Verificar si el usuario existe
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar si el email ya existe en otro usuario
        existing_user = db.query(models.User).filter(
            models.User.email == user_data.email,
            models.User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="El email ya está en uso"
            )
        
        # Actualizar campos básicos
        db_user.email = user_data.email
        db_user.full_name = user_data.full_name
        
        # Actualizar trainer_id si se proporciona
        if user_data.trainer_id is not None:
            # Verificar que el trainer existe
            trainer_exists = db.query(models.Trainer).filter(
                models.Trainer.id == user_data.trainer_id
            ).first()
            if not trainer_exists and user_data.trainer_id != 0:
                raise HTTPException(
                    status_code=404,
                    detail="Entrenador no encontrado"
                )
            db_user.trainer_id = user_data.trainer_id or None
        
        # Actualizar contraseña si se proporciona
        if user_data.password:
            db_user.hashed_password = get_password_hash(user_data.password)
        
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}

@router.get("/plans/", response_model=List[schemas.Plan])
def read_plans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    plans = db.query(models.WorkoutPlan).offset(skip).limit(limit).all()
    return plans

@router.get("/routines/", response_model=List[schemas.Routine])
def read_routines(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    routines = db.query(models.Routine).offset(skip).limit(limit).all()
    return routines

@router.post("/routines/", response_model=schemas.Routine)
def create_routine(
    routine: schemas.RoutineCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    try:
        db_routine = models.Routine(**routine.dict())
        db.add(db_routine)
        db.commit()
        db.refresh(db_routine)
        return db_routine
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/routines/{routine_id}", response_model=schemas.Routine)
def update_routine(
    routine_id: int,
    routine_data: schemas.RoutineUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_routine = db.query(models.Routine).filter(models.Routine.id == routine_id).first()
    if not db_routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    
    for field, value in routine_data.dict(exclude_unset=True).items():
        setattr(db_routine, field, value)
    
    try:
        db.commit()
        db.refresh(db_routine)
        return db_routine
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/routines/{routine_id}")
def delete_routine(
    routine_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_routine = db.query(models.Routine).filter(models.Routine.id == routine_id).first()
    if not db_routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    
    db.delete(db_routine)
    db.commit()
    return {"message": "Routine deleted"}


@router.get("/workout-plans/", response_model=List[schemas.WorkoutPlan])
def read_workout_plans(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    workout_plans = db.query(models.WorkoutPlan).offset(skip).limit(limit).all()
    return workout_plans

@router.get("/nutrition-plans/", response_model=List[schemas.NutritionPlan])
def read_nutrition_plans(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    nutrition_plans = db.query(models.NutritionPlan).offset(skip).limit(limit).all()
    return nutrition_plans

@router.put("/trainers/{trainer_id}", response_model=schemas.Trainer)
async def update_trainer(
    trainer_id: int,
    trainer_data: TrainerUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Verificar si el entrenador existe
    db_trainer = db.query(models.Trainer).filter(models.Trainer.id == trainer_id).first()
    if not db_trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    # Actualizar campos
    db_trainer.email = trainer_data.email
    db_trainer.full_name = trainer_data.full_name
    
    # Solo actualizar la contraseña si se proporciona una nueva
    if trainer_data.password:
        db_trainer.hashed_password = get_password_hash(trainer_data.password)
    
    try:
        db.commit()
        db.refresh(db_trainer)
        return db_trainer
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/trainers/{trainer_id}")
def delete_trainer(
    trainer_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_trainer = db.query(models.Trainer).filter(models.Trainer.id == trainer_id).first()
    if not db_trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    db.delete(db_trainer)
    db.commit()
    return {"message": "Trainer deleted"}

reset_tokens = {}

@router.post("/create-admin/", response_model=schemas.Admin)
async def create_admin(
    admin: schemas.AdminCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_admin = models.Admin(
        email=admin.email,
        hashed_password=get_password_hash(admin.password),
        full_name=admin.full_name
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

@router.put("/admin/{admin_id}", response_model=schemas.Admin)
async def update_admin(
    admin_id: int,
    admin_data: schemas.AdminUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    db_admin.email = admin_data.email
    db_admin.full_name = admin_data.full_name
    
    if admin_data.password:
        db_admin.hashed_password = get_password_hash(admin_data.password)
    
    try:
        db.commit()
        db.refresh(db_admin)
        return db_admin
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/admin/{admin_id}")
async def delete_admin(
    admin_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    db.delete(db_admin)
    db.commit()
    return {"message": "Admin deleted"}


@router.post("/request-password-reset/")
async def request_password_reset(
    request: schemas.AdminLoginReset,
    db: Session = Depends(get_db)
):
    user = None
    # Buscar en todas las tablas
    admin = db.query(models.Admin).filter(models.Admin.email == request.email).first()
    trainer = db.query(models.Trainer).filter(models.Trainer.email == request.email).first()
    user = db.query(models.User).filter(models.User.email == request.email).first()

    if not any([admin, trainer, user]):
        raise HTTPException(status_code=404, detail="Email no encontrado")

    # Generar token
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = {
        "email": request.email,
        "expires": datetime.utcnow() + timedelta(hours=1)
    }

    # Enviar email
    send_reset_email(request.email, token)
    
    return {"message": "Si el email existe, recibirás instrucciones para resetear tu contraseña"}

@router.post("/reset-password/")
async def reset_password(
    reset_data: schemas.PasswordReset,
    db: Session = Depends(get_db)
):
    token_data = reset_tokens.get(reset_data.token)
    if not token_data:
        raise HTTPException(status_code=400, detail="Token inválido")
    
    if datetime.utcnow() > token_data["expires"]:
        raise HTTPException(status_code=400, detail="Token expirado")

    # Actualizar contraseña en la tabla correspondiente
    admin = db.query(models.Admin).filter(models.Admin.email == token_data["email"]).first()
    trainer = db.query(models.Trainer).filter(models.Trainer.email == token_data["email"]).first()
    user = db.query(models.User).filter(models.User.email == token_data["email"]).first()

    new_password_hash = get_password_hash(reset_data.new_password)

    if admin:
        admin.hashed_password = new_password_hash
    elif trainer:
        trainer.hashed_password = new_password_hash
    elif user:
        user.hashed_password = new_password_hash

    db.commit()
    del reset_tokens[reset_data.token]
    
    return {"message": "Contraseña actualizada exitosamente"}