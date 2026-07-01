# AWS IAM Config Guide for Selling Partner API (SP-API)

This guide provides step-by-step instructions on how to configure an AWS IAM User and IAM Role required to authenticate, sign, and make requests to Amazon SP-API.

> [!IMPORTANT]
> **AWS IAM & SigV4 is no longer required for standard SP-API calls.**  
> Amazon has officially deprecated the requirement for AWS Signature Version 4 for standard API invocations. The configuration steps below are kept only as legacy/reference or if you need to set up AWS SQS webhook notification subscriptions later. For standard order lookups and basic endpoints, you only need LWA credentials and marketplace identifiers.

---


## 1. Prerequisites & AWS Account Choice

* **AWS Account selection**: You can use a standard AWS Free Tier or paid account. It does **not** have to be the AWS account associated with your Amazon Seller Central developer account, although using the same account simplifies management.
* **Region recommendation**: While IAM is global, the SP-API resources reside on regional AWS endpoints (e.g., `eu-west-1` for Europe).

---

## 2. AWS Keys vs. Amazon LWA Credentials

It is critical to distinguish these two sets of credentials:

| Credential Type | Authority | Purpose |
| :--- | :--- | :--- |
| **AWS Access Key & Secret** | AWS Console (IAM) | Used to sign the API request cryptographically using **AWS Signature Version 4 (SigV4)**. |
| **Login with Amazon (LWA) Token** | Amazon Seller Central | OAuth credentials used to get an access token that represents the merchant's consent to read/write their data. |

To make a call to SP-API, the backend must use **both** (1) the LWA Access Token in the headers and (2) the AWS IAM credentials to sign the entire request envelope.

---

## 3. Step-by-Step IAM Configuration

### Step 1: Create the IAM User
This user is a programmatic user whose access keys will be used by the backend.
1. Log in to the AWS Management Console and open the **IAM Console**.
2. In the navigation pane, choose **Users** ➔ **Create user**.
3. Set the name to `sp-api-ingress-user`.
4. Click **Next** to proceed to permissions.
5. Do **not** assign any policies directly to this user. This user only needs permission to assume the role we will create.
6. Click **Next**, then **Create user**.

### Step 2: Generate Access Keys
1. Click on the newly created user `sp-api-ingress-user` in the Users list.
2. Select the **Security credentials** tab.
3. Scroll down to **Access keys** and click **Create access key**.
4. Choose **Application running outside AWS** or **Other**, then click **Next**.
5. Click **Create access key**.
6. **Save the credentials immediately**:
   * **`AMAZON_AWS_ACCESS_KEY`**: AWS Access Key ID (e.g. `AKIA...`)
   * **`AMAZON_AWS_SECRET_KEY`**: AWS Secret Access Key.
   * *Do not close the page until you have saved these values securely.*

### Step 3: Create the SP-API Invocation Policy
1. In the IAM Console navigation pane, choose **Policies** ➔ **Create policy**.
2. Select the **JSON** tab and paste the following policy definition:
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
3. Click **Next: Tags**, then **Next: Review**.
4. Name the policy `SPAPIIInvocationPolicy` and click **Create policy**.

### Step 4: Create the IAM Role
This is the role that holds the actual SP-API call permissions.
1. In the IAM Console navigation pane, choose **Roles** ➔ **Create role**.
2. For trusted entity type, select **Custom trust policy**.
3. Under the custom trust policy block, specify that only the IAM user created in Step 1 is allowed to assume this role. Paste the following JSON (replace `<AWS_ACCOUNT_ID>` with your 12-digit AWS Account ID):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "arn:aws:iam::<AWS_ACCOUNT_ID>:user/sp-api-ingress-user"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   ```
4. Click **Next**.
5. In the permissions list, search for and select the checkbox next to **`SPAPIIInvocationPolicy`** (created in Step 3).
6. Click **Next**.
7. Name the role `sp-api-caller-role`.
8. Click **Create role**.
9. Select the newly created role and copy its ARN:
   * **`AMAZON_ROLE_ARN`** (e.g. `arn:aws:iam::123456789012:role/sp-api-caller-role`).

---

## 4. Key Target Variable Sources

| Environment Variable | Where it Comes From |
| :--- | :--- |
| `AMAZON_AWS_ACCESS_KEY` | **AWS User Credentials (Step 2)** |
| `AMAZON_AWS_SECRET_KEY` | **AWS User Credentials (Step 2)** |
| `AMAZON_ROLE_ARN` | **AWS Role Summary (Step 4)** |

---

## 5. Security Rules

> [!CRITICAL]
> **Rule 1: No Frontend Key Inclusion**
> Under no circumstances should AWS User keys, secret keys, or role ARNs be copy-pasted or referenced inside frontend directories (`frontend/*`), UI HTML, or client JavaScript files.
> 
> **Rule 2: No Code Commits**
> Do not check in `.env` files containing these keys to GitHub. Ensure `backend/.env` is ignored by `.gitignore`.
> 
> **Rule 3: Local Environment Boundary**
> Keep credentials restricted exclusively to `backend/.env` for local testing.
