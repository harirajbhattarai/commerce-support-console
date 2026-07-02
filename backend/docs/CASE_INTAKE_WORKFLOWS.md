# Case Intake Workflows
## Phase 5 — Hoverboard Store AI Support Agent

---

## Overview

Case intake is a structured conversation flow that collects all information needed to create a support case before escalating to a human agent. The bot guides the customer through a series of questions and creates a `support_cases` record in Supabase with a unique case reference.

---

## Supabase Table: `support_cases`

```sql
CREATE TABLE support_cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  case_reference TEXT UNIQUE NOT NULL,   -- e.g. "HC-20260702-0001"
  session_id TEXT NOT NULL,
  store_id TEXT NOT NULL DEFAULT 'hoverboard_store',
  case_type TEXT NOT NULL,               -- see types below
  status TEXT NOT NULL DEFAULT 'open',   -- open / under_review / resolved / closed
  order_number TEXT,
  product_name TEXT,
  customer_description TEXT,
  evidence_urls TEXT[],                  -- photos/videos if provided
  bot_summary TEXT,
  assigned_to TEXT,                      -- staff member name or ID
  staff_notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  resolved_at TIMESTAMPTZ
);
```

---

## Case Types

| Case Type | Trigger Intent | Priority |
| :--- | :--- | :--- |
| `return_request` | return_request | Normal |
| `warranty_fault` | warranty_fault | Normal |
| `damaged_on_arrival` | damaged_on_arrival | High |
| `missing_part` | missing_part | Normal |
| `wrong_item` | wrong_item | High |
| `charging_issue` | charging_issue | Normal |
| `stopped_working` | stopped_working | Normal |

---

## Case Reference Format

`HC-YYYYMMDD-NNNN`

Example: `HC-20260702-0047`

Where `NNNN` is a zero-padded sequential counter that resets daily.

---

## Intake Conversation Flows

### 1. Return Request

```
Bot: "I can help you start a return.
      Can I get your order number please?"
Customer: provides order number

Bot: "And could you confirm the email address on the order?"
Customer: provides email

Bot: "What is the reason for your return?"
Customer: provides reason

Bot: "Is the item in its original, unused condition and packaging?"
Customer: confirms

Bot: "I've created return case HC-XXXXXXXX-XXXX for you.
      Our team will review and send return instructions to your email shortly.
      You can also email contact@hoverboardstore.co.uk quoting your case reference."
```

**Required fields**: order_number, email, return_reason, item_condition  
**Optional fields**: evidence_urls (photos of condition)

---

### 2. Warranty Fault

```
Bot: "I'm sorry to hear about the fault. Let me log this for you.
      Can I get your order number please?"
Customer: provides order number

Bot: "When did you purchase the product?"
Customer: provides date or says "a few months ago"

Bot: "Can you describe the fault in as much detail as possible?"
Customer: provides description

Bot: "If you have any photos or videos showing the fault, please share them here —
      this will help our team process your case faster."
Customer: shares or skips

Bot: "I've created warranty case HC-XXXXXXXX-XXXX.
      Our support team will review your case within 1-2 business days and contact you here or by email.
      You can also email contact@hoverboardstore.co.uk quoting your case reference."
```

**Required fields**: order_number, fault_description, purchase_date (approximate)  
**Optional fields**: evidence_urls

---

### 3. Damaged on Arrival

```
Bot: "I'm really sorry to hear your order arrived damaged.
      Let's get this sorted quickly.
      Can I get your order number please?"

Bot: "Could you describe the damage?"

Bot: "Please share photos of the damaged item and packaging if you can —
      this is important for processing your case."

Bot: "I've created damaged-on-arrival case HC-XXXXXXXX-XXXX.
      Our team will review this as a priority. You'll hear back shortly."
```

**Required fields**: order_number, damage_description  
**Strongly required**: evidence_urls (photos of damage AND packaging)  
**Priority**: HIGH — dashboard must flag as priority case

---

### 4. Missing Part

```
Bot: "Let me log a missing part report for you.
      Can I get your order number?"

Bot: "What part or accessory is missing from your order?"

Bot: "Was the packaging sealed and undamaged when you received it?"

Bot: "I've created missing part case HC-XXXXXXXX-XXXX.
      Our team will verify and send the missing part if confirmed."
```

**Required fields**: order_number, missing_part_description, packaging_condition

---

### 5. Wrong Item Received

```
Bot: "I'm sorry you received the wrong item.
      Let's get this corrected.
      Can I get your order number?"

Bot: "What did you order, and what did you receive instead?"

Bot: "Please share a photo of what you received if you can."

Bot: "I've created wrong item case HC-XXXXXXXX-XXXX.
      Our team will arrange the correct item and a collection of the wrong one."
```

**Required fields**: order_number, item_ordered, item_received  
**Required**: evidence_urls

---

### 6. Charging Issue

```
Bot: "Let me help diagnose your charging issue.
      First — do you notice any burning smell, smoke, sparks, or the charger getting unusually hot?"

  ├── YES: [IMMEDIATELY route to battery_safety_high_risk — provide safety guidance + escalate]
  └── NO: Continue intake

Bot: "Can you describe exactly what happens when you plug in the charger?
      For example: no light, wrong colour light, intermittent charging, etc."

Bot: "I've logged a charging issue case HC-XXXXXXXX-XXXX.
      Our team will follow up with diagnostic steps or a replacement if needed."
```

**Required fields**: order_number (optional for first contact), charging_description, safety_check_passed

---

### 7. Stopped Working

```
Bot: "Let me try to help. Has the hoverboard stopped working completely,
      or is it a specific issue like lights, wheels, or sound?"

Bot: "Have you already tried: charging fully, pressing and holding the power button,
      and placing it on a flat surface to recalibrate?"

  ├── Not tried yet: Provide reset/charge steps. Offer to create case if steps fail.
  └── Already tried and failed: Continue intake.

Bot: "I've created a case HC-XXXXXXXX-XXXX.
      Our technical team will review and advise on warranty repair or replacement."
```

**Required fields**: issue_description, troubleshooting_steps_tried

---

## Dashboard Case View Requirements (Phase 5)

- New "Cases" tab in admin dashboard
- Case list: case_reference, case_type, status, created_at, session_id
- Case detail: all fields + conversation history link
- Status update control: open → under_review → resolved → closed
- Priority flag for `damaged_on_arrival` and `wrong_item` cases

---

## New API Endpoints (Phase 5)

```
POST /api/cases                         — Create new support case
GET  /api/cases                         — List all cases (admin auth)
GET  /api/cases/{case_reference}        — Get case detail
PATCH /api/cases/{case_reference}       — Update case status/notes (admin auth)
```
