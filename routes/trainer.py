from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db
import models.models as models
import schemas.schemas as schemas
from utils.auth import get_current_trainer, get_password_hash

router = APIRouter(prefix="/trainer", tags=["trainer"])

@router.post("/users/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_user = models.User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        trainer_id=current_user["user"].id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).filter(
        models.User.trainer_id == current_user["user"].id
    ).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_update: schemas.UserCreate,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.email = user_update.email
    db_user.full_name = user_update.full_name
    if user_update.password:
        db_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
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
    current_user = Depends(get_current_trainer)
):
    plans = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.trainer_id == current_user["user"].id
    ).offset(skip).limit(limit).all()
    return plans

@router.get("/routines/", response_model=List[schemas.Routine])
def read_routines(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    routines = db.query(models.Routine).filter(
        models.Routine.trainer_id == current_user["user"].id
    ).offset(skip).limit(limit).all()
    return routines

@router.post("/routines/", response_model=schemas.Routine)
def create_routine(
    routine: schemas.RoutineCreate,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_routine = models.Routine(
        name=routine.name,
        description=routine.description,
        trainer_id=current_user["user"].id
    )
    db.add(db_routine)
    db.flush()

    for exercise in routine.exercises:
        db_exercise = models.Exercise(
            **exercise.dict(),
            routine_id=db_routine.id
        )
        db.add(db_exercise)

    db.commit()
    db.refresh(db_routine)
    return db_routine

@router.put("/routines/{routine_id}", response_model=schemas.Routine)
def update_routine(
    routine_id: int,
    routine: schemas.RoutineUpdate,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_routine = db.query(models.Routine).filter(
        models.Routine.id == routine_id,
        models.Routine.trainer_id == current_user["user"].id
    ).first()
    if not db_routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    # Update routine basic info
    for key, value in routine.dict(exclude_unset=True).items():
        if key != "exercises":
            setattr(db_routine, key, value)

    # If exercises are provided, update them
    if routine.exercises is not None:
        # Delete existing exercises
        db.query(models.Exercise).filter(models.Exercise.routine_id == routine_id).delete()
        
        # Add new exercises
        for exercise in routine.exercises:
            db_exercise = models.Exercise(
                **exercise.dict(),
                routine_id=routine_id
            )
            db.add(db_exercise)

    db.commit()
    db.refresh(db_routine)
    return db_routine

@router.delete("/routines/{routine_id}")
def delete_routine(
    routine_id: int,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_routine = db.query(models.Routine).filter(
        models.Routine.id == routine_id,
        models.Routine.trainer_id == current_user["user"].id
    ).first()
    if not db_routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    # Delete associated exercises first
    db.query(models.Exercise).filter(models.Exercise.routine_id == routine_id).delete()
    
    # Delete the routine
    db.delete(db_routine)
    db.commit()
    
    return {"message": "Routine deleted successfully"}


@router.get("/workout-plans/", response_model=List[schemas.WorkoutPlan])
def read_workout_plans(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    workout_plans = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.trainer_id == current_user["user"].id
    ).offset(skip).limit(limit).all()
    return workout_plans

@router.get("/nutrition-plans/", response_model=List[schemas.NutritionPlan])
def read_nutrition_plans(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    nutrition_plans = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.trainer_id == current_user["user"].id
    ).offset(skip).limit(limit).all()
    return nutrition_plans

@router.post("/workout-plans/", response_model=schemas.WorkoutPlan)
def create_workout_plan(
    plan: schemas.WorkoutPlanCreate,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_plan = models.WorkoutPlan(
        name=plan.name,
        description=plan.description,
        trainer_id=current_user["user"].id
    )
    db.add(db_plan)
    db.flush()

    for exercise in plan.exercises:
        db_exercise = models.Exercise(
            **exercise.dict(),
            workout_plan_id=db_plan.id
        )
        db.add(db_exercise)

    db.commit()
    db.refresh(db_plan)
    return db_plan













@router.put("/workout-plans/{plan_id}", response_model=schemas.WorkoutPlan)
def update_workout_plan(
    plan_id: int,
    plan_update: schemas.WorkoutPlanCreate,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.id == plan_id,
        models.WorkoutPlan.trainer_id == current_user["user"].id
    ).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    db_plan.name = plan_update.name
    db_plan.description = plan_update.description
    
    # Delete existing exercises
    db.query(models.Exercise).filter(models.Exercise.workout_plan_id == plan_id).delete()
    
    # Add new exercises
    for exercise in plan_update.exercises:
        db_exercise = models.Exercise(
            **exercise.dict(),
            workout_plan_id=db_plan.id
        )
        db.add(db_exercise)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.delete("/workout-plans/{plan_id}")
def delete_workout_plan(
    plan_id: int,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.id == plan_id,
        models.WorkoutPlan.trainer_id == current_user["user"].id
    ).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    db.delete(db_plan)
    db.commit()
    return {"message": "Workout plan deleted"}

@router.post("/nutrition-plans/", response_model=schemas.NutritionPlan)
def create_nutrition_plan(
    plan: schemas.NutritionPlanCreate,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_plan = models.NutritionPlan(
        name=plan.name,
        description=plan.description,
        trainer_id=current_user["user"].id
    )
    db.add(db_plan)
    db.flush()

    for meal in plan.meals:
        db_meal = models.Meal(
            **meal.dict(),
            nutrition_plan_id=db_plan.id
        )
        db.add(db_meal)

    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.get("/nutrition-plans/", response_model=List[schemas.NutritionPlan])
def read_nutrition_plans(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    plans = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.trainer_id == current_user["user"].id
    ).offset(skip).limit(limit).all()
    return plans

@router.put("/nutrition-plans/{plan_id}", response_model=schemas.NutritionPlan)
def update_nutrition_plan(
    plan_id: int,
    plan_update: schemas.NutritionPlanCreate,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_plan = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.id == plan_id,
        models.NutritionPlan.trainer_id == current_user["user"].id
    ).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Nutrition plan not found")
    
    db_plan.name = plan_update.name
    db_plan.description = plan_update.description
    
    # Delete existing meals
    db.query(models.Meal).filter(models.Meal.nutrition_plan_id == plan_id).delete()
    
    # Add new meals
    for meal in plan_update.meals:
        db_meal = models.Meal(
            **meal.dict(),
            nutrition_plan_id=db_plan.id
        )
        db.add(db_meal)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.delete("/nutrition-plans/{plan_id}")
def delete_nutrition_plan(
    plan_id: int,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    db_plan = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.id == plan_id,
        models.NutritionPlan.trainer_id == current_user["user"].id
    ).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Nutrition plan not found")
    
    db.delete(db_plan)
    db.commit()
    return {"message": "Nutrition plan deleted"}

@router.post("/assign-workout/{user_id}/{plan_id}")
def assign_workout_plan(
    user_id: int,
    plan_id: int,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.id == plan_id,
        models.WorkoutPlan.trainer_id == current_user["user"].id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")

    user.workout_plans.append(plan)
    db.commit()
    return {"message": "Workout plan assigned successfully"}

@router.post("/assign-nutrition/{user_id}/{plan_id}")
def assign_nutrition_plan(
    user_id: int,
    plan_id: int,
    current_user = Depends(get_current_trainer),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.trainer_id == current_user["user"].id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    plan = db.query(models.NutritionPlan).filter(
        models.NutritionPlan.id == plan_id,
        models.NutritionPlan.trainer_id == current_user["user"].id
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Nutrition plan not found")

    user.nutrition_plans.append(plan)
    db.commit()
    return {"message": "Nutrition plan assigned successfully"}