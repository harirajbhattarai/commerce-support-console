# Change Control and Release Workflow
## Hoverboard Store AI Support Agent

> [!CAUTION]
> Any push to `main` that bypasses this workflow risks breaking the live Shopify customer widget on hoverboardstore.co.uk. Follow every step.

---

## Guiding Principle

**If it's not tested in staging first, it does not go to production.**
No exceptions for "small" fixes, prompt tweaks, or database seed changes.

---

## Branch Model

```
main         ← Production only. Auto-deploys to Production Railway.
staging      ← Integration test branch. Auto-deploys to Staging Railway.
feature/*    ← All new work. Branch from staging, never from main.
hotfix/*     ← Urgent production fixes only. Branch from main, merge to main AND staging.
```

---

## Workflow: Standard Feature

### Step 1 — Create Feature Branch from Staging
```bash
git checkout staging
git pull origin staging
git checkout -b feature/your-feature-name
```

### Step 2 — Develop and Test Locally
```bash
cd backend
./venv/bin/python test_takeover_flow.py
APP_ENV=STAGING ./venv/bin/python -m uvicorn app.main:app --reload
```

### Step 3 — Push Feature Branch to Remote
```bash
git add <files>
git commit -m "feat: description of your change"
git push origin feature/your-feature-name
```

### Step 4 — Merge Feature into Staging
```bash
git checkout staging
git pull origin staging
git merge feature/your-feature-name
git push origin staging
```
→ Railway Staging auto-deploys from the `staging` branch push.

### Step 5 — Run Full Staging QA
- Visit staging Railway URL
- Confirm `STAGING` badge visible in dashboard
- Run integration test suite:
  ```bash
  ./venv/bin/python test_takeover_flow.py
  ```
- Run dataset test runner (Phase 2+):
  ```bash
  ./venv/bin/python tests/run_dataset_tests.py
  ```
- Confirm all tests pass ✅

### Step 6 — Merge Staging into Main (Production Deploy)
```bash
git checkout main
git pull origin main
git merge staging
git push origin main
```
→ Railway Production auto-deploys from the `main` branch push.

### Step 7 — Post-Deploy Verify
- Visit production Railway URL
- Confirm `PRODUCTION` badge visible in dashboard
- Send one test message in live Shopify widget
- Confirm response is correct

---

## Workflow: Hotfix (Urgent Production Fix)

Only use for genuine production-breaking bugs.

```bash
# Branch from main
git checkout main
git pull origin main
git checkout -b hotfix/description-of-fix

# Make targeted fix, test locally
cd backend
./venv/bin/python test_takeover_flow.py

# Merge to main (production)
git checkout main
git merge hotfix/description-of-fix
git push origin main

# Also merge hotfix to staging to keep branches in sync
git checkout staging
git merge hotfix/description-of-fix
git push origin staging

# Delete hotfix branch
git branch -d hotfix/description-of-fix
git push origin --delete hotfix/description-of-fix
```

---

## What Requires a Staging Test Before Production

| Change Type | Staging Required |
| :--- | :--- |
| Any change to `support_brain.py` | ✅ Mandatory |
| Any change to `/api/chat` route | ✅ Mandatory |
| Any new intent or routing rule | ✅ Mandatory |
| Any Supabase schema change | ✅ Mandatory |
| Any new knowledge article seeded | ✅ Mandatory |
| Any change to `admin-dashboard.html` | ✅ Mandatory |
| Any new Railway environment variable | ✅ Mandatory |
| Any change to MiniMax prompt | ✅ Mandatory — dataset test required |
| Fix to static text or CSS only | ⚠️ Recommended |
| Documentation update only | Optional |

---

## Commit Message Format

Use this format for all commits:

```
<type>: <short description>

Types:
  feat:     New feature or behaviour
  fix:      Bug fix
  docs:     Documentation only
  test:     Test additions or changes
  refactor: Code reorganisation with no behaviour change
  chore:    Dependency or config update
```

Examples:
```
feat: add reset/calibration intent to support brain
fix: prevent low-risk queries from triggering needs_escalation
docs: update PHASE_GATES with Phase 1 completion status
test: add 50 new product recommendation questions to dataset v2
```

---

## Prohibited Actions

| ❌ Action | Reason |
| :--- | :--- |
| `git push origin main` for a chatbot logic change without staging test | Could break live widget |
| Direct edit of production Railway environment variables without staging test | Could break live bot |
| Delete or truncate production Supabase tables | Irreversible data loss |
| Share production ADMIN_DASHBOARD_TOKEN | Security breach |
| Share SUPABASE_SERVICE_ROLE_KEY | Security breach |
| Add `print()` debug calls containing tokens/keys | Accidental secret exposure in logs |
