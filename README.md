# ⚙️ SmartSpare AI 2.0

> **An Enterprise-Grade Industrial Intelligence & Predictive Maintenance Platform**

SmartSpare AI is a modern, full-stack application designed to revolutionize factory inventory management and predictive maintenance. Built with a highly scalable architecture, it bridges the gap between on-the-floor industrial operations and advanced LLM-driven analytics. 

Version 2.0 introduces a complete architectural overhaul, featuring a mathematically secure JWT authentication pipeline, strict database schema enforcement, and a lightning-fast React frontend.

## ✨ Key Features

* **Secure Authentication Pipeline:** Industry-standard JWT (JSON Web Tokens) with bcrypt password hashing and strict route protection.
* **Multi-Tenant Architecture:** Built in isolation using PostgreSQL UUIDs to securely segregate data across different factories and worker roles.
* **Inventory Management:** Full CRUD capabilities for tracking industrial spare parts, SKUs, and machinery components.
* **Modern UI/UX:** Responsive, component-driven frontend built with Next.js and styled with Tailwind CSS for a seamless user experience.
* **AI Copilot Ready:** The foundation is primed for integrating Generative AI agents to predict maintenance schedules and forecast material demands.

## 🛠️ Tech Stack

**Frontend:**
* Next.js (React Framework)
* Tailwind CSS
* Lucide Icons

**Backend:**
* FastAPI (Python)
* PostgreSQL (Database)
* SQLAlchemy 2.0 (asyncpg)
* Passlib & Bcrypt (Cryptography)
* Pydantic (Data Validation)

## 🚀 Getting Started (Local Development)

Follow these precise steps to get a local instance of SmartSpare AI running on your machine.

### Prerequisites
* **Node.js** (v18+)
* **Python** (3.10+)
* **PostgreSQL** (Installed and running locally via pgAdmin)
* **Git**

### Clone the Repository
```bash
git clone [https://github.com/Ashitpatel001/SmartSpare-AI.git](https://github.com/Ashitpatel001/SmartSpare-AI.git)
cd SmartSpare-AI
```

###  Database Configuration
1. Open **pgAdmin**.
2. Create a new database named `smartspare_ai`.
3. The SQLAlchemy models will automatically build the `users`, `factories`, and `spare_parts` tables upon server startup.


### Backend Setup (FastAPI)
Open a terminal in the root directory:
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
### Environment Variables (.env)
Create a .env file in the root directory and add your secure configuration:
```bash
Ini, TOML
# Database Connection
DATABASE_URL=postgresql+asyncpg://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/smartspare_ai

# Security Settings
SECRET_KEY=generate_a_secure_random_string_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI APIs (Keep these secret!)
GROQ_API_KEY=your_groq_key
```

### Boot the Server:
```bash
Bash
# Run the FastAPI application
uvicorn app.main:app --reload
```

The API documentation will be available at: http://localhost:8000/docs

### Frontend Setup (Next.js)
Open a second terminal window (keep the backend running):
```bash
Bash
# Navigate to the frontend directory (if separated) or stay in root
npm install
```

### Start the development server

npm run dev
The web application will be available at: http://localhost:3000
