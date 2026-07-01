/* =========================================================================
   CHATBOT WIDGET CORE ENGINE - CLIENT INTERACTIVITY
   ========================================================================= */

// Configuration Settings
const BACKEND_URL = "http://127.0.0.1:8000";

// Mock store product data for visual showcase
const MOCK_STORES_CONTENT = {
  hoverboard_store: {
    title: "Hoverboard Store UK",
    badge: "⚡ UK Fast Free Delivery",
    heroTitle: "Ride the Future Today",
    heroDesc: "Explore the UK's safest UL-certified electric hoverboards and scooters. Built for performance, durability, and pure joy.",
    suggestions: ["Shipping delivery times", "Return policy", "Battery safety guide"],
    products: [
      { name: "Apex Cruiser V1", price: "£199.99", desc: "UL-certified, safe battery technology with built-in Bluetooth speakers.", emoji: "🛴" },
      { name: "Nomad All-Terrain", price: "£289.50", desc: "Heavy duty 8.5-inch rugged wheels designed for mud, grass, and gravel.", emoji: "🛹" },
      { name: "Supernova Light-Up", price: "£149.00", desc: "Bright LED wheel lights and hoverboard shell. Perfect gift for teenagers.", emoji: "✨" }
    ]
  },
  hcs_gadgets: {
    title: "HCS Gadgets",
    badge: "🔌 Quality Checked Tech Diagnostics",
    heroTitle: "Premium Audio & Wearables",
    heroDesc: "Curated collection of next-gen smart devices, active noise cancelling headphones, and wearable diagnostics.",
    suggestions: ["Warranty policy", "Diagnostic returns", "Faulty gadget help"],
    products: [
      { name: "HCS Wave ANC Earbuds", price: "£49.99", desc: "Active Noise Cancellation, 30 hours battery life with charging case.", emoji: "🎧" },
      { name: "Pulse Fit Smartwatch", price: "£79.00", desc: "Heart rate monitoring, step counter, sleep tracker, and GPS logs.", emoji: "⌚" },
      { name: "Quantum Charge Powerbank", price: "£24.99", desc: "10,000mAh rapid charging backup battery with dual USB-C output.", emoji: "🔋" }
    ]
  },
  aroma_haven: {
    title: "Aroma Haven Botanicals",
    badge: "🪻 100% Pure Organic Extracts",
    heroTitle: "Nurture Your Sanctuary",
    heroDesc: "Hand-blended pure essential oils, soy-wax candles, and high-frequency ultrasonic mist diffusers.",
    suggestions: ["Essential oils guide", "Leaked broken package", "Safe oil diffusing"],
    products: [
      { name: "Calming Lavender Oil (10ml)", price: "£12.00", desc: "Organic English lavender extract. Promotes deep sleep and relaxation.", emoji: "🪻" },
      { name: "Zen Ultrasonic Diffuser", price: "£34.99", desc: "Sleek wooden base, 7-color ambient light cycles, whisper-quiet mist.", emoji: "💨" },
      { name: "Invigorating Citrus Candle", price: "£18.50", desc: "Soy-wax hand-poured candle infused with sweet orange and lemon peel.", emoji: "🕯️" }
    ]
  }
};

// --------------------------------------------------------------------------
// DOM ELEMENTS
// --------------------------------------------------------------------------
const bodyEl = document.body;
const storeSelect = document.getElementById("store-select");
const storeTitle = document.getElementById("store-title");
const heroBadge = document.getElementById("hero-badge");
const heroTitle = document.getElementById("hero-title");
const heroDesc = document.getElementById("hero-desc");
const productGrid = document.getElementById("product-grid");

const chatWindow = document.getElementById("chat-window");
const chatFab = document.getElementById("chat-fab");
const chatClose = document.getElementById("chat-close");
const chatBody = document.getElementById("chat-body");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatSuggestions = document.getElementById("chat-suggestions");
const chatHeaderTitle = document.getElementById("chat-header-title");
const badgeDot = document.querySelector(".badge-dot");

// State tracker
let activeStore = "hoverboard_store";
let storeConversations = {}; // Schema: { store_id: { conversation_id, messages: [] } }

// --------------------------------------------------------------------------
// ENGINE INITIALIZATION
// --------------------------------------------------------------------------
window.addEventListener("DOMContentLoaded", () => {
  // 1. Setup default state
  activeStore = storeSelect.value || "hoverboard_store";
  
  // 2. Load conversation logs from Session Storage if available
  const savedState = sessionStorage.getItem("shopify_chatbot_conversations");
  if (savedState) {
    try {
      storeConversations = JSON.parse(savedState);
    } catch (e) {
      console.error("Could not parse saved conversations session:", e);
      storeConversations = {};
    }
  }

  // 3. Render store page contents
  renderStoreLayout(activeStore);

  // 4. Setup Event Listeners
  storeSelect.addEventListener("change", handleStoreChange);
  chatForm.addEventListener("submit", handleFormSubmit);

  // Handle FAB clicks manually to toggle badges/unread counts
  chatFab.addEventListener("click", () => {
    badgeDot.classList.add("hidden");
  });

  // Inject initial greeting if first time
  ensureInitialGreeting(activeStore);

  // 5. Setup REST polling for agent replies every 5 seconds
  setInterval(pollAgentReplies, 5000);
});

