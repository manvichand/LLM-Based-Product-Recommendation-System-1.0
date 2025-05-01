from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    """
    SQLAlchemy model for product information.

    Columns:
        id (String): Product identifier
        name (String): Product name
        description (String): Product description
        category (String): Product category
        price (Float): Product price
        features (JSON): Additional metadata
    """
    __tablename__ = "products"
    id = Column(String, primary_key=True, index=True)  # Changed to String for StockCode
    name = Column(String, index=True)
    description = Column(String)
    category = Column(String)
    price = Column(Float)
    features = Column(JSON)

class User(Base):
    """
    SQLAlchemy model for users.

    Columns:
        id (Integer): Unique user ID
        username (String): Username (must be unique)
        hashed_password (String): Hashed user password
        preferences (JSON): User's preference profile
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    preferences = Column(JSON)

class Feedback(Base):
    """
    SQLAlchemy model for storing user feedback on products.

    Columns:
        id (Integer): Unique feedback ID
        user_id (Integer): ID of the user giving feedback
        product_id (String): ID of the product being reviewed
        rating (Float): Feedback rating (1 to 5)
        comment (String): Optional textual feedback
    """
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    product_id = Column(String)  # Changed to String to match Product.id
    rating = Column(Float)
    comment = Column(String)

