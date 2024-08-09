from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Marriage MatchMaking API!"}

@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    db_user = models.User(
        name=user.name,
        age=user.age,
        gender=user.gender,
        email=user.email,
        city=user.city
    )
    db_user.set_interests(user.interests)  # Convert list to comma-separated string
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    for user in users:
        user.interests = user.get_interests()  # Convert comma-separated string to list
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.interests = user.get_interests()  # Convert comma-separated string to list
    return user

@app.put("/users/{user_id}", response_model=schemas.User)                                 # Added new endpoint.
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = user.dict(exclude_unset=True)
    if "interests" in update_data:
        update_data["interests"] = ",".join(update_data["interests"])

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    db_user.interests = db_user.get_interests()  # Convert comma-separated string to list
    return db_user

@app.delete("/users/{user_id}", response_model=schemas.User)  # Added new endpoint.
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(db_user)
    db.commit()
    return db_user

@app.get("/users/{user_id}/matches/", response_model=list[schemas.User])  # Added new endpoint.
def find_matches(user_id: int, db: Session = Depends(get_db)):
    # Fetch the user based on the provided user_id
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user_interests = set(user.get_interests())  # Convert comma-separated string to list
    
    matched_users = []
    
    for potential_match in db.query(models.User).filter(models.User.id != user_id).all():
        potential_match_interests = set(potential_match.get_interests())  # Convert comma-separated string to list
        
        if user_interests.intersection(potential_match_interests):
            potential_match.interests = potential_match.get_interests()  # Convert to list
            matched_users.append(potential_match)
    
    return matched_users

