from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Account(db.Model):
    __tablename__ = 'accounts'
    accounts_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String, nullable=False)

class ProductType(db.Model):
    __tablename__ = 'products_type'
    type_products_id = Column(Integer, primary_key=True, autoincrement=True)
    type_products = Column(String(50), nullable=False, unique=True)

class Product(db.Model):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name_product = Column(String(255), nullable=False, unique=True)
    price = Column(DECIMAL(18,2), nullable=False)
    cost = Column(DECIMAL(18,2), nullable=False)
    type_product_id = Column(Integer, ForeignKey('products_type.type_products_id'), nullable=False)
    type_product = relationship('ProductType', back_populates='products')
    
class Customer(db.Model):
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name_customer = Column(String(50), nullable=False)
    phone = Column(String(10), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    product = relationship('Product', back_populates='customers')

class Review(db.Model):
    __tablename__ = 'reviews'
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    rate_star = Column(Integer, nullable=False)
    comment_reviews = Column(Text, nullable=False)
    total_like = Column(Integer)
    date_reviews = Column(DateTime, nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=False)
    product = relationship('Product', back_populates='reviews')
    customer = relationship('Customer', back_populates='reviews')

class Bought(db.Model):
    __tablename__ = 'bought'
    bought_id = Column(Integer, primary_key=True, autoincrement=True)
    isbought = Column(Boolean, nullable=False)
    date_bought = Column(DateTime)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=False)
    product = relationship('Product', back_populates='bought')
    customer = relationship('Customer', back_populates='bought')
