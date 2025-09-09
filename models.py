from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False) # Add length
    category = Column(String(50), index=True, nullable=False) # Add length
    brand = Column(String(100), nullable=False) # Add length
    model = Column(String(255), nullable=False) # Add length
    specs = Column(JSON, nullable=False, default={}) # JSON doesn't need length
    image_url = Column(String(500)) # Add length
    gaming_score = Column(Integer, default=0)
    productivity_score = Column(Integer, default=0)
    aesthetic_tags = Column(String(255)) # Add length - Comma-separated tags

    prices = relationship("PriceEntry", back_populates="product")
    build_parts = relationship("BuildPart", back_populates="product")

    def __repr__(self):
        return f"<Product(name='{self.name}', category='{self.category}')>"

class PriceEntry(Base):
    __tablename__ = "price_entries"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    retailer_name = Column(String(100), nullable=False) # Add length
    retailer_url = Column(String(500), nullable=False) # Add length
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="prices")

    def __repr__(self):
        return f"<PriceEntry(product_id={self.product_id}, retailer='{self.retailer_name}', price={self.price})>"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100)) # Add length
    email = Column(String(255), unique=True, index=True, nullable=False) # Add length
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    saved_builds = relationship("SavedBuild", back_populates="user")

class SavedBuild(Base):
    __tablename__ = "saved_builds"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_preferences = Column(JSON, nullable=False) # JSON doesn't need length
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notified_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="saved_builds")
    parts = relationship("BuildPart", back_populates="saved_build")

class BuildPart(Base):
    __tablename__ = "build_parts"
    id = Column(Integer, primary_key=True, index=True)
    saved_build_id = Column(Integer, ForeignKey("saved_builds.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    recommended_price = Column(Float, nullable=False)
    current_price = Column(Float)
    lowest_price_retailer = Column(String(100)) # Add length
    lowest_price_url = Column(String(500)) # Add length

    saved_build = relationship("SavedBuild", back_populates="parts")
    product = relationship("Product", back_populates="build_parts")