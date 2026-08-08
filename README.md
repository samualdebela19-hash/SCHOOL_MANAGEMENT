# School Management System - Starter Project

A simple Role-Based School Management System built with **Python + Flask**.

## Features

- **Admin**: Full system overview, user list
- **Registrar**: Student registration, edit, delete, list
- **Attendance Controller**: Mark Present/Absent/Late, view records
- **Property Officer**: Inventory management, issue & return items

## Default Login Accounts

| Username    | Password  | Role              |
|-------------|-----------|-------------------|
| admin       | admin123  | Admin             |
| registrar   | reg123    | Registrar         |
| attendance  | att123    | Attendance        |
| property    | prop123   | Property Officer  |

## How to Run

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate        # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser:
   ```
   http://127.0.0.1:5000
   ```

The database (`school.db`) will be created automatically on first run with the default users.

## Project Structure

```
school_management/
├── app.py              # Main application + routes
├── config.py           # Configuration
├── models.py           # Database models
├── forms.py            # WTForms
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── admin/
│   ├── registrar/
│   ├── attendance/
│   └── property/
└── static/
```

## Tech Stack

- Python 3.10+
- Flask 3
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Bootstrap 5
- SQLite (default)

## Next Steps You Can Add

- Fee management module
- Exam & report cards
- Parent notifications (SMS/Email)
- Better search & filters
- Export to Excel/PDF
- Mobile responsive improvements
- Change default passwords in production!

---
Built as a starter project for school management system.
