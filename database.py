import os
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

class Investor(Base):
    """Model for storing investor information"""
    __tablename__ = "investors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    location = Column(String)
    investments = Column(Integer)
    profile_url = Column(String)
    investment_stages = Column(JSON)  # Stored as JSON array
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database connection manager
class Database:
    def __init__(self):
        self.SessionLocal = SessionLocal

    def get_session(self):
        """Get a database session"""
        db = self.SessionLocal()
        try:
            return db
        except Exception as e:
            logger.error(f"Error creating database session: {str(e)}")
            db.close()
            raise

    def init_db(self):
        """Initialize database tables"""
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise

# Create database tables
db = Database()
db.init_db()
