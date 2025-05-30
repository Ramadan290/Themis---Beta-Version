# Themis – Beta Version

**Themis** is a Human Resource Management System (HRMS) that combines secure authentication, employee management, and AI-driven analytics to help organizations manage their teams effectively.  
This repository represents the **Beta Version**, designed as the first functional release before a planned upgrade with deeper AI integration and structured SQL-backed storage.

> ⚠️ A **refined version** is coming soon and will feature:
> - More advanced **deep learning models**.
> - Migration from MongoDB to a **relational SQL database**.
> - Cleaner **controller-based backend structure**.
> - A complete **frontend redesign** using React or similar frameworks.

---

## 🚀 Features

### 🔐 Authentication & Role Management
- Secure login using **JWT tokens** (access & refresh).
- Password hashing via **bcrypt**.
- Role-based access control (`employee`, `hr`, etc.).

### 🧾 Payroll Module
- View and update salary, appraisals, penalties, and benefits.
- Submit and manage **raise requests** (auto-approved or reviewed by HR).
- HR-exclusive payroll filtering, editing, and raise approvals.

### 🕒 Attendance Module
- Log attendance manually or programmatically.
- Upload **sick notes with file attachments**.
- HR review system for sick notes (accept/reject with comments).
- Full attendance filtering system with date/status-based queries.

### 📰 Internal News System
- Employees can view and comment on internal news.
- HR can create, edit, and delete news or specific comments.

### 📊 Status & Performance Overview
- Employee profile tracks:
  - Completion rates
  - Project contributions
  - Interaction metrics
  - Workload handling
- Integrated with payroll and attendance for unified reporting.

### 🧠 AI Models – Beta Version
All models are trained using real-time API data fetched from MongoDB collections.

#### 1. **Well-Being Prediction**
- Classifies employees as `Good`, `Neutral`, or `At Risk`.
- Features: attendance patterns, salary, penalties, workload, and engagement metrics.
- Trained with: `RandomForestClassifier`.

#### 2. **BCR (Benefit-Cost Ratio) Estimation**
- Calculates benefit-to-cost performance for employees.
- Features include appraisals, penalties, completion rate, and salary.
- Trained with: `RandomForestRegressor`.

#### 3. **Department Fit Prediction (Decentralization Model)**
- Predicts which department suits an employee based on their skills, experience, and performance.
- Supports future decentralization of organizational structures.
- Trained with: `RandomForestClassifier`.

---

## 🧱 Tech Stack

| Layer       | Stack                        |
|-------------|------------------------------|
| **Backend** | FastAPI (Python)             |
| **Database**| MongoDB                      |
| **AI/ML**   | scikit-learn, joblib, pandas |
| **Frontend**| HTML, CSS, JavaScript        |
| **Security**| OAuth2 + JWT + bcrypt        |

---

## 📁 Project Structure
themis/
├── app/
│ ├── main.py # FastAPI initialization
│ ├── auth.py # JWT and password logic
│ ├── config.py # MongoDB setup
│ ├── models.py # Pydantic schemas
│ ├── routes/
│ │ ├── authorization.py # Login, register, token refresh
│ │ ├── attendance.py # Attendance CRUD + HR tools
│ │ ├── payroll.py # Payroll CRUD + HR tools
│ │ ├── news.py # News posting + comments
│ │ ├── status.py # Employee analytics & HR overview
│ │ └── classification_input.py # AI predictions
├── ML/
│ ├── BCR.py # Trains BCR model
│ ├── DEC.py # Trains decentralization model
│ ├── WELL_BEING.py # Trains well-being model
├── frontend/
│ ├── index.html # Landing page
│ ├── login/ # Login UI
│ ├── css/ # Stylesheets
│ ├── js/ # Frontend logic
├── uploads/ # Sick note files
├── .env # MongoDB URI and secret keys


---

## ▶️ How to Run Locally

### ✅ Prerequisites
- Python 3.10+
- Node.js (optional if expanding frontend)
- MongoDB running locally or hosted (URI in `.env`)
- Create `.env` file with:

- 
### 🚀 Run Backend
```bash
cd themis
uvicorn app.main:app --reload


http://127.0.0.1:8000/


🧪 Notes
This beta release uses machine learning models only — deep learning will be used in the refined release.

MongoDB is used for all collections, including: users, attendance, payroll, news, status, and skills.



