# HCHAHAL Support Console - Local Startup Manual

This document provides instructions for starting, verifying, and troubleshooting the local development environment for the HCHAHAL Support Console prototype.

---

## 1. Project Specifications

*   **Project Workspace Path**:  
    `/Volumes/XTREM/BITLEAF-SYTEM/50-59 SYSTEMS/52 AI Agents/GOOGLE_I_O_2026/ANTIGRAVITY_AGENT`
*   **Default Listening Port**: `8000`

---

## 2. Startup Instructions

To start the FastAPI backend server safely, follow these steps in your terminal:

```bash
# Step 1: Navigate to the backend folder
cd "/Volumes/XTREM/BITLEAF-SYTEM/50-59 SYSTEMS/52 AI Agents/GOOGLE_I_O_2026/ANTIGRAVITY_AGENT/backend"

# Step 2: Start the server using Python's module invoker
./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

> [!NOTE]
> We recommend executing Uvicorn via the Python module invoker (`python -m uvicorn`) rather than calling `./venv/bin/uvicorn` directly. This bypasses absolute shebang path errors that occur if the project folder is moved or opened on another system.

---

## 3. Verification URLs

Once the server is running, you can verify and access the system via the following URLs:

*   **Health Check Status**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)  
    *(Confirms server status, database connection, and loaded store configurations)*
*   **Admin Dashboard Console**: [http://127.0.0.1:8000/admin-dashboard.html](http://127.0.0.1:8000/admin-dashboard.html)  
    *(The support representative console view)*
*   **Customer Storefront Widget**: [http://127.0.0.1:8000/index.html](http://127.0.0.1:8000/index.html)  
    *(Simulates the client chat widget)*

---

## 4. Troubleshooting Guide

### Case A: "Address already in use" (Port 8000 is occupied)
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

### Case B: "Missing Folder" or "No such file" (External drive `XTREM` is not mounted)
Since this project is stored on the external volume `XTREM`, files will appear missing if the drive goes to sleep or is unplugged:
1.  Unplug and reconnect the external drive.
2.  Verify the drive is mounted in macOS Finder or run:
    ```bash
    df -h | grep XTREM
    ```
3.  If visible but not mounted, open macOS **Disk Utility**, select the volume, and click **Mount**.

### Case C: `uvicorn: bad interpreter: No such file or directory`
This occurs if the virtual environment shebang path breaks. Avoid calling `uvicorn` directly; always invoke it using the Python binary:
```bash
./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 5. Safety & Compliance Reminder

> [!WARNING]
> *   **Amazon Selling Partner API is locked to Sandbox Mode**: All order lookups occur against mock sandboxed data only.
> *   **No Live Sending Enabled**: The Amazon Messaging API is completely disconnected. No live customer messages can be sent or transmitted from this console.
> *   **Strict Human-in-the-Loop**: Auto-reply remains disabled. Every message draft generated in the console must be manually reviewed, edited, and copy-pasted into Seller Central by support staff.
