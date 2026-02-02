"""
Database configuration for the Todo API.

This module sets up the SQLAlchemy database engine, session, and base class.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable, with a default for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo.db")

# Create the database engine
# For SQLite, we need to add connect_args={"check_same_thread": False} for multiple thread access
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for declarative models
Base = declarative_base()