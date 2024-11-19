from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
import models.models as models
import schemas.schemas as schemas
from utils.auth import get_current_user

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile/", response_model=schemas.User)
def read_user_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Only users can access their profile")
    return current_user["user"]

@router.put("/profile/", response_model=schemas.User)
def update_user_profile(
    user_update: schemas.UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Only users can update their profile")
    
    user = db.query(models.User).filter(models.User.id == current_user["user"].id).first()
    
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.get("/plans/", response_model=dict)
async def get_user_plans(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Only users can access their plans")
    
    user = db.query(models.User).filter(models.User.id == current_user["user"].id).first()
    
    return {
        "workout_plans": [
            {
                "id": plan.id,
                "name": plan.name,
                "description": plan.description,
                "exercises": [
                    {
                        "name": exercise.name,
                        "sets": exercise.sets,
                        "reps": exercise.reps
                    } for exercise in plan.exercises
                ]
            } for plan in user.workout_plans
        ],
        "nutrition_plans": [
            {
                "id": plan.id,
                "name": plan.name,
                "description": plan.description,
                "meals": [
                    {
                        "name": meal.name,
                        "description": meal.description,
                        "calories": meal.calories
                    } for meal in plan.meals
                ]
            } for plan in user.nutrition_plans
        ]
    }