# Ecommerce Shopping App Backend

Welcome to the Ecommerce Shopping App Backend! This project provides the backend functionality for an Ecommerce Shopping App, including user management, product management, order processing, and more.

## Features

- **Admin Dashboard**: Secure admin login, manage order status, view order history.
- **User Management**: Register new users, user login, manage user profiles.
- **Product Management**: Add, update, and delete products, manage product inventory.
- **Shopping Cart Processing**: Add items, update quantity, remove items, get items, calculate total prices.
- **Order Processing**: Complete purchase, get-order.
- **API Documentation**: Detailed documentation of API endpoints for easy integration with frontend or external systems.

## Technologies Used

- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.7+.
- **MongoDB**: A NoSQL document database for storing user data, product information, and order details.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **Cloudinary**: Cloud-based image and video management platform for storing and serving product images.
- **bcrypt**: Password hashing library for securing user passwords.

## Getting Started

1. **Clone the repository:**

   ```bash
   git clone https://github.com/anurag-b72/ecommerce-shopping-backend.git

1. **Create virtual environment:**

   ```bash
   cd ecommerce-shopping-backend
   python -m venv venv
1. **Open virtual environment:**

   ```bash
   .\venv\Scripts\activate
1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
1. **Run the application:**

   ```bash
   uvicorn main:app --reload
1. **To close application and virtual environment:**

   Press `CTRL/CMD + C`
   ```bash
   deactivate
