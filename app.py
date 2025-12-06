from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr

from models import Base, User, Workout, Exercise, Meal

# Database Configuration
DATABASE_URL = "sqlite:///./fitness_tracker.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Fitness Tracker API",
    description="API for tracking workouts, exercises, and meals",
    version="1.0.0",
)

# CORS Configuration (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# Pydantic Schemas (Request/Response Models)
# ============================================


# User Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    google_id: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    google_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Workout Schemas
class WorkoutCreate(BaseModel):
    user_id: int
    type: str
    duration_min: int
    distance_km: Optional[float] = None
    avg_pace: Optional[float] = None
    date: date
    is_starred: bool = False


class WorkoutUpdate(BaseModel):
    type: Optional[str] = None
    duration_min: Optional[int] = None
    distance_km: Optional[float] = None
    avg_pace: Optional[float] = None
    date: Optional[date] = None
    is_starred: Optional[bool] = None


class WorkoutResponse(BaseModel):
    id: int
    user_id: int
    type: str
    duration_min: int
    distance_km: Optional[float]
    avg_pace: Optional[float]
    date: date
    is_starred: bool

    class Config:
        from_attributes = True


# Exercise Schemas
class ExerciseCreate(BaseModel):
    workout_id: int
    name: str
    sets: int
    reps: int
    weight: float


class ExerciseResponse(BaseModel):
    id: int
    workout_id: int
    name: str
    sets: int
    reps: int
    weight: float

    class Config:
        from_attributes = True


# Meal Schemas
class MealCreate(BaseModel):
    user_id: int
    name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    date: date


class MealResponse(BaseModel):
    id: int
    user_id: int
    name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    date: date

    class Config:
        from_attributes = True


# ============================================
# API Endpoints
# ============================================


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Fitness Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "users": "/users",
            "workouts": "/workouts",
            "exercises": "/exercises",
            "meals": "/meals",
        },
    }


# ============================================
# USER ENDPOINTS
# ============================================


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users with pagination"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user and all associated data"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    db.delete(user)
    db.commit()
    return None




@app.post(
    "/workouts", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED
)
def create_workout(workout: WorkoutCreate, db: Session = Depends(get_db)):
    """Create a new workout"""
    # Verify user exists
    user = db.query(User).filter(User.id == workout.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_workout = Workout(**workout.model_dump())
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


@app.get("/workouts", response_model=List[WorkoutResponse])
def get_workouts(
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get all workouts, optionally filtered by user_id"""
    query = db.query(Workout)
    if user_id:
        query = query.filter(Workout.user_id == user_id)
    workouts = query.offset(skip).limit(limit).all()
    return workouts


@app.get("/workouts/{workout_id}", response_model=WorkoutResponse)
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    """Get a specific workout by ID"""
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found"
        )
    return workout


@app.patch("/workouts/{workout_id}", response_model=WorkoutResponse)
def update_workout(
    workout_id: int, workout_update: WorkoutUpdate, db: Session = Depends(get_db)
):
    """Update a workout"""
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found"
        )

    # Update only provided fields
    update_data = workout_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(workout, key, value)

    db.commit()
    db.refresh(workout)
    return workout


@app.delete("/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    """Delete a workout and all associated exercises"""
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found"
        )
    db.delete(workout)
    db.commit()
    return None


# ============================================
# EXERCISE ENDPOINTS
# ============================================


@app.post(
    "/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED
)
def create_exercise(exercise: ExerciseCreate, db: Session = Depends(get_db)):
    """Create a new exercise"""
    # Verify workout exists
    workout = db.query(Workout).filter(Workout.id == exercise.workout_id).first()
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found"
        )

    db_exercise = Exercise(**exercise.model_dump())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


@app.get("/exercises", response_model=List[ExerciseResponse])
def get_exercises(
    workout_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get all exercises, optionally filtered by workout_id"""
    query = db.query(Exercise)
    if workout_id:
        query = query.filter(Exercise.workout_id == workout_id)
    exercises = query.offset(skip).limit(limit).all()
    return exercises


@app.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    """Delete an exercise"""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found"
        )
    db.delete(exercise)
    db.commit()
    return None


# ============================================
# MEAL ENDPOINTS
# ============================================


@app.post("/meals", response_model=MealResponse, status_code=status.HTTP_201_CREATED)
def create_meal(meal: MealCreate, db: Session = Depends(get_db)):
    """Create a new meal"""
    # Verify user exists
    user = db.query(User).filter(User.id == meal.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_meal = Meal(**meal.model_dump())
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


@app.get("/meals", response_model=List[MealResponse])
def get_meals(
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get all meals, optionally filtered by user_id"""
    query = db.query(Meal)
    if user_id:
        query = query.filter(Meal.user_id == user_id)
    meals = query.offset(skip).limit(limit).all()
    return meals


@app.get("/meals/{meal_id}", response_model=MealResponse)
def get_meal(meal_id: int, db: Session = Depends(get_db)):
    """Get a specific meal by ID"""
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found"
        )
    return meal


@app.delete("/meals/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    """Delete a meal"""
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found"
        )
    db.delete(meal)
    db.commit()
    return None


# ============================================
# Health Check
# ============================================


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
