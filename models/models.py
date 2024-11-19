# models/models.py
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text, Table
from sqlalchemy.orm import relationship
from config.database import Base

# Tablas intermedias
user_workout_plans = Table(
    'user_workout_plans',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('workout_plan_id', Integer, ForeignKey('workout_plans.id'), primary_key=True)
)

user_nutrition_plans = Table(
    'user_nutrition_plans',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('nutrition_plan_id', Integer, ForeignKey('nutrition_plans.id'), primary_key=True)
)

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    trainers = relationship("Trainer", back_populates="admin")

class Trainer(Base):
    __tablename__ = "trainers"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    admin_id = Column(Integer, ForeignKey("admins.id"))
    admin = relationship("Admin", back_populates="trainers")
    users = relationship("User", back_populates="trainer")
    workout_plans = relationship("WorkoutPlan", back_populates="trainer")
    nutrition_plans = relationship("NutritionPlan", back_populates="trainer")
    plans = relationship("Plan", back_populates="trainer")
    routines = relationship("Routine", back_populates="trainer")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    trainer = relationship("Trainer", back_populates="users")
    workout_plans = relationship("WorkoutPlan", secondary=user_workout_plans, back_populates="users")
    nutrition_plans = relationship("NutritionPlan", secondary=user_nutrition_plans, back_populates="users")

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    trainer = relationship("Trainer", back_populates="workout_plans")
    exercises = relationship("Exercise", back_populates="workout_plan", cascade="all, delete-orphan")
    users = relationship("User", secondary=user_workout_plans, back_populates="workout_plans")

class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id"))
    routine_id = Column(Integer, ForeignKey("routines.id"))
    workout_plan = relationship("WorkoutPlan", back_populates="exercises")
    routine = relationship("Routine", back_populates="exercises")

class Routine(Base):
    __tablename__ = "routines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    trainer = relationship("Trainer", back_populates="routines")
    exercises = relationship("Exercise", back_populates="routine")

class NutritionPlan(Base):
    __tablename__ = "nutrition_plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    trainer = relationship("Trainer", back_populates="nutrition_plans")
    meals = relationship("Meal", back_populates="nutrition_plan", cascade="all, delete-orphan")
    users = relationship("User", secondary=user_nutrition_plans, back_populates="nutrition_plans")

class Meal(Base):
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    calories = Column(Integer, nullable=False)
    nutrition_plan_id = Column(Integer, ForeignKey("nutrition_plans.id"))
    nutrition_plan = relationship("NutritionPlan", back_populates="meals")

    
class Plan(Base):
    __tablename__ = "plans"  # o la tabla que corresponda
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    trainer = relationship("Trainer", back_populates="plans")

