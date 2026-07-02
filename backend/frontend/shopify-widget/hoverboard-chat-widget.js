/* =========================================================================
   SHOPIFY EMBEDDED WIDGET JS ENGINE
   Handles isolated DOM events and connects to local or production API.
   ========================================================================= */

(function () {
  // Check if we are running in local development mode
  const isLocalDev = window.location.hostname === "localhost" || 
                     window.location.hostname === "127.0.0.1" || 
                     window.location.hostname.includes("local");

  // Load Configurations from Global Config or Default Fallback
  const globalConfig = window.HBS_CHAT_CONFIG || {};
  let resolvedApiHost = globalConfig.apiHost;
  
  if (!resolvedApiHost) {
    resolvedApiHost = isLocalDev 
      ? "http://127.0.0.1:8000" 
      : "https://commerce-support-console-production.up.railway.app";
  } else if (resolvedApiHost.includes("127.0.0.1") || resolvedApiHost.includes("localhost")) {
    // If it was explicitly set to local API but the user is not on local dev, force fallback to production Railway URL
    if (!isLocalDev) {
      resolvedApiHost = "https://commerce-support-console-production.up.railway.app";
    }
  }

  const CONFIG = {
    storeId: globalConfig.storeId || "hoverboard_store",
    apiHost: resolvedApiHost
  };

  const API_ENDPOINT = `${CONFIG.apiHost}/api/chat`;

  // Dev-only logs helper (silent for customers in production)
  function devLog(message, ...args) {
    if (isLocalDev) {
      console.log(`[HBS_CHAT_DEV] ${message}`, ...args);
    }
  }
  
  function devError(message, ...args) {
    if (isLocalDev) {
      console.error(`[HBS_CHAT_DEV] ${message}`, ...args);
    }
  }

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

      // Question limit checks
      const limitKey = `hbs_chat_question_count_${CONFIG.storeId}`;
      let currentCount = parseInt(sessionStorage.getItem(limitKey) || "0", 10);
      
      const MAX_FREE_QUESTIONS = 5;
      if (currentCount >= MAX_FREE_QUESTIONS) {
        addMessage("bot", `You have reached the maximum number of free support questions (${MAX_FREE_QUESTIONS}) for this session. Please contact support via email if you need further help.`);
        chatInput.value = "";
        return;
      }
      
      // Increment count
      currentCount++;
      sessionStorage.setItem(limitKey, currentCount.toString());

      chatInput.value = "";

      // Push user message
      addMessage("user", userText);
      scrollToBottom();

      // Show typing indicator
      const typingIndicator = showTypingIndicator();
      scrollToBottom();

      try {
        devLog("Sending message to API endpoint:", API_ENDPOINT);
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
        devError("Chatbot backend connection error:", err);
        typingIndicator.remove();
        
        const supportEmails = {
          hoverboard_store: "support@hoverboardstore.co.uk",
          hcs_gadgets: "support@hcsgadgets.co.uk",
          aroma_haven: "support@aromahaven.co.uk"
        };
        const supportEmail = supportEmails[CONFIG.storeId] || "support@hoverboardstore.co.uk";
        addMessage("bot", `Sorry, our support assistant is temporarily unavailable. Please email ${supportEmail}.`);
      }

      scrollToBottom();
    });

    // Populate suggestions
    populateSuggestions(storeTheme.suggestions, chatSuggestions, chatInput, chatForm);

    // Track already rendered human agent replies to avoid duplication
    const seenReplyIds = new Set();
    messages.forEach(msg => {
      if (msg.id) {
        seenReplyIds.add(msg.id);
      }
    });

    // Human Takeover Reply Polling Loop
    let pollInterval = null;
    function startPolling() {
      if (pollInterval) return;
      pollInterval = setInterval(async () => {
        try {
          const res = await fetch(`${CONFIG.apiHost}/api/agent-replies/${conversationId}`);
          if (!res.ok) return;
          const replies = await res.json();
          
          let newReplies = false;
          replies.forEach(reply => {
            if (!seenReplyIds.has(reply.id)) {
              seenReplyIds.add(reply.id);
              addMessage("agent", reply.message, reply.id);
              newReplies = true;
            }
          });
          
          if (newReplies) {
            scrollToBottom();
            if (!chatWin.classList.contains("hbs-chat-open")) {
              unreadDot.classList.remove("hbs-chat-hidden");
            }
          }
        } catch (e) {
          devError("Error polling agent replies:", e);
        }
      }, 5000);
    }
    
    // Start polling loop immediately
    startPolling();

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

    function addMessage(sender, content, id = null) {
      messages.push({ sender, content, id });
      sessionStorage.setItem(sessionKey, JSON.stringify({ conversationId, messages }));
      appendBubble(sender, content);
    }

    function appendBubble(sender, content) {
      // 1. Render small sender label
      const label = document.createElement("div");
      label.className = `hbs-chat-message-label hbs-chat-message-label-${sender}`;
      if (sender === "bot") {
        label.textContent = "Bot assistant";
      } else if (sender === "agent") {
        label.textContent = "Support agent";
      } else {
        label.textContent = "Customer";
      }
      chatBody.appendChild(label);

      // 2. Render bubble
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
})();
