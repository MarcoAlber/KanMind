<h1 align="center">KanMind</h1>

<p align="center">
  <em>KanMind is a backend application built with Django and Django REST Framework (DRF).  
  It provides a RESTful API for a Kanban-style task management system.  
  Users can register, log in, and manage their own boards and tasks in an isolated environment.</em>
  <br>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.13.2-blue?logo=python&logoColor=white" alt="Python version"></a>
  <a href="https://www.djangoproject.com/"><img src="https://img.shields.io/badge/Django-5.2.7-success?logo=django&logoColor=white" alt="Django version"></a>
  <a href="https://www.django-rest-framework.org/"><img src="https://img.shields.io/badge/DRF-3.16.1-red?logo=django&logoColor=white" alt="DRF version"></a>
</p>

<hr>

## 🔧 Features

- User registration and authentication  
- JWT-based login system (if applicable)  
- Create and manage personal Kanban boards  
- Add, update, and delete tasks  
- Comment on tasks  
- User-specific access: users can only access their own boards and data  

---

## 🚀 Tech Stack

- **Python** 3.13.2  
- **Django** 5.2.7  
- **Django REST Framework (DRF)**  
- **SQLite** (for development)  
- **CORS support** (via `django-cors-headers`)  
- **Nested routing** for clean API structure  

---

## 📁 Project Structure

```text
kanmind/
├── user_auth_app/
├── kanban_app/
├── core/                  # API routing (combines app-level endpoints)
├── manage.py
└── db.sqlite3
```

---

## 📦 Installation

1. **Clone the repository**
```bash
git clone git@github.com:MarcoAlber/KanMind.git .

2. **Create a virtual environment and activate it**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

3. **Install dependencies**
```bash
  pip install -r requirements.txt

4. **Apply migrations**
```bash
python manage.py migrate

5. **Run the development server**

```bash
python manage.py runserver

---

## 🔑 API Endpoints

- Authentication
| Method | Endpoint             | Description                            |
| ------ | -------------------- | -------------------------------------- |
| POST   | `/api/registration/` | Register a new user                    |
| POST   | `/api/login/`        | Log in to receive authentication token |


- Boards
| Method | Endpoint                  | Description                               |
| ------ | ------------------------- | ----------------------------------------- |
| GET    | `/api/boards/`            | List all boards of the authenticated user |
| POST   | `/api/boards/`            | Create a new board                        |
| GET    | `/api/boards/{board_id}/` | Retrieve details of a specific board      |
| PATCH  | `/api/boards/{board_id}/` | Update a board                            |
| DELETE | `/api/boards/{board_id}/` | Delete a board                            |
| GET    | `/api/email-check/`       | Check if an email is already registered   |


- Tasks
| Method | Endpoint                                      | Description                                   |
| ------ | --------------------------------------------- | --------------------------------------------- |
| GET    | `/api/tasks/assigned-to-me/`                  | List tasks assigned to the authenticated user |
| GET    | `/api/tasks/reviewing/`                       | List tasks the user is reviewing              |
| POST   | `/api/tasks/`                                 | Create a new task                             |
| PATCH  | `/api/tasks/{task_id}/`                       | Update a task                                 |
| DELETE | `/api/tasks/{task_id}/`                       | Delete a task                                 |
| GET    | `/api/tasks/{task_id}/comments/`              | List comments on a task                       |
| POST   | `/api/tasks/{task_id}/comments/`              | Add a comment to a task                       |
| DELETE | `/api/tasks/{task_id}/comments/{comment_id}/` | Delete a comment                              |


---

## 🥪 Testing (optional)
If you have tests in place, run:

python manage.py test


---

## ⚙️ Requirements
ini
Code kopieren
asgiref==3.10.0
Django==5.2.7
django-cors-headers==4.9.0
djangorestframework==3.16.1
drf-nested-routers==0.95.0
sqlparse==0.5.3
tzdata==2025.2

---

## 📌 Notes
The app uses SQLite for development.
For production, switch to PostgreSQL or another robust DB.

All users can only see and manage their own data.

CORS is enabled, allowing frontend apps (e.g. React) to communicate with the backend.

---

## 📨 Contact
For any questions or contributions, feel free to reach out or open an issue.
