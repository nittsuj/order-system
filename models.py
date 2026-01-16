from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

products_orders = Table (
    "products_orders",
    Base.metadata,
    Column("products_id",
           ForeignKey("products.id"),
           primary_key=True),
    Column("orders_id",
           ForeignKey("orders.id"),
           primary_key=True),
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, 
                primary_key=True, 
                index=True)
    username = Column(String(50), 
                      unique=True, 
                      nullable=False)
    email = Column(String(254), 
                   unique=True, 
                   nullable=False)

    orders = relationship("Order",
                          back_populates="user")
    
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True)
    price = Column(Integer)
    stock = Column(Integer)
    
    orders = relationship("Order", 
                          secondary=products_orders,
                          back_populates="products")

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, 
                primary_key=True,
                index=True)
    status = Column(String(50),
                    default="pending",
                    nullable=False)

    users_id = Column(Integer, 
                      ForeignKey("users.id"),
                      nullable=False)
    
    user = relationship("User",
                         back_populates="orders")
    products = relationship("Product",
                            secondary=products_orders,
                            back_populates="orders")
