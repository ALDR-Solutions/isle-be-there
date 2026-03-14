"""
SQLAlchemy models for the application.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    is_active = Column(Boolean, default=True)
    is_business = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    listings = relationship("Listing", back_populates="owner")
    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("Review", back_populates="user")


class Listing(Base):
    """Listing model for business/hotel listings."""
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    address = Column(String(500))
    city = Column(String(100))
    country = Column(String(100))
    price_per_night = Column(Float)
    capacity = Column(Integer)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    amenities = Column(Text)  # JSON string
    images = relationship("Image", back_populates="listing")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="listings")
    bookings = relationship("Booking", back_populates="listing")
    reviews = relationship("Review", back_populates="listing")


class Booking(Base):
    """Booking model for reservations."""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)
    total_price = Column(Float)
    status = Column(String(50), default="pending")  # pending, confirmed, cancelled, completed
    special_requests = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    listing_id = Column(Integer, ForeignKey("listings.id"))
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    listing = relationship("Listing", back_populates="bookings")


class Review(Base):
    """Review model for listings."""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    listing_id = Column(Integer, ForeignKey("listings.id"))
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    listing = relationship("Listing", back_populates="reviews")


class Image(Base):
    """Image model for listing images."""
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False)
    caption = Column(String(200))
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    listing_id = Column(Integer, ForeignKey("listings.id"))
    
    # Relationships
    listing = relationship("Listing", back_populates="images")
