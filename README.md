# E-commerce Admin API

The E-commerce Admin API is a backend application built using FastAPI that serves as the foundation for a web admin dashboard for e-commerce managers. It provides detailed insights into sales, revenue, and inventory status, as well as allows new product registration. This README file provides essential information for setting up and using the API.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.11
- pip (Python package manager)
- SQLite (Relational database)

### Installation

1. Clone the repository to your local machine:
    git clone https://github.com/mobeenaslam007/forsit-e-commerce/

2. Navigate to the project directory:
   cd forsit-e-commerce
   
4. Create a virtual environment (optional but recommended):
   python -m venv venv

5. Activate the virtual environment:
   On Windows: venv\Scripts\activate
   On Mac and linux: venv\Scripts\activate

6. Install the project dependencies:
   pip install -r requirements.txt

7. Run this project using following commannd:
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  
