# Themis – Beta Version

**Themis** is a Human Resource Management System (HRMS) that combines secure authentication, employee management, and AI-driven analytics to help organizations manage their teams effectively.  
This repository represents the **Beta Version**, designed as the first functional release before a planned upgrade with deeper AI integration and structured SQL-backed storage

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

Preview :
<img width="947" alt="image" src="https://github.com/user-attachments/assets/91849619-ede9-4b68-99e4-da8116c2fd13" />
<img width="949" alt="image" src="https://github.com/user-attachments/assets/b6796233-ef9d-4151-8ad4-bb1a31599b83" />
<img width="947" alt="image" src="https://github.com/user-attachments/assets/3689813e-f155-45a1-9a8e-48bb4311e24b" />
<img width="947" alt="image" src="https://github.com/user-attachments/assets/657fcc2f-ab2f-4e20-b718-e0bcf7994e56" />
<img width="946" alt="image" src="https://github.com/user-attachments/assets/9283fd31-fbe2-4a78-ab0c-d4e3c4c79034" />
<img width="945" alt="image" src="https://github.com/user-attachments/assets/310b9a51-3434-4ed9-b8a6-50fc14e1fdc3" />
<img width="935" alt="image" src="https://github.com/user-attachments/assets/131a0466-6235-453a-a01c-104d0f03971f" />
<img width="948" alt="image" src="https://github.com/user-attachments/assets/a15b5888-e7b4-4a43-ba36-5034e1a51232" />
<img width="947" alt="image" src="https://github.com/user-attachments/assets/77ba1f42-0bd3-4990-8832-3e39e2ee2a66" />
<img width="946" alt="image" src="https://github.com/user-attachments/assets/bea51cfd-99b7-4624-82a5-9e3e003ee481" />
<img width="946" alt="image" src="https://github.com/user-attachments/assets/8730aaf2-119a-4792-bb83-155da48a29ca" />
<img width="944" alt="image" src="https://github.com/user-attachments/assets/ec1c7380-1243-42b3-9d3f-fe760185a4ec" />
<img width="944" alt="image" src="https://github.com/user-attachments/assets/e5e1caa9-c19c-437d-9bef-49c7a8b22db3" />

<img width="959" alt="image" src="https://github.com/user-attachments/assets/d6dad4b0-e814-4f74-9ef3-cd2bd94fb6ca" />

---

## ▶️ How to Run Locally

### ✅ Prerequisites
- Python 3.10+
- Node.js (optional if expanding frontend)
- MongoDB running locally or hosted (URI in `.env`)
- Create `.env` file with:

 
### 🚀 Run Backend
```bash
cd themis
uvicorn app.main:app --reload


http://127.0.0.1:8000/
---------------------------------------------------------------

### 🧪 Notes
 - This beta release uses machine learning models only — deep learning will be used in the refined release.

 - MongoDB is used for all collections, including: users, attendance, payroll, news, status, and skills.