// --------------------------------------------------------------------------
// BACKGROUND AGENT REPLIES POLLING ENGINE
// --------------------------------------------------------------------------
async function pollAgentReplies() {
  const session = storeConversations[activeStore];
  if (!session || !session.conversation_id) return;

  try {
    const response = await fetch(`${BACKEND_URL}/api/agent-replies/${session.conversation_id}`);
    if (!response.ok) {
      throw new Error(`HTTP response error ${response.status}`);
    }
    const replies = await response.json();
    
    let appendedNew = false;
    replies.forEach(reply => {
      // Check if message is already present (deduplicate by reply.id)
      const alreadyPresent = session.messages.some(msg => msg.id === reply.id);
      if (!alreadyPresent) {
        session.messages.push({
          id: reply.id,
          sender: "bot", // Display agent replies under the 'bot' class/style
          content: reply.message,
          timestamp: reply.created_at
        });
        appendedNew = true;
      }
    });

    if (appendedNew) {
      saveSession();
      renderMessages(activeStore);
      
      // If the chat window is closed, show the red dot notification
      if (!chatWindow.matches(":popover-open")) {
        badgeDot.classList.remove("hidden");
      }
    }
  } catch (error) {
    console.debug("Error polling agent replies:", error);
  }
}

// --------------------------------------------------------------------------
// MULTI-STORE DESIGN RENDERER
// --------------------------------------------------------------------------
function renderStoreLayout(storeId) {
  // Update body store key for CSS variables
  bodyEl.setAttribute("data-store", storeId);
  
  const content = MOCK_STORES_CONTENT[storeId];
  if (!content) return;

  // Update layout typography
  storeTitle.textContent = content.title;
  heroBadge.textContent = content.badge;
  heroTitle.textContent = content.heroTitle;
  heroDesc.textContent = content.heroDesc;
  chatHeaderTitle.textContent = `${content.title} Assistant`;

  // Render product grids
  productGrid.innerHTML = "";
  content.products.forEach(p => {
    const card = document.createElement("div");
    card.className = "product-card";
    card.innerHTML = `
      <div>
        <div class="product-emoji">${p.emoji}</div>
        <h4 class="product-name">${p.name}</h4>
        <p class="product-description">${p.desc}</p>
      </div>
      <div class="product-footer">
        <span class="product-price">${p.price}</span>
        <button class="btn-buy" onclick="alert('Demo: Added ${p.name} to cart!')">Buy Now</button>
      </div>
    `;
    productGrid.appendChild(card);
  });

  // Render suggestion chips
  renderSuggestions(content.suggestions);

  // Redraw message timeline
  renderMessages(storeId);
}

function handleStoreChange(e) {
  activeStore = e.target.value;
  renderStoreLayout(activeStore);
  ensureInitialGreeting(activeStore);
}

// --------------------------------------------------------------------------
// CONVERSATION FLOW ENGINE
// --------------------------------------------------------------------------
function getOrGenerateSession(storeId) {
  if (!storeConversations[storeId]) {
    storeConversations[storeId] = {
      conversation_id: crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2, 15),
      messages: []
    };
    saveSession();
  }
  return storeConversations[storeId];
}

function saveSession() {
  sessionStorage.setItem("shopify_chatbot_conversations", JSON.stringify(storeConversations));
}

function ensureInitialGreeting(storeId) {
  const session = getOrGenerateSession(storeId);
  if (session.messages.length === 0) {
    const content = MOCK_STORES_CONTENT[storeId];
    const greeting = `Hi! Welcome to ${content.title} support. How can I help you today? You can ask about shipping, returns, safety, or diagnostics!`;
    
    session.messages.push({
      sender: "bot",
      content: greeting,
      timestamp: new Date().toISOString()
    });
    saveSession();
    renderMessages(storeId);
    
    // Notify user of new message (show red dot if chat is closed)
    if (!document.getElementById("chat-window").matches(":popover-open")) {
      badgeDot.classList.remove("hidden");
    }
  }
}

function renderSuggestions(suggestions) {
  chatSuggestions.innerHTML = "";
  suggestions.forEach(suggestion => {
    const chip = document.createElement("button");
    chip.className = "suggestion-chip";
    chip.textContent = suggestion;
    chip.addEventListener("click", () => {
      chatInput.value = suggestion;
      chatForm.dispatchEvent(new Event("submit"));
    });
    chatSuggestions.appendChild(chip);
  });
}

