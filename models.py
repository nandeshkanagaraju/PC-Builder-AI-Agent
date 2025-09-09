from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False) # e.g., CPU, GPU, RAM, Motherboard, Monitor
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    specs = Column(JSON, nullable=False, default={}) # Store detailed specs as JSON
    image_url = Column(String)
    # Add a simple score for recommendation logic (e.g., gaming_score, productivity_score)
    gaming_score = Column(Integer, default=0)
    productivity_score = Column(Integer, default=0)
    aesthetic_tags = Column(String) # Comma-separated tags: RGB, Minimalist, White

    prices = relationship("PriceEntry", back_populates="product")
    build_parts = relationship("BuildPart", back_populates="product")

    def __repr__(self):
        return f"<Product(name='{self.name}', category='{self.category}')>"

class PriceEntry(Base):
    __tablename__ = "price_entries"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    retailer_name = Column(String, nullable=False)
    retailer_url = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="prices")

    def __repr__(self):
        return f"<PriceEntry(product_id={self.product_id}, retailer='{self.retailer_name}', price={self.price})>"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    saved_builds = relationship("SavedBuild", back_populates="user")

class SavedBuild(Base):
    __tablename__ = "saved_builds"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_preferences = Column(JSON, nullable=False) # Store original user query/preferences
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notified_at = Column(DateTime(timezone=True)) # Timestamp of last price drop notification

    user = relationship("User", back_populates="saved_builds")
    parts = relationship("BuildPart", back_populates="saved_build")

class BuildPart(Base):
    __tablename__ = "build_parts"
    id = Column(Integer, primary_key=True, index=True)
    saved_build_id = Column(Integer, ForeignKey("saved_builds.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    recommended_price = Column(Float, nullable=False) # Price at the time of recommendation
    current_price = Column(Float) # Current lowest price if updated
    lowest_price_retailer = Column(String)
    lowest_price_url = Column(String)

    saved_build = relationship("SavedBuild", back_populates="parts")
    product = relationship("Product", back_populates="build_parts")