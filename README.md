# Bhavi India Fashion 🛍️

Bhavi India Fashion is a full-stack web application developed using Django and MySQL that provides a platform for customers to explore, order, and manage ethnic and contemporary fashion products. It includes a robust admin panel for managing inventory, orders, users, and reporting.

---

## 🌐 Tech Stack

- 🐍 Backend: Python, Django  
- 🌐 Frontend: HTML, CSS, JavaScript  
- 🛢️ Database: MySQL

---

## 🔑 Key Features

- ✅ User authentication and registration  
- 🛒 Admin dashboard for managing products and orders  
- 🗂️ Category-wise product listings  
- 📦 Bulk order and custom design request modules  
- 📬 Contact form and log management  
- 💾 SQL backup and restore support

---

## 📁 Project Structure

- `accounts/` – User login, registration, profile  
- `admin_dashboard/` – Admin control panel  
- `bulk_orders/`, `custom_designs/` – Specialized modules  
- `logs/`, `orders/`, `products/` – Business logic & data models  
- `report_manager/` – Export and report generation  
- `static/`, `templates/` – Frontend files  
- `db.sqlite3`, `backup.sql` – Database and backup

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/shrushtiprograms/bhavi_fashion.git

# Create a virtual environment
python -m venv venv

# Activate the environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and start the server
python manage.py migrate
python manage.py runserver
Visit your site at: [http://localhost:8000/](http://localhost:8000/)

---

## 🗄️ Database

To restore the sample database:

- Use phpMyAdmin to import `backup.sql`,  
  or  
- Run the following in MySQL CLI:

```bash
mysql -u root -p bhavi_db < backup.sql
---
## 📄 License

This project is for educational and portfolio purposes only.

📌 After that, you can add the following instructions to help others use the README:

```markdown
---

## 📌 How to Add This README

1. Go to your GitHub repository.
2. Click on "Add file" → "Create new file".
3. Name the file: `README.md`
4. Paste all the code you just copied.
5. Scroll down and click "Commit new file".

Your README will now appear on the homepage of your GitHub repository.
