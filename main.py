from fastapi import FastAPI, Depends, HTTPException, Query, Path, Body
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import Session, sessionmaker, relationship
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

# Create a FastAPI application
app = FastAPI()

# Define the database connection URL (replace with your actual database URL)
DATABASE_URL = "sqlite:///./forsit.db"

# Create a database engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the base model for SQLAlchemy
Base = declarative_base()

# Define Pydantic models

# Pydantic models for Product
class ProductBase(BaseModel):
    name: str
    description: str
    price: float

class ProductCreate(ProductBase):
    category_id: int

class ProductResponse(ProductBase):
    id: int

# Pydantic models for Sale
class SaleBase(BaseModel):
    product_id: int
    quantity: int
    revenue: float

class SaleCreate(SaleBase):
    category_id: int

class SaleResponse(SaleBase):
    id: int
    sale_date: datetime

# Pydantic models for Inventory
class InventoryBase(BaseModel):
    product_id: int
    stock_quantity: int

class InventoryCreate(InventoryBase):
    category_id: int

class InventoryResponse(InventoryBase):
    id: int
    last_updated: datetime

# Pydantic models for Revenue Analysis
class RevenueQueryParams(BaseModel):
    start_date: datetime
    end_date: datetime
    product_id: Optional[int] = None
    category_id: Optional[int] = None

class RevenueAnalysis(BaseModel):
    period: str
    revenue: float

# Pydantic models for Category
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

# Define database models for Product, Sale, Inventory, and Category

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    revenue = Column(Float)
    sale_date = Column(DateTime, default=func.now())
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="sales")

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    stock_quantity = Column(Integer)
    last_updated = Column(DateTime, default=func.now())
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="inventory")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    products = relationship("Product", back_populates="category")
    sales = relationship("Sale", back_populates="category")
    inventory = relationship("Inventory", back_populates="category")

# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Example request bodies

example_product = {
    "name": "Example Product",
    "description": "This is an example product.",
    "price": 19.99,
    "category_id": 1
}

example_sale = {
    "product_id": 1,
    "quantity": 5,
    "revenue": 99.95,
    "category_id": 1
}

example_inventory_update_body = {
    "stock_quantity": 50,
    "category_id": 1
}

# Product Endpoints

# Create a product
@app.post("/products/", response_model=ProductResponse)
def create_product(
    product: ProductCreate = Body(example_product, title="Product Data"),
    db: Session = Depends(get_db)
):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Retrieve a product by ID
@app.get("/products/{product_id}", response_model=ProductResponse)
def read_product(
    product_id: int = Path(..., title="The ID of the product to retrieve"),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Retrieve all products
@app.get("/products/", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

# Sale Endpoints

# Create a sale
@app.post("/sales/", response_model=SaleResponse)
def create_sale(
    sale: SaleCreate = Body(example_sale, title="Sale Data"),
    db: Session = Depends(get_db)
):
    db_sale = Sale(**sale.dict())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

# Retrieve sales data based on query parameters
@app.get("/sales/", response_model=List[SaleResponse])
def get_sales(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    sales_query = db.query(Sale)
    
    if start_date:
        sales_query = sales_query.filter(Sale.sale_date >= start_date)
    if end_date:
        sales_query = sales_query.filter(Sale.sale_date <= end_date)
    if product_id:
        sales_query = sales_query.filter(Sale.product_id == product_id)
    if category_id:
        sales_query = sales_query.filter(Sale.category_id == category_id)
    
    sales = sales_query.all()
    
    return sales

# Revenue Endpoints

# Calculate revenue for a given period
def calculate_revenue_for_period(db: Session, params: RevenueQueryParams):
    revenue = 0.0
    
    sales_query = db.query(Sale).filter(Sale.sale_date >= params.start_date, Sale.sale_date <= params.end_date)
    
    if params.product_id:
        sales_query = sales_query.filter(Sale.product_id == params.product_id)
    
    if params.category_id:
        sales_query = sales_query.filter(Sale.category_id == params.category_id)
    
    sales = sales_query.all()
    
    for sale in sales:
        revenue += sale.revenue
    
    return revenue

# Retrieve revenue analysis based on query parameters
@app.get("/revenue/", response_model=List[RevenueAnalysis])
def revenue_analysis(
    start_date: datetime = Query(..., description="Start date for revenue analysis"),
    end_date: datetime = Query(..., description="End date for revenue analysis"),
    product_id: Optional[int] = Query(None, description="Product ID for filtering"),
    category_id: Optional[int] = Query(None, description="Category ID for filtering"),
    db: Session = Depends(get_db)
):
    revenue_data = []

    # Calculate daily, weekly, monthly, and annual revenue
    for period in ["daily", "weekly", "monthly", "annual"]:
        if period == "daily":
            revenue = calculate_revenue_for_period(db, RevenueQueryParams(start_date=start_date, end_date=end_date, product_id=product_id, category_id=category_id))
        elif period == "weekly":
            end_date = start_date + timedelta(days=6)
            revenue = calculate_revenue_for_period(db, RevenueQueryParams(start_date=start_date, end_date=end_date, product_id=product_id, category_id=category_id))
        elif period == "monthly":
            end_date = start_date.replace(day=1, month=start_date.month + 1) - timedelta(days=1)
            revenue = calculate_revenue_for_period(db, RevenueQueryParams(start_date=start_date, end_date=end_date, product_id=product_id, category_id=category_id))
        elif period == "annual":
            end_date = start_date.replace(month=1, day=1, year=start_date.year + 1) - timedelta(days=1)
            revenue = calculate_revenue_for_period(db, RevenueQueryParams(start_date=start_date, end_date=end_date, product_id=product_id, category_id=category_id))

        revenue_data.append(RevenueAnalysis(period=period, revenue=revenue))

    return revenue_data

# Inventory Endpoints

# Update inventory levels for a product
@app.put("/inventory/{product_id}", response_model=InventoryResponse)
def update_inventory(
    product_id: int = Path(..., title="The ID of the product to update inventory for"),
    stock_quantity: int = Body(example_inventory_update_body, title="Inventory Update Data"),
    db: Session = Depends(get_db)
):
    # Validate stock_quantity is a positive integer
    if not isinstance(stock_quantity, int) or stock_quantity <= 0:
        raise HTTPException(status_code=400, detail="stock_quantity should be a positive integer")

    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    inventory.stock_quantity = stock_quantity
    inventory.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(inventory)
    
    return inventory

# Retrieve all inventory items
@app.get("/inventory/", response_model=List[InventoryResponse])
def get_all_inventory_items(db: Session = Depends(get_db)):
    inventory_items = db.query(Inventory).all()
    return inventory_items

# Retrieve inventory of a specific product by ID
@app.get("/inventory/{product_id}", response_model=InventoryResponse)
def get_inventory_by_product_id(
    product_id: int = Path(..., title="The ID of the product to retrieve inventory for"),
    db: Session = Depends(get_db)
):
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found for this product")
    return inventory


# Category Endpoints

# Create a category
@app.post("/categories/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate = Body(..., title="Category Data"),
    db: Session = Depends(get_db)
):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# Retrieve a category by ID
@app.get("/categories/{category_id}", response_model=CategoryResponse)
def read_category(
    category_id: int = Path(..., title="The ID of the category to retrieve"),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

# Update a category
@app.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int = Path(..., title="The ID of the category to update"),
    category: CategoryCreate = Body(..., title="Category Data"),
    db: Session = Depends(get_db)
):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in category.dict().items():
        setattr(db_category, key, value)

    db.commit()
    db.refresh(db_category)
    return db_category

# Retrieve all categories
@app.get("/categories/", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
