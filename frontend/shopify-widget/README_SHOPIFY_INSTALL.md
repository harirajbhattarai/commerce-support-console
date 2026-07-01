# Shopify Chatbot Widget Installation Guide

Follow these steps to integrate the floating customer support chatbot widget into your Shopify theme.

---

## 1. File Categorization

### Local Development / Testing
These files are used only for local verification and mock hosting:
- `frontend/index.html`: Development test page (mock shop dashboard).
- `frontend/widget.js` & `frontend/widget.css`: Sandboxed development scripts.

### Shopify Production
These are the files you will upload to your Shopify Theme editor:
- `frontend/shopify-widget/hoverboard-chat-widget.js`
- `frontend/shopify-widget/hoverboard-chat-widget.css`
- `frontend/shopify-widget/install-snippet.liquid`

---

## 2. Shopify Installation Steps

### Step A: Upload Assets
1. From your Shopify Admin dashboard, go to **Online Store** > **Themes**.
2. Click the three dots (`...`) next to your active theme and click **Edit code**.
3. Scroll down the left-hand folder tree to the **Assets** folder.
4. Click **Add a new asset** and upload these two files:
   - `hoverboard-chat-widget.js`
   - `hoverboard-chat-widget.css`

### Step B: Create the Liquid Snippet
1. In the same code editor, scroll up to the **Snippets** folder.
2. Click **Add a new snippet**.
3. Name it exactly: `hoverboard-chat-snippet`.
4. Open the newly created `hoverboard-chat-snippet.liquid` file.
5. Copy the entire contents of `install-snippet.liquid` and paste it inside.
6. **Configure the Store Scoping** (lines 8-13):
   Adjust the values for your specific store:
   ```html
   <script>
     window.HBS_CHAT_CONFIG = {
       storeId: "hoverboard_store", // E.g., 'hoverboard_store', 'hcs_gadgets', or 'aroma_haven'
       apiHost: "http://127.0.0.1:8000" // Keep this as localhost for local testing. Replace with production URL later.
     };
   </script>
   ```
7. Click **Save**.

### Step C: Include Snippet in the Theme Layout
To make the floating chatbot visible on all pages, render the snippet in your main layout file:
1. Open the **Layout** folder on the left menu.
2. Click **`theme.liquid`**.
3. Scroll down to the bottom of the file and locate the closing `</body>` tag.
4. Directly **above** the `</body>` tag, insert this line to render the snippet:
   ```liquid
   {% render 'hoverboard-chat-snippet' %}
   ```
5. Click **Save**.

---

## 3. Local testing your Shopify theme
When testing the widget inside Shopify locally (e.g. running a local Shopify CLI theme dev server):
- Keep the FastAPI python backend server running (`uvicorn app.main:app --reload --port 8000`).
- Ensure `allow_origins=["*"]` is kept inside `backend/app/main.py` so requests from your Shopify store domain are not blocked by CORS settings.
