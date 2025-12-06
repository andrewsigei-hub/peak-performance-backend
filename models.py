from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    Boolean,
    ForeignKey,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship, declarative_base

# Setup base class

Base = declarative_base()  # The class all  models inherit from


# Creation of schema


# 1. Table: User
class User(Base):
    # User table
    __tablename__ = "users"  ## must provide th table name
    # Tables have at least one column
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    google_id = Column(
        String, unique=True, nullable=True
    )  ## Can be empty when user hasnt logged in
    created_at = Column(DateTime, default=func.now())

    # Relationships: One User to Many Workouts and Many Meals
    workouts = relationship(
        "Workout", back_populates="user", cascade="all, delete-orphan"
    )
    meals = relationship("Meal", back_populates="user", cascade="all, delete-orphan")


# 2. Table: Workout (Child of User, Parent of Exercise)
class Workout(Base):
    """Represents a workout session (e.g., a run, a lift, HIIT)."""

    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign Key
    type = Column(String, nullable=False)
    duration_min = Column(Integer, nullable=False)
    distance_km = Column(Float, nullable=True)
    avg_pace = Column(Float, nullable=True)
    date = Column(Date, nullable=False)
    is_starred = Column(Boolean, default=False)

    # Relationships - Connects user to workouts
    user = relationship("User", back_populates="workouts")
    exercises = relationship(
        "Exercise", back_populates="workout", cascade="all, delete-orphan"
    )  ## If a workout is deleted all exercise are too


# 3. Table: Exercise (Child of Workout)
class Exercise(Base):
    """Represents a specific exercise performed during a strength/lift workout."""

    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(
        Integer, ForeignKey("workouts.id"), nullable=False
    )  # Foreign Key
    name = Column(String, nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)

    # Relationship
    workout = relationship("Workout", back_populates="exercises")  # links to workout


# 4. Meal table
class Meal(Base):
    """Represents a logged meal or food entry, including macronutrients."""

    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign Key
    name = Column(String, nullable=False)
    calories = Column(Integer, nullable=False)
    protein = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

    # Relationship
    user = relationship("User", back_populates="meals")  # Connects meal to a user
