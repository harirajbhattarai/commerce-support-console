# HCHAHAL Support Console - GitHub Push Checklist

Use this checklist to securely initialize Git and push the project codebase to a private GitHub repository without exposing configurations or API credentials.

---

## 1. Pre-Push Security Verifications

- [x] **GitIgnore Defined**: Confirm a `.gitignore` exists at the root path of the project.
- [x] **Secrets Ignored**: Verify `backend/.env` and `.env` are listed in `.gitignore` (they will show up as untracked files in `git status` but will not be added).
- [x] **Placeholders Gated**: Confirm `backend/.env.example` contains only placeholder values (e.g. `your-supabase-service-role-key`).
- [x] **No Hardcoded Tokens**: Verify that no production API keys, service role keys, or Amazon LWA refresh tokens are hardcoded inside backend source files.
- [x] **PaaS Configuration Verified**: Ensure `backend/Procfile`, `backend/runtime.txt`, and `backend/requirements.txt` exist and are configured.

---

## 2. Git Sequence & Push Commands

Follow these exact shell commands to initialize git and push to your private repository:

```bash
# Step 1: Initialize local Git repository (if not already initialized)
git init

# Step 2: Check git status to ensure ignored files (.env, venv/) are not staged
git status

# Step 3: Add all code files to the staging index
git add .

# Step 4: Verify staged files again to ensure no secret configuration gets committed
git status

# Step 5: Commit the files to the local repository
git commit -m "feat: integrate dynamic CORS settings and prepare deployment configurations"

# Step 6: Create your private repository on github.com (do not initialize with README, .gitignore, or license)
# Then link the local repository to your remote
git remote add origin git@github.com:YOUR_ORGANIZATION_OR_USERNAME/hchahal-support-console.git

# Step 7: Rename current branch to main
git branch -M main

# Step 8: Push the code to the main branch
git push -u origin main
```

---

## 3. Post-Push Audits

- [ ] Log in to your **GitHub Account** and select the new private repository.
- [ ] Verify that the `backend/.env` file is **not** present in the file explorer.
- [ ] Confirm that `Procfile`, `runtime.txt`, and `requirements.txt` are active in the `backend/` subdirectory.
- [ ] Proceed to configure the environment variables within your hosting provider (Railway/Render) using the templates defined in `.env.example`.
