/* =========================================================================
   SHOPIFY EMBEDDED WIDGET JS ENGINE
   Handles isolated DOM events and connects to local or production API.
   ========================================================================= */

(function () {
  // 1. Load Configurations from Global Config or Default Fallback
  const CONFIG = window.HBS_CHAT_CONFIG || {
    storeId: "hoverboard_store",
    apiHost: "http://127.0.0.1:8000"
  };

  const API_ENDPOINT = `${CONFIG.apiHost}/api/chat`;

  // Brand Accent Configuration per Store (Sets CSS Variables Dynamically)
  const BRAND_THEMES = {
    hoverboard_store: { accent: "#00f3ff", hover: "#00cbd4", title: "Hoverboard UK Support", suggestions: ["Shipping Times", "Return Policy", "Battery Safety"] },
    hcs_gadgets: { accent: "#b5179e", hover: "#7209b7", title: "HCS Gadgets Support", suggestions: ["Warranty Policy", "Diagnostic Check"] },
    aroma_haven: { accent: "#588157", hover: "#3a5a40", title: "Aroma Haven Support", suggestions: ["Essential Oils Guide", "Leaking Package"] }
  };

  // 2. Fetch Theme Details for Selected Store
  const storeTheme = BRAND_THEMES[CONFIG.storeId] || BRAND_THEMES["hoverboard_store"];

  // 3. Initialize DOM Elements once the script is loaded
  document.addEventListener("DOMContentLoaded", () => {
    // Inject accent color variables into container
    const container = document.querySelector(".hbs-chat-container");
    if (container) {
      container.style.setProperty("--hbs-chat-accent", storeTheme.accent);
      container.style.setProperty("--hbs-chat-accent-hover", storeTheme.hover);
    }

    const fabBtn = document.getElementById("hbs-chat-fab");
    const chatWin = document.getElementById("hbs-chat-window");
    const closeBtn = document.getElementById("hbs-chat-close");
    const chatBody = document.getElementById("hbs-chat-body");
    const chatForm = document.getElementById("hbs-chat-form");
    const chatInput = document.getElementById("hbs-chat-input");
    const chatSuggestions = document.getElementById("hbs-chat-suggestions");
    const unreadDot = document.getElementById("hbs-chat-unread-dot");
    const titleEl = document.querySelector(".hbs-chat-title");

    if (titleEl) {
      titleEl.textContent = storeTheme.title;
    }

    let conversationId = "";
    let messages = [];

    // Load active session from sessionStorage
    const sessionKey = `hbs_chat_session_${CONFIG.storeId}`;
    const cachedSession = sessionStorage.getItem(sessionKey);
    if (cachedSession) {
      try {
        const parsed = JSON.parse(cachedSession);
        conversationId = parsed.conversationId || generateUUID();
        messages = parsed.messages || [];
      } catch (e) {
        conversationId = generateUUID();
        messages = [];
      }
    } else {
      conversationId = generateUUID();
    }

    // Toggle Chat Window
    fabBtn.addEventListener("click", () => {
      chatWin.classList.toggle("hbs-chat-open");
      unreadDot.classList.add("hbs-chat-hidden");
      scrollToBottom();
    });

    closeBtn.addEventListener("click", () => {
      chatWin.classList.remove("hbs-chat-open");
    });

    // Handle form submit
    chatForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const userText = chatInput.value.trim();
      if (!userText) return;

      chatInput.value = "";

      // Push user message
      addMessage("user", userText);
      scrollToBottom();

      // Show typing indicator
      const typingIndicator = showTypingIndicator();
      scrollToBottom();

      try {
        const res = await fetch(API_ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            store_id: CONFIG.storeId,
            message: userText,
            conversation_id: conversationId
          })
        });

        typingIndicator.remove();

        if (!res.ok) throw new Error("API Connection failed");

        const data = await res.json();
        addMessage("bot", data.reply);

      } catch (err) {
        console.warn("FastAPI backend is offline. Running offline simulation:", err);
        typingIndicator.remove();
        
        // Simulating matching in offline mode
        const fallbackReply = getOfflineReply(CONFIG.storeId, userText);
        addMessage("bot", fallbackReply);
      }

      scrollToBottom();
    });

    // Populate suggestions
    populateSuggestions(storeTheme.suggestions, chatSuggestions, chatInput, chatForm);

    // Initial greeting if session is fresh
    if (messages.length === 0) {
      addMessage("bot", `Hello! Thanks for visiting us. How can I help you today?`);
      if (!chatWin.classList.contains("hbs-chat-open")) {
        unreadDot.classList.remove("hbs-chat-hidden");
      }
    } else {
      // Repopulate older messages
      messages.forEach(msg => appendBubble(msg.sender, msg.content));
    }

    function addMessage(sender, content) {
      messages.push({ sender, content });
      sessionStorage.setItem(sessionKey, JSON.stringify({ conversationId, messages }));
      appendBubble(sender, content);
    }

    function appendBubble(sender, content) {
      const bubble = document.createElement("div");
      bubble.className = `hbs-chat-message hbs-chat-message-${sender}`;
      bubble.textContent = content;
      chatBody.appendChild(bubble);
    }

    function showTypingIndicator() {
      const indicator = document.createElement("div");
      indicator.className = "hbs-chat-message hbs-chat-message-bot hbs-chat-typing-container";
      indicator.innerHTML = `
        <div class="hbs-chat-typing">
          <div class="hbs-chat-dot"></div>
          <div class="hbs-chat-dot"></div>
          <div class="hbs-chat-dot"></div>
        </div>
      `;
      chatBody.appendChild(indicator);
      return indicator;
    }

    function scrollToBottom() {
      chatBody.scrollTop = chatBody.scrollHeight;
    }
  });

  // Auxiliary UUID Generator
  function generateUUID() {
    return crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2, 15);
  }

  // Populate Suggestion Chips
  function populateSuggestions(chips, parentEl, inputEl, formEl) {
    if (!parentEl) return;
    parentEl.innerHTML = "";
    chips.forEach(chipText => {
      const chip = document.createElement("button");
      chip.className = "hbs-chat-chip";
      chip.textContent = chipText;
      chip.addEventListener("click", () => {
        inputEl.value = chipText;
        formEl.dispatchEvent(new Event("submit"));
      });
      parentEl.appendChild(chip);
    });
  }

  // Client-side fail-safe fallback
  function getOfflineReply(storeId, text) {
    const query = text.toLowerCase();
    const serverNote = "\n\n(⚠️ Live Chatbot Server is offline. Showing simulated offline reply.)";
    
    if (storeId === "hoverboard_store") {
      if (query.includes("ship") || query.includes("deliver")) {
        return "We ship hoverboards in the UK in 2-3 business days." + serverNote;
      }
      if (query.includes("return") || query.includes("refund")) {
        return "You can return your hoverboard in original packaging within 30 days." + serverNote;
      }
      if (query.includes("battery") || query.includes("charge")) {
        return "Always charge on flat surfaces, do not leave unattended, and use the official charger." + serverNote;
      }
    } else if (storeId === "hcs_gadgets") {
      if (query.includes("warranty")) {
        return "We provide a 12-month manufacturer warranty covering defects." + serverNote;
      }
      if (query.includes("return") || query.includes("fault")) {
        return "Faulty gadgets can be returned for laboratory diagnostics within 14 days." + serverNote;
      }
    } else if (storeId === "aroma_haven") {
      if (query.includes("oil") || query.includes("pets") || query.includes("safe")) {
        return "Dilute essential oils before skin contact. Do not ingest, and keep away from pets." + serverNote;
      }
      if (query.includes("broken") || query.includes("leak") || query.includes("package")) {
        return "If glass bottles leak or arrive broken, email support@aromahaven.co.uk within 48h." + serverNote;
      }
    }
    
    return "I didn't recognize that topic offline. Please make sure the FastAPI backend is running locally.";
  }
})();