function renderMessages(storeId) {
  const session = getOrGenerateSession(storeId);
  
  // Clear chat body, keeping system message placeholder at top if wanted
  chatBody.innerHTML = `
    <div class="system-message">
      Secure connection initialized • Scoped to ${MOCK_STORES_CONTENT[storeId].title}
    </div>
  `;

  session.messages.forEach(msg => {
    appendMessageBubble(msg.sender, msg.content);
  });
  
  scrollToBottom();
}

function appendMessageBubble(sender, text) {
  const bubble = document.createElement("div");
  bubble.className = `message message-${sender}`;
  bubble.textContent = text;
  chatBody.appendChild(bubble);
}

function scrollToBottom() {
  chatBody.scrollTop = chatBody.scrollHeight;
}

// --------------------------------------------------------------------------
// MESSAGE TRANSACTIONS (fetch backend or fallback)
// --------------------------------------------------------------------------
async function handleFormSubmit(e) {
  e.preventDefault();
  
  const text = chatInput.value.trim();
  if (!text) return;

  chatInput.value = "";
  
  // 1. Save and Render User Message
  const session = getOrGenerateSession(activeStore);
  session.messages.push({
    sender: "user",
    content: text,
    timestamp: new Date().toISOString()
  });
  saveSession();
  appendMessageBubble("user", text);
  scrollToBottom();

  // 2. Insert Typing Indicator
  const typingIndicator = createTypingIndicator();
  chatBody.appendChild(typingIndicator);
  scrollToBottom();

  try {
    // 3. Post to FastAPI backend
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        store_id: activeStore,
        message: text,
        conversation_id: session.conversation_id
      })
    });

    typingIndicator.remove();

    if (!response.ok) {
      throw new Error(`HTTP response error ${response.status}`);
    }

    const data = await response.json();
    
    // 4. Save and Render Bot Response
    session.messages.push({
      sender: "bot",
      content: data.reply,
      timestamp: new Date().toISOString()
    });
    saveSession();
    appendMessageBubble("bot", data.reply);
  } catch (error) {
    console.warn("Backend server connection failed, running offline mock client fallback:", error);
    
    // 5. Offline Fallback simulation (if server is not running)
    setTimeout(() => {
      typingIndicator.remove();
      
      const offlineReply = getOfflineFallbackReply(activeStore, text);
      
      session.messages.push({
        sender: "bot",
        content: offlineReply,
        timestamp: new Date().toISOString()
      });
      saveSession();
      appendMessageBubble("bot", offlineReply);
      scrollToBottom();
    }, 800); // Small typing delay simulation
  }
  
  scrollToBottom();
}

function createTypingIndicator() {
  const container = document.createElement("div");
  container.className = "message message-bot typing-indicator-container";
  container.innerHTML = `
    <div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  return container;
}

// --------------------------------------------------------------------------
// MOCK CLIENT SIDE FALLBACK (When uvicorn server is offline)
// --------------------------------------------------------------------------
function getOfflineFallbackReply(storeId, userText) {
  const cleanText = userText.toLowerCase();
  
  // Notice note telling user about starting the FastAPI server
  const serverNote = "\n\n(⚠️ Note: Backend server is offline, displaying offline simulation reply.)";
  
  if (storeId === "hoverboard_store") {
    if (cleanText.includes("ship") || cleanText.includes("deliver")) {
      return "Hoverboards are shipped within 2-3 business days in the UK." + serverNote;
    }
    if (cleanText.includes("return") || cleanText.includes("refund")) {
      return "We offer a 30-day return policy for unused products in original boxes." + serverNote;
    }
    if (cleanText.includes("battery") || cleanText.includes("charge")) {
      return "Only charge on flat surfaces, do not leave unattended, and use the official charger." + serverNote;
    }
  } else if (storeId === "hcs_gadgets") {
    if (cleanText.includes("warranty")) {
      return "We provide a 12-month manufacturer warranty covering defects." + serverNote;
    }
    if (cleanText.includes("return") || cleanText.includes("fault")) {
      return "Faulty gadgets can be returned for laboratory diagnostics within 14 days." + serverNote;
    }
  } else if (storeId === "aroma_haven") {
    if (cleanText.includes("oil") || cleanText.includes("pets") || cleanText.includes("safe")) {
      return "Always dilute essential oils before skin contact. Do not ingest, and keep away from pets." + serverNote;
    }
    if (cleanText.includes("broken") || cleanText.includes("leak") || cleanText.includes("package")) {
      return "Fragile oils are in bubble sleeves. If broken, email support@aromahaven.co.uk within 48h." + serverNote;
    }
  }
  
  return `Thank you for asking. I didn't recognize that topic offline. Please make sure the FastAPI server is running (port 8000) for active knowledge base lookup.` + serverNote;
}
