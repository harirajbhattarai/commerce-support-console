# HCHAHAL Support Console - Startup & Deployment Manual

This document provides complete instructions for starting, verifying, and troubleshooting the HCHAHAL Support Console prototype locally, as well as deploying it to a cloud hosting environment (e.g., Railway or Render).

---

## 1. Local Development Startup

### Prerequisites
*   Ensure your Supabase database instance is active and has the required schemas applied (see `backend/supabase_schema.sql` and `backend/knowledge_brain_schema.sql`).
*   Ensure that the `agent_replies` table exists (if not, execute the SQL found in `DEPLOYMENT_LIVE_READINESS_PLAN.md`).

### Commands
Navigate to the `backend` directory and run:
```bash
# Navigate to the backend folder
cd "/Volumes/XTREM/BITLEAF-SYTEM/50-59 SYSTEMS/52 AI Agents/GOOGLE_I_O_2026/ANTIGRAVITY_AGENT/backend"

# Start the server using Python's module invoker
./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

> [!NOTE]
> We recommend executing Uvicorn via the Python module invoker (`python -m uvicorn`) rather than calling `./venv/bin/uvicorn` directly. This bypasses absolute shebang path errors that occur if the project folder is moved or opened on another system.

### Local Verification URLs
*   **Health Check Status**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
*   **Admin Dashboard Console**: [http://127.0.0.1:8000/admin-dashboard.html](http://127.0.0.1:8000/admin-dashboard.html)
*   **Customer Storefront Widget**: [http://127.0.0.1:8000/index.html](http://127.0.0.1:8000/index.html)

---

## 2. Cloud Live Deployment Guide

For live production hosting, we recommend a PaaS provider like **Railway** or **Render** due to their low friction, built-in SSL handling, and automatic Github integrations.

### Deployment Configuration Files & Directory Structure
The following files and structures are configured to handle automated cloud builds:
1.  **`Procfile`**: Used by Render, Heroku, and Railway to detect the startup routine.
    ```
    web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    ```
2.  **`runtime.txt`**: Locks the environment Python build version.
    ```
    python-3.11.9
    ```
3.  **`requirements.txt`**: Declares necessary application dependencies.
4.  **`frontend/` (Mirrored)**: Because Railway sets the `backend` folder as the repository root directory, files outside of `backend/` are not included in the container build. The static frontend files have been mirrored into `backend/frontend/` to allow successful static file serving. FastAPI resolves paths dynamically: checking `backend/frontend` first, then falling back to `../frontend` locally, and finally logging a warning instead of crashing if files are missing.

### Step-by-Step Deployment Steps
1.  **VCS Sync**: Push your repository to your private GitHub organization/account.
2.  **PaaS Link**: Create a new Web Service in **Railway** or **Render** and link it to the backend directory.
3.  **Environment Setup**: Copy all variables from `backend/.env.example` into your host's environment settings. Add your live Supabase credentials.
4.  **CORS Restriction**: Set the `ALLOWED_ORIGINS` variable to restrict API access:
    ```
    ALLOWED_ORIGINS=https://hoverboardstore.co.uk,https://www.hoverboardstore.co.uk
    ```
5.  **Shopify Integration**: Change the `apiHost` parameter inside the widget javascript files to point to your new public URL.

---

## 3. Local Troubleshooting Guide

### Case A: Port 8000 is occupied
If your terminal reports that port 8000 is already in use:
1.  Find the Process ID (PID) of the service running on port 8000:
    ```bash
    lsof -i :8000
    ```
2.  Terminate the process using its PID:
    ```bash
    kill -9 <PID>
    ```
3.  Alternatively, start the server on a different port (e.g., 8080):
    ```bash
    ./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
    ```

### Case B: `uvicorn: bad interpreter: No such file or directory`
This occurs if the virtual environment shebang path breaks. Avoid calling `uvicorn` directly; always invoke it using the Python binary:
```bash
./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 4. Safety & Compliance Reminder

> [!WARNING]
> *   **Admin Dashboard Protection Active**: Accessing `/admin-dashboard.html` or administrative APIs requires token authentication when `ADMIN_DASHBOARD_TOKEN` is configured. Navigate to `/admin-dashboard.html?token=YOUR_TOKEN` to unlock your sessions.
> *   **Amazon Selling Partner API is locked to Sandbox Mode**: All order lookups occur against mock sandboxed data only.
> *   **No Live Sending Enabled**: The Amazon Messaging API is completely disconnected. No live customer messages can be sent or transmitted from this console.
> *   **Strict Human-in-the-Loop**: Auto-reply remains disabled. Every message draft generated in the console must be manually reviewed, edited, and copy-pasted into Seller Central by support staff.
