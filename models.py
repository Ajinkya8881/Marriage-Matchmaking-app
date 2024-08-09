from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    email = Column(String, unique=True, index=True)
    city = Column(String)
    interests = Column(String)  # Store as comma-separated string

    def get_interests(self):
        return self.interests.split(",") if self.interests else []

    def set_interests(self, interests_list):
        self.interests = ",".join(interests_list) if interests_list else ""
