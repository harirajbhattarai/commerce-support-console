# Amazon SP-API Credentials Configuration Guide

This guide details the environment variables, credential sources, feature-specific requirements, and security rules required to safely integrate the Amazon Selling Partner API (SP-API) into the HCHAHAL Support Console.

---

## 1. Environment Variable Definitions

Below is a detailed breakdown of each required environment variable:

### `AMAZON_LWA_CLIENT_ID`
* **Meaning**: Login with Amazon (LWA) Client Identifier. Identifies the SP-API application.
* **Format**: Starts with `amzn1.application-oa2-client.`.

### `AMAZON_LWA_CLIENT_SECRET`
* **Meaning**: Login with Amazon Client Secret. Used in combination with the Client ID to request temporary LWA access tokens from the Amazon OAuth server.
* **Format**: A 64-character alphanumeric string.

### `AMAZON_LWA_REFRESH_TOKEN`
* **Meaning**: The long-lived refresh token representing a seller's consent for your application to access their Seller Central account. Used to fetch short-lived access tokens.
* **Format**: Starts with `Atzr|`.

### `AMAZON_AWS_ACCESS_KEY`
* **Meaning**: AWS Access Key ID for the IAM User executing the API calls. Used to generate AWS Signature Version 4 signatures.
* **Format**: A 20-character alphanumeric string starting with `AKIA`.

### `AMAZON_AWS_SECRET_KEY`
* **Meaning**: AWS Secret Access Key corresponding to the IAM User. Used for cryptographic request signing.
* **Format**: A 40-character string.

### `AMAZON_ROLE_ARN`
* **Meaning**: Amazon Resource Name (ARN) of the AWS IAM Role that holds the permissions to invoke the SP-API. The backend assumes this role before signing requests.
* **Format**: Looks like `arn:aws:iam::123456789012:role/your-sp-api-role`.

### `AMAZON_REGION`
* **Meaning**: The AWS / SP-API region endpoint where API calls are routed. Matches the marketplace location of the store.
* **Options**: 
  * North America: `us-east-1`
  * Europe: `eu-west-1`
  * Far East: `us-west-2`

### `AMAZON_MARKETPLACE_ID`
* **Meaning**: The unique identifier of the specific Amazon Marketplace (e.g. Amazon.co.uk or Amazon.com) to search orders and check client data.
* **Format**: A fixed alphanumeric ID (e.g., `A1F83G8C2ARO7P` for UK, `ATVPDKIKX0DER` for US).

---

## 2. Credential Sources Map

| Environment Variable | Source Console / Step |
| :--- | :--- |
| `AMAZON_LWA_CLIENT_ID` | **Seller Central App Console** ➔ Apps ➔ Develop Apps ➔ LWA Credentials |
| `AMAZON_LWA_CLIENT_SECRET` | **Seller Central App Console** ➔ Apps ➔ Develop Apps ➔ LWA Credentials |
| `AMAZON_LWA_REFRESH_TOKEN` | **Seller Central Authorization Flow** ➔ App authorization by the Store Seller |
| `AMAZON_AWS_ACCESS_KEY` | **AWS IAM Console** ➔ IAM Users ➔ Security Credentials ➔ Create Access Key |
| `AMAZON_AWS_SECRET_KEY` | **AWS IAM Console** ➔ IAM Users ➔ Security Credentials ➔ Create Access Key |
| `AMAZON_ROLE_ARN` | **AWS IAM Console** ➔ IAM Roles ➔ Role Summary (linked in trust relationship to User) |
| `AMAZON_REGION` | **Marketplace Settings** ➔ Decided based on store country (e.g., `eu-west-1` for UK/Europe) |
| `AMAZON_MARKETPLACE_ID` | **Amazon Developer Docs** ➔ Look up the static ID corresponding to the target country |

---

## 3. Credential Requirements by Phase / Action

| Feature Phase | Required Variables | Purpose / Action |
| :--- | :--- | :--- |
| **Connector Health Check** | None (All variables checked for existence / placeholders only) | Validates that environment configurations exist and are formatted correctly without making active requests. |
| **Safe Order Lookup** | `AMAZON_LWA_CLIENT_ID`, `AMAZON_LWA_CLIENT_SECRET`, `AMAZON_LWA_REFRESH_TOKEN`, `AMAZON_AWS_ACCESS_KEY`, `AMAZON_AWS_SECRET_KEY`, `AMAZON_ROLE_ARN`, `AMAZON_REGION`, `AMAZON_MARKETPLACE_ID` | Authenticates, signs requests using AWS SigV4, and queries SP-API Orders endpoints (`/orders/v0/orders/{orderId}`) to fetch shipping status/items. |
| **Messaging Actions Check** | Same as above | Hits the `/messaging/v1/actions` endpoint to determine which message types are permitted for a specific order. |
| **Sending Messages (Future)** | Same as above + Specific Amazon messaging permissions approved on App | Sends structured customer replies via Amazon Messaging API endpoints (e.g., `/messaging/v1/orders/{orderId}/messages/custom`). |

---

## 4. Security Rules

> [!CRITICAL]
> **Rule 1: Never expose credentials in Frontend Client Files**
> Do not write or reference AWS, LWA, or role credentials in any static files, HTML templates, or frontend Javascript engines. They must stay encapsulated within the backend server runtime.
> 
> **Rule 2: Never store credentials in Supabase Database Tables**
> Keep credentials out of database rows. The Supabase connection is for user interaction logs and support drafts; it should not hold application API secrets.
> 
> **Rule 3: Use local `backend/.env` for local testing only**
> The local `.env` file should be listed inside `.gitignore` and never committed to source control.
> 
> **Rule 4: Rotate Keys immediately upon exposure**
> If any environment variables or AWS secret keys are accidentally exposed in logs, screenshots, or code commits, delete the IAM credentials in the AWS Console immediately and generate a new set of API access keys.
