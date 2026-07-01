# Amazon SP-API LWA Refresh Token Retrieval Guide

This guide describes how to generate and configure the **`AMAZON_LWA_REFRESH_TOKEN`** for your private/internal **HCHAHAL Support Console** SP-API application.

---

## 1. What is the LWA Refresh Token?

The **Login with Amazon (LWA) Refresh Token** is a long-lived credential representing the merchant's consent for your application to access their Seller Central data. 

* **Why it is needed**: Access tokens expire after 1 hour. The backend client uses the refresh token to request new temporary access tokens dynamically from the Amazon authorization server without requiring human re-authorization.
* **Format**: Starts with `Atzr|` followed by a long alphanumeric string.

---

## 2. Self-Authorization for Private Apps

Since the **HCHAHAL Support Console** is a private/internal application (not a public app listed on the Selling Partner Appstore), it **can be self-authorized** directly by your own Seller Central administrator. 

Self-authorization bypasses the OAuth consent redirect loop and immediately returns the required refresh token directly inside the Seller Central UI.

---

## 3. Step-by-Step Self-Authorization Flow

### Step 1: Navigate to the Developer Console
1. Log in to your Amazon [Seller Central](https://sellercentral.amazon.com) account using the administrator credentials.
2. In the main menu, go to **Partner Network** ➔ **Develop Apps** (or search for Developer Console).
3. Find your registered app: **HCHAHAL Support Console** or **HCHAHAL Support Connector**.

### Step 2: Trigger Authorization
1. In the action dropdown menu next to your application name, click **Authorize**.
2. If this is a sandbox/draft application:
   * Select the **Authorize** action under the draft status column.
3. Review the data access permission checklist (confirming it requests order details) and click **Authorize App**.

### Step 3: Extract the Refresh Token
1. Upon clicking Authorize, Seller Central will generate and display your **LWA Refresh Token**.
2. Copy the token immediately. 
   * *Note: It starts with `Atzr|`. Save it to a secure temp file or clipboard.*

---

## 4. Redirect / Callback URL Configuration (Fallback)

If you configure your app to support OAuth redirects instead of standard self-authorization:
* **Redirect URL**: Configure a localhost placeholder redirect URL in the App registration screen:
  `http://127.0.0.1:8000/api/amazon/callback` or `https://localhost`
* *For internal support widgets, self-authorization is highly recommended over building redirect pages.*

---

## 5. Local Integration & Verification

### Step 4: Paste into local `backend/.env`
Open your local `backend/.env` file and populate the refresh token key:

```env
AMAZON_LWA_REFRESH_TOKEN=Atzr|LWA_REFRESH_TOKEN_HERE
```

### Step 5: Test Verification Status
Run a terminal query against the local health check:
```bash
curl -s http://127.0.0.1:8000/api/amazon/health | json_pp
```

**Expected JSON Response (With all 5 mandatory keys set):**
```json
{
   "configured" : true,
   "missing_env_vars" : [],
   "mode" : "ready_for_sp_api_test"
}
```

---

## 6. Security Boundaries

> [!CRITICAL]
> **1. No Frontend Exposure**
> Do not copy the LWA refresh token into client-side JS widgets (`widget.js`), static pages, or web repositories.
> 
> **2. No Database Storage**
> Keep the token out of Supabase tables. It belongs solely inside the backend host environment configuration.
> 
> **3. Prevent GitHub commits**
> Make sure `backend/.env` is ignored by git so the active token is never pushed to public repositories.
