# Forsit E-commerce Admin API

The Forsit E-commerce Admin API is a backend application built using FastAPI that serves as the foundation for a web admin dashboard for e-commerce managers. It provides detailed insights into sales, revenue, and inventory status, as well as allows new product registration. This README file provides essential information for setting up and using the API.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.11
- pip (Python package manager)
- SQLite (Relational database)

### Installation

1. Clone the repository to your local machine:<br>
        git clone https://github.com/mobeenaslam007/forsit-e-commerce/

2. Navigate to the project directory:<br>
       cd forsit-e-commerce
   
4. Create a virtual environment (optional but recommended):<br>
       python -m venv venv

5. Activate the virtual environment:<br>
       On Windows: venv\Scripts\activate<br>
       On Mac and linux: venv\Scripts\activate

6. Install the project dependencies:<br>
       pip install -r requirements.txt

7. Run this project using following commannd:<br>
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload


## API Endpoints

### Products

- **POST /products/**: Create a new product.
- **GET /products/{product_id}**: Retrieve product details by ID.
- **GET /products/**: Retrieve a list of all products.

### Sales

- **POST /sales/**: Record a new sale.
- **GET /sales/**: Retrieve sales data with filtering options (start_date, end_date, product_id, category_id).

### Inventory

- **PUT /inventory/{product_id}**: Update inventory levels for a product.
- **GET /inventory/{product_id}**: Retrieve inventory details for a specific product.
- **GET /inventory/**: Retrieve a list of all inventory items.

### Revenue Analysis

- **GET /revenue/**: Analyze revenue based on query parameters (start_date, end_date, product_id, category_id).

### Categories

- **POST /categories/**: Create a new product category.
- **GET /categories/{category_id}**: Retrieve category details by ID.
- **PUT /categories/{category_id}**: Update category details.
- **GET /categories/**: Retrieve a list of all product categories.

  
