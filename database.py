from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config

# Create a database engine
engine = create_engine(Config.DATABASE_URL)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# For initial setup:
def create_db_and_tables():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    print("Creating database tables...")
    create_db_and_tables()
    print("Tables created.")