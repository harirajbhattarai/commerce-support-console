# Human Approval Rules
## Hoverboard Store AI Support Agent

---

## Principle

The bot may **collect**, **classify**, **draft**, and **recommend** — but it may never **decide**, **commit**, or **execute** financial or irreversible actions without a human staff member's explicit approval.

---

## Decision Matrix

| Action | Bot Allowed | Human Approval Required | Notes |
| :--- | :--- | :--- | :--- |
| Answer product question | ✅ Yes | ❌ No | Standard auto-reply |
| Provide delivery policy | ✅ Yes | ❌ No | Standard auto-reply |
| Provide return policy | ✅ Yes | ❌ No | Standard auto-reply |
| Provide warranty policy | ✅ Yes | ❌ No | Standard auto-reply |
| Provide reset/calibration steps | ✅ Yes | ❌ No | Standard auto-reply |
| Provide battery safety guidance | ✅ Yes | ❌ No | Hardcoded safety response |
| Request order verification | ✅ Yes | ❌ No | Must verify before acting |
| Retrieve order status (Phase 4+) | ✅ Yes | ❌ No | Read-only, verified only |
| Retrieve tracking number (Phase 4+) | ✅ Yes | ❌ No | Read-only, verified only |
| Create support case (Phase 5+) | ✅ Yes | ❌ No | Bot creates draft case |
| Draft a customer reply | ✅ Yes | ⚠️ Recommended review | Staff sees draft in dashboard |
| Send draft reply to customer | ❌ No | ✅ Required | Staff must send manually |
| Approve a return request | ❌ No | ✅ Required | Financial commitment |
| Approve a warranty replacement | ❌ No | ✅ Required | Stock and cost commitment |
| Approve a refund | ❌ No | ✅ Required | Financial commitment |
| Cancel an order | ❌ No | ✅ Required | Irreversible action |
| Change a delivery address | ❌ No | ✅ Required | Fraud risk and logistics impact |
| Issue a discount code | ❌ No | ✅ Required | Financial commitment |
| Make a warranty decision (in/out of warranty) | ❌ No | ✅ Required | Legal/policy decision |
| Send any marketplace message (Amazon, eBay) | ❌ No | ✅ Required | Platform policy compliance |

---

## Cases That Always Require Human Escalation

Regardless of phase or AI confidence level, the following must ALWAYS escalate:

1. **Any battery safety report** (smoke, fire, sparks, swelling, burning smell, overheating)
2. **Any legal threat or Trading Standards mention**
3. **Any mention of personal injury from the product**
4. **Any formal complaint** ("I want to make a complaint", "I'm taking legal action")
5. **Any explicit human request** ("I want to speak to a person")
6. **Any order cancellation request**
7. **Any delivery address change request**
8. **Any request involving a child's safety** (injury, dangerous use, age concern)

---

## Draft Reply Approval Flow (Phase 6)

```
Bot generates draft reply
      ↓
Draft stored in reply_drafts table with status: "pending_review"
      ↓
Dashboard shows draft in conversation detail panel
      ↓
Staff reads draft, edits if needed
      ↓
Staff clicks "Send Reply" — reply sent to customer
      ↓
Draft status updated to "sent"
```

Staff must NOT use "Auto-Send Draft" as an option in Phase 6. Auto-send is a Phase 8+ consideration requiring full analytics validation.

---

## Warranty Approval Flow (Phase 6)

```
Bot collects warranty fault details (Phase 5)
      ↓
Case created in support_cases table
      ↓
Staff reviews case and evidence in dashboard
      ↓
Staff makes decision: approve / reject / request more info
      ↓
Staff manually sends response to customer
```

The bot never communicates a warranty approval or rejection decision on behalf of staff.

---

## Refund and Replacement Approval Flow (Phase 6)

```
Bot identifies potential refund/replacement scenario
      ↓
Bot summarises situation in dashboard: "Customer reports [issue] for order #XXXX.
  Suggested action: [refund / replacement]. Requires staff approval."
      ↓
Staff reviews case and approves/rejects in dashboard
      ↓
Staff processes refund/replacement manually in Shopify admin
      ↓
Staff sends confirmation to customer
```

The bot is never involved in executing refunds or replacements in Shopify admin.

---

## Escalation Response Standards

When escalating to a human, the bot must always:

1. Acknowledge the customer's situation
2. Confirm that a human will reply
3. Provide the support email `contact@hoverboardstore.co.uk` as an alternative
4. NOT make promises about timescales unless a specific SLA is set and approved
5. NOT apologise for issues the bot has not verified (e.g. "I'm sorry your item was damaged" before damage is confirmed)

**Correct escalation template**:
> "I've passed this to our support team and a team member will reply here shortly. You can also contact us at contact@hoverboardstore.co.uk."

**Incorrect** (avoid):
> "I'm really sorry your order was damaged, we'll sort this right away and send a replacement."

---

## Staff SLA Targets (Recommended)

| Case Type | Target First Response |
| :--- | :--- |
| Battery safety / fire reports | ≤ 1 hour |
| Damaged on arrival | ≤ 4 hours |
| Wrong item received | ≤ 4 hours |
| Missing part | ≤ 8 hours |
| Return request | ≤ 24 hours |
| Warranty fault | ≤ 48 hours |
| General human request | ≤ 4 hours |
| Complaint | ≤ 2 hours |
