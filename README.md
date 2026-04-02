# 🚀 CampusHub: College Event Management System

CampusHub is a full-stack event management platform built for students, club organizers, and administrators. It handles everything from registration and attendance to logistical planning and administrative approval.

---

## 🛠️ Project Stack
- **Backend:** Python (Flask), PyJWT, Flask-Limiter, PostgreSQL
- **Frontend:** Vanilla JS, HTML, Tailwind CSS (CDN)
- **Security:** Layered Token Strategy (Access/Refresh), Fingerprinting, CSRF-proof HTTP-only Cookies

---

## 📦 Local Setup Instructions

Follow these steps to get the project running on your own machine.

### 1. Prerequisites
Ensure you have the following installed:
- **Python 3.14+** (Earlier versions may work but the `venv` is built on 3.14)
- **PostgreSQL Database**:
  - Install PostgreSQL locally or use Docker.
  - Create a master database named `cems`.
  - Update the credentials (user/password) in `backend/db.py` to match your local setup.
- **Git** for version control.

### 2. Clone the Repository
```bash
git clone https://github.com/veera-crt/CEMS_SEPM.git
cd CEMS_SEPM
```

---

## 🔧 Detailed Environment Configuration

### Automatic macOS Setup (Recommended)
If you are on a Mac, we have pre-configured a high-performance virtual environment for you. Simply activate it:
```bash
source venv/bin/activate
```

### Manual Cross-Platform Setup (Windows/Linux)
If the pre-built `venv` is incompatible with your system architecture, rebuild it from the source:
```bash
# 1. Clean old environment
rm -rf venv

# 2. Re-create and Activate
python3 -m venv venv
source venv/bin/activate  # (On Windows use: .\venv\Scripts\activate)

# 3. Synchronize Dependencies
cd backend
pip install -r requirements.txt
```

---

## 🗄️ Database Initialization & Orchestration

We have unified all database logic into a single orchestration script. **You only need to run one command** to build the entire system from scratch.

### 1. Configure Connection
Before running the code, open `backend/db.py` and ensure the `DB_PARAMS` match your PostgreSQL password and username.

### 2. Build the System
Execute the master creation script from the **backend directory**:
```bash
cd backend
python3 database_creation.py
```

**What this script does for you:**
*   **Schema Build**: Creates all 9 core tables (Users, Clubs, Halls, Events, etc.) with strict Foreign Key constraints.
*   **Security Layer**: Initializes the Refresh Token rotation and Blacklist tables.
*   **Seed Data**: Pre-loads **40+ College Clubs** and the **Campus Hall Inventory**.
*   **Automation Triggers**: Installs the `set_event_club_id` trigger directly into your Postgres engine for automatic data linkage.

### 3. Verify
You can verify the tables by running `\dt` in your psql terminal. You should see 9 tables registered.

---

### 5. Setup Environment Variables
Create a `.env` file in the **root directory** and add the following keys. 
*(Note: You can use `openssl rand -hex 64` to generate keys)*

```env
JWT_SECRET=your_new_long_random_string_here
CRYPTO_KEY=your_encryption_key_for_pii
MAIL_USERNAME="youremail@gmail.com"
MAIL_PASSWORD="your-app-specific-google-password"
```

### 7. Run the Application
Start the Flask development server:
```bash
cd backend
python3 app.py
```
The server will start on **`http://127.0.0.1:5005`**. 

---

## 🔐 Key Security Features implemented
- **Auto-Rotation**: Refresh tokens rotate on every use to prevent replay attacks.
- **Fingerprinting**: Identity is bound to the User-Agent and IP to prevent token theft.
- **Rate Limiting**: Login endpoints are protected against brute-force.
- **HTTP-only Cookies**: JS cannot access session tokens, stopping XSS-based theft.

---

## 👥 Contributors
- Dev Team (Collaboration)
