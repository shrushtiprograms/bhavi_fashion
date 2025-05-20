Bhavi India Fashion 🛍️

Bhavi India Fashion is a full-stack web application developed using Django and MySQL that provides a platform for customers to explore, order, and manage ethnic and contemporary fashion products. It includes a robust admin panel for managing inventory, orders, users, and reporting.
🌐 Tech Stack

    Backend: Python, Django

    Frontend: HTML, CSS, JavaScript

    Database: MySQL

🔑 Key Features

    User authentication and registration

    Admin dashboard for managing products and orders

    Category-wise product listings

    Bulk order and custom design request modules

    Contact form and log management

    SQL backup and restore support

📁 Project Structure

    accounts/ – User login, registration, profile

    admin_dashboard/ – Admin control panel

    bulk_orders/, custom_designs/ – Specialized modules

    logs/, orders/, products/ – Business logic & data models

    report_manager/ – Export and report generation

    static/, templates/ – Frontend files

    db.sqlite3, backup.sql – Database and backup

🚀 Getting Started

    Clone the repository:

    git clone https://github.com/shrushtiprograms/bhavi_fashion.git

    Create a virtual environment and activate it:

    python -m venv venv
    venv\Scripts\activate (on Windows)

    Install dependencies:

    pip install -r requirements.txt

    Run migrations and start the server:

    python manage.py migrate
    python manage.py runserver

    Access the app at http://localhost:8000/

📦 Database

To restore the sample database:

    Use backup.sql in phpMyAdmin or run via MySQL CLI:
    mysql -u root -p bhavi_db < backup.sql

📜 License

This project is for educational and portfolio purposes.
