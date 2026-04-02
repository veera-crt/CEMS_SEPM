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
- **Python 3.14+**
- **PostgreSQL Database** (Create a database named `campushub` or change config in `backend/db.py`)
- **Git**

### 2. Clone the Repository
```bash
git clone <your-repository-url>
cd <folder-name>
```

### 3. Setup Virtual Environment
> [!IMPORTANT]
> The `venv/` folder in this repo is pre-configured for **macOS**. 
> - **Mac Users:** You can use the existing `venv/` directly.
> - **Windows/Linux Users:** Do NOT use the included `venv/`. Delete it and create your own.

**To create your own (Required for Windows/Linux):**
```bash
# Delete existing if any
rm -rf venv

# Create new environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Activate it (Windows)
.\venv\Scripts\activate
```

### 4. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 5. Setup Environment Variables
Create a `.env` file in the **root directory** and add the following keys. 
*(Note: You can use `openssl rand -hex 64` to generate keys)*

```env
JWT_SECRET=your_new_long_random_string_here
CRYPTO_KEY=your_encryption_key_for_pii
MAIL_USERNAME="youremail@gmail.com"
MAIL_PASSWORD="your-app-specific-google-password"
```

### 6. Initialize Database
Run the following command once to create the necessary tables and seed the initial data (Clubs list).

```bash
python3 database_creation.py
```

### 7. Run the Application
Start the Flask development server:

```bash
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
