from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: str
    full_name: str

class UserCreate(UserBase):
    password: str
    trainer_id: Optional[int] = None

class UserUpdate(UserBase):
    password: Optional[str] = None
    trainer_id: Optional[int] = None

class User(UserBase):
    id: int
    trainer_id: Optional[int] = None

    class Config:
        from_attributes = True


class TrainerBase(BaseModel):
    email: str
    full_name: str

class TrainerCreate(TrainerBase):
    password: str

class TrainerUpdate(TrainerBase):
    password: Optional[str] = None

class Trainer(TrainerBase):
    id: int
    admin_id: int

    class Config:
        from_attributes = True

class AdminBase(BaseModel):
    email: EmailStr
    full_name: str

class AdminCreate(AdminBase):
    password: str

class Admin(AdminBase):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    email: str | None = None
    role: str | None = None

class Plan(BaseModel):
    id: int
    name: str
    description: str | None = None
    trainer_id: int

    class Config:
        from_attributes = True

class Routine(BaseModel):
    id: int
    name: str
    description: str | None = None
    trainer_id: int

    class Config:
        from_attributes = True

class ExerciseBase(BaseModel):
    name: str
    sets: int
    reps: int

class ExerciseCreate(ExerciseBase):
    pass

class Exercise(ExerciseBase):
    id: int
    workout_plan_id: int

    class Config:
        from_attributes = True

class WorkoutPlanBase(BaseModel):
    name: str
    description: str | None = None

class WorkoutPlanCreate(WorkoutPlanBase):
    exercises: list[ExerciseCreate]

class WorkoutPlan(WorkoutPlanBase):
    id: int
    trainer_id: int
    exercises: list[Exercise]

    class Config:
        from_attributes = True

class MealBase(BaseModel):
    name: str
    description: str | None = None
    calories: int

class MealCreate(MealBase):
    pass

class Meal(MealBase):
    id: int
    nutrition_plan_id: int

    class Config:
        from_attributes = True

class NutritionPlanBase(BaseModel):
    name: str
    description: str | None = None

class NutritionPlanCreate(NutritionPlanBase):
    meals: list[MealCreate]

class NutritionPlan(NutritionPlanBase):
    id: int
    trainer_id: int
    meals: list[Meal]

    class Config:
        from_attributes = True

class AdminLoginReset(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str