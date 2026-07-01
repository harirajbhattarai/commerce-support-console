# Amazon SP-API Developer Setup Checklist

This checklist provides step-by-step instructions for provisioning, configuring, and testing real Amazon Selling Partner API (SP-API) credentials for local integration.

> [!WARNING]
> **Existing Suppressed Apps Notice**
> * There are existing Developer Central applications named **hscm** and **redcube** showing a status of **Suppressed**.
> * **Do NOT** use, edit, rotate, delete, or connect to these apps until ownership has been officially verified.
> * For this project, you must create a separate, dedicated private/internal SP-API application named **HCHAHAL Support Console** or **HCHAHAL Support Connector**.
> 
> **Important Safety Policies**
> * **No Live Amazon Sending**: Automatic outbound message sending remains strictly disabled.
> * **Human Approval Only**: All messages must require manual agent approval inside the console prior to queue transmission.

---


## Phase 1: Amazon Seller Central & Developer Prerequisites

- [x] **Step 1: Verify Seller Central Account Status**
  * Ensure you have an active Professional Selling Account on Amazon Seller Central (Individual accounts cannot access SP-API developer registration).
- [x] **Step 2: Register as a Developer** (Solution Provider Portal Onboarding Completed)
  * Navigate to the [Seller Central Developer Console](https://sellercentral.amazon.com/developer/register).
  * Fill out the developer profile request. Specify that your application handles customer support triage (request access to order information, but select *no* for direct Personally Identifiable Information (PII) if you are only matching orders).
- [x] **Step 3: Define Region and Marketplace**
  * Identify your target marketplace region. For the UK marketplace, use the following:
    * **Marketplace ID**: `A1F83G8C2ARO7P`
    * **AWS / SP-API Region**: `eu-west-1` (Europe Endpoint)

---

## Phase 2: AWS IAM Identity Configuration (Optional / Legacy / Future Use)

> [!NOTE]
> **AWS IAM is no longer required for standard SP-API integration.** Amazon has removed the AWS Signature Version 4 requirements for standard endpoints. You may skip this phase entirely unless you plan to use AWS-based notification hooks (such as SQS subscriptions) later.


- [ ] **Step 4: Create an AWS IAM User**
  * Log in to the AWS Management Console.
  * Go to the IAM Service ➔ Users ➔ **Create user**.
  * Name the user (e.g., `sp-api-ingress-user`).
  * Under security credentials, create an **Access Key for programmatic access**.
  * Save the generated keys:
    * `AMAZON_AWS_ACCESS_KEY`
    * `AMAZON_AWS_SECRET_KEY`
- [ ] **Step 5: Create a SP-API Invocation Policy**
  * Create a custom IAM Policy permitting execution permissions on SP-API:
    ```json
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": "execute-api:Invoke",
          "Resource": "arn:aws:execute-api:*:*:*"
        }
      ]
    }
    ```
- [ ] **Step 6: Create the IAM Role to Assume**
  * Create an IAM Role (e.g., `sp-api-caller-role`).
  * Attach the Invocation Policy created in Step 5.
  * Configure the **Trust Relationship of the role** to allow the IAM User created in Step 4 to assume this role.
  * Save the Role's ARN:
    * `AMAZON_ROLE_ARN`

---

## Phase 3: Developer App Registration & LWA Credentials

- [x] **Step 7: Register App in Seller Central** (Sandbox SP-API App `HCHAHAL SUPPORT CONNECTOR` Created)
  * Go to Seller Central ➔ Partner Network ➔ **Develop Apps** (Developer Console).
  * Click **Register new application**.
  * Enter your application name as **HCHAHAL SUPPORT CONNECTOR** (do not modify existing suppressed apps *hscm* or *redcube*).
  * Input the IAM Role ARN saved in Step 6 (`AMAZON_ROLE_ARN`) under the IAM ARN input (note: optional/legacy for standard test flow).
  * Choose **SP-API** as the API type.
- [x] **Step 8: Retrieve Login with Amazon (LWA) Credentials** (AMAZON_LWA_CLIENT_ID & AMAZON_LWA_CLIENT_SECRET Verified)
  * Once the application is approved/registered, view the LWA Credentials.
  * Copy and save the parameters:
    * `AMAZON_LWA_CLIENT_ID`
    * `AMAZON_LWA_CLIENT_SECRET`

---

## Phase 4: Retrieve LWA Refresh Token Safely

- [x] **Step 9: Generate User Consent Authorization Link** (Sandbox app consent approved)
  * In the Developer Console app listing, click the dropdown actions menu for your app and select **Authorize**.
  * Choose the store account you want to connect and authorize.
- [x] **Step 10: Extract the Refresh Token** (AMAZON_LWA_REFRESH_TOKEN Verified)
  * Once authorized, Seller Central redirects to the redirect URL containing the auth parameters, or displays the client consent data directly.
  * Copy and save the token:
    * `AMAZON_LWA_REFRESH_TOKEN` (Starts with `Atzr|`)

---

## Phase 5: Local Integration & Security Boundaries

- [x] **Step 11: Set local Environment Variables** (Configured in backend/.env)
  * Paste the gathered credentials **ONLY** inside the backend configuration file:
    * File: `backend/.env`
  * Example layout:
    ```env
    # Mandatory for standard SP-API calls
    AMAZON_LWA_CLIENT_ID=amzn1.application-oa2-client.your-real-id
    AMAZON_LWA_CLIENT_SECRET=your-real-secret
    AMAZON_LWA_REFRESH_TOKEN=Atzr|your-real-token
    AMAZON_REGION=eu-west-1
    AMAZON_MARKETPLACE_ID=A1F83G8C2ARO7P

    # Optional / Legacy AWS credentials (skip for standard calls)
    AMAZON_AWS_ACCESS_KEY=AKIAYOURREALACCESSKEY
    AMAZON_AWS_SECRET_KEY=yourrealawssecretkey
    AMAZON_ROLE_ARN=arn:aws:iam::123456789012:role/your-sp-api-role
    ```

### Strict Guardrails (What NOT to do)
- [x] **Security Rule 1**: **Do NOT** copy these keys into frontend HTML or JavaScript files.
- [x] **Security Rule 2**: **Do NOT** insert these credentials into database tables or Supabase rows.
- [x] **Security Rule 3**: **Do NOT** commit your `backend/.env` file to git repositories. Ensure it is ignored.
- [x] **Security Rule 4**: **Do NOT** enable message transmission or automated customer responses.

---

## Phase 6: Verify Endpoint Status

- [x] **Step 12: Run the Diagnostic Verification** (GET /api/amazon/health returns configured: true)
  * Verify that the hot-reloaded FastAPI server parses the credentials successfully.
  * Run a terminal query:
    ```bash
    curl -s http://127.0.0.1:8000/api/amazon/health | json_pp
    ```
  * Confirm that the response switches to `ready_for_sp_api_test` once all **5 mandatory keys** are successfully populated with valid, non-placeholder credentials:
    ```json
    {
       "configured" : true,
       "missing_env_vars" : [],
       "mode" : "ready_for_sp_api_test"
    }
    ```

---

## Phase 7: Sandbox Connection Token Test

- [x] **Step 13: Run Sandbox Token Exchange Verification** (GET /api/amazon/token-test - **Verified**)
  * Verify that the backend can successfully request an LWA access token from Amazon's OAuth server. **Token exchange works.**
  * Run a terminal query:
    ```bash
    curl -s http://127.0.0.1:8000/api/amazon/token-test | json_pp
    ```
  * Confirm that the response returns the standard success payload showing the exchange completed successfully:
    ```json
    {
       "access_token_received" : true,
       "configured" : true,
       "expires_in" : 3600,
       "mode" : "sandbox_token_test",
       "token_exchange" : "success"
    }
    ```

---

## Phase 8: Sandbox API Connectivity Call Test

- [x] **Step 14: Run Sellers Sandbox Marketplace Participations Query** (GET /api/amazon/sandbox/marketplaces - **Verified**)
  * Verify that the backend can successfully fetch and parse mock sandbox marketplace participations. **First safe SP-API sandbox call works.**
  * *Note: The sandbox returns mock marketplace data which shows the US marketplace (`ATVPDKIKX0DER`, `Amazon.com`, `USD`) even though the UK marketplace (`A1F83G8C2ARO7P` / `eu-west-1`) is configured.*
  * Run a terminal query:
    ```bash
    curl -s http://127.0.0.1:8000/api/amazon/sandbox/marketplaces | json_pp
    ```
  * Confirm that the response returns the standard success payload showing that both token exchange and the SP-API call succeeded:
    ```json
    {
       "configured" : true,
       "endpoint" : "sellers marketplace participations",
       "marketplace_count" : 1,
       "marketplaces" : [
          {
             "country_code" : "US",
             "default_currency_code" : "USD",
             "is_participating" : true,
             "marketplace_id" : "ATVPDKIKX0DER",
             "name" : "Amazon.com"
          }
       ],
       "mode" : "sandbox_marketplace_test",
       "sp_api_call" : "success",
       "token_exchange" : "success"
    }
    ```

---

## Phase 9: Sandbox Orders API Call Test

- [x] **Step 15: Run Orders Sandbox API Query** (GET /api/amazon/sandbox/orders - **Verified**)
  * Verify that the backend can successfully fetch and parse mock sandbox orders. **First safe SP-API Orders sandbox call works.**
  * *Note: The sandbox returns mock US order records by default. All buyer PII is explicitly removed.*
  * Run a terminal query:
    ```bash
    curl -s http://127.0.0.1:8000/api/amazon/sandbox/orders | json_pp
    ```
  * Confirm that the response returns the standard success payload showing that both token exchange and the Orders API call succeeded, containing sanitized fields with no buyer PII:
    ```json
    {
       "configured" : true,
       "endpoint" : "orders list",
       "mode" : "sandbox_orders_test",
       "order_count" : 2,
       "orders" : [
          {
             "amazon_order_id" : "902-1845936-5435065",
             "fulfillment_channel" : "MFN",
             "last_update_date" : "1970-01-19T03:58:32Z",
             "number_of_items_shipped" : 0,
             "number_of_items_unshipped" : 1,
             "order_status" : "Unshipped",
             "order_type" : "StandardOrder",
             "purchase_date" : "1970-01-19T03:58:30Z",
             "sales_channel" : "Amazon.com"
          },
          {
             "amazon_order_id" : "902-8745147-1934268",
             "fulfillment_channel" : "MFN",
             "last_update_date" : "1970-01-19T03:58:32Z",
             "number_of_items_shipped" : 0,
             "number_of_items_unshipped" : 1,
             "order_status" : "Unshipped",
             "order_type" : "StandardOrder",
             "purchase_date" : "1970-01-19T03:58:30Z",
             "sales_channel" : "Amazon.com"
          }
       ],
       "sp_api_call" : "success",
       "token_exchange" : "success"
    }
    ```

---

## Phase 10: Sandbox Single Order Lookup API Call Test

- [x] **Step 16: Run Single Order Sandbox Lookup API Query** (GET /api/amazon/orders/{order_id} - **Verified**)
  * Verify that the backend can successfully fetch and parse a specific sandbox order. **First safe SP-API Single Order sandbox lookup works.**
  * *Note: Tested with sandbox order ID `902-1845936-5435065`. All buyer PII is explicitly removed.*
  * Run a terminal query:
    ```bash
    curl -s http://127.0.0.1:8000/api/amazon/orders/902-1845936-5435065 | json_pp
    ```
  * Confirm that the response returns the standard success payload showing that both token exchange and the Single Order API call succeeded, containing sanitized fields with no buyer PII:
    ```json
    {
       "configured" : true,
       "endpoint" : "order lookup",
       "mode" : "sandbox_order_lookup",
       "order" : {
          "amazon_order_id" : "902-1845936-5435065",
          "fulfillment_channel" : "MFN",
          "last_update_date" : "1970-01-19T03:58:32Z",
          "number_of_items_shipped" : 0,
          "number_of_items_unshipped" : 1,
          "order_status" : "Unshipped",
          "order_type" : "StandardOrder",
          "purchase_date" : "1970-01-19T03:58:30Z",
          "sales_channel" : "Amazon.com"
       },
       "sp_api_call" : "success",
       "token_exchange" : "success"
    }
    ```

---

---

## Phase 11: Sandbox Issue Classification & Draft Reply API Call Test

- [x] **Step 17: Run Sandbox Issue Classification & Draft Reply Query** (POST /api/amazon/draft/analyse - **Verified**)
  * Verify that the backend can analyze buyer messages, assign issue categories and risk levels, and dynamically generate draft templates using retrieved order status.
  * Run a terminal query to verify a low-risk invoice request:
    ```bash
    curl -s -X POST -H "Content-Type: application/json" -d '{"message": "Please send me a VAT invoice"}' http://127.0.0.1:8000/api/amazon/draft/analyse | json_pp
    ```
  * Run a terminal query to verify a high-risk safety escalation:
    ```bash
    curl -s -X POST -H "Content-Type: application/json" -d '{"message": "My hoverboard battery exploded and caught fire!"}' http://127.0.0.1:8000/api/amazon/draft/analyse | json_pp
    ```
  * Run a terminal query to verify dynamic draft customization for an unshipped order:
    ```bash
    curl -s -X POST -H "Content-Type: application/json" -d '{"message": "Please cancel my order 902-1845936-5435065"}' http://127.0.0.1:8000/api/amazon/draft/analyse | json_pp
    ```
  * Run a terminal query to verify dynamic draft customization for a shipped order:
    ```bash
    curl -s -X POST -H "Content-Type: application/json" -d '{"message": "Please cancel my order 902-8745147-1934268"}' http://127.0.0.1:8000/api/amazon/draft/analyse | json_pp
    ```

---

## Safety & Next Steps

* **No buyer PII (ShippingAddress, BuyerInfo, BuyerTaxInformation) has been returned or processed.**
* **No messaging APIs have been touched and no Amazon messages have been sent.**
* **No Messaging API was used. Auto-send remains disabled.**
* **Important Note**:
  * **Sandbox Mode**: Sandbox uses mock order IDs and fallback mapping for known sandbox test IDs (such as mapping `902-1845936-5435065` to `TEST_CASE_200` internally to match static sandbox rules). We have customized the returned order status to show both Shipped and Unshipped flows in the sandbox.
  * **Production Mode**: Production order lookup later must use real order IDs and continue to exclude buyer PII unless explicitly approved and compliant.
* **Next Recommended Phase**: Design and implement the support console UI elements (e.g. risk indicators, suggested draft reply cards, editor integration) to show these classification results inside the admin panel.




