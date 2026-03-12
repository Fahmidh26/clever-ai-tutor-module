# AI Tutor Architecture

> **Canonical reference** — Use this document to understand what runs where. Do not assume experts/chat go to the main site.

---

## Core Rule: Main Site vs Tutor Site

| Responsibility | Where It Runs | Notes |
|----------------|---------------|-------|
| **Authentication** | Main site | OAuth login, token exchange, user profile |
| **Billing** | Main site | Subscriptions, Stripe |
| **Credit / token deduction** | Main site | Reserve, deduct, reconcile |
| **Experts** | Tutor site (local) | Expert catalog, personas |
| **Chat** | Tutor site (local) | AI responses, streaming |
| **Sessions** | Tutor site (local) | Session create/list/get, message persistence |
| **RAG / knowledge base** | Tutor site (local) | Document upload, retrieval |

---

## What the Main Site Provides (Only)

- OAuth 2.0 login flow and JWT tokens
- User profile (`GET /api/user/details`, `GET /api/user`)
- Credit balance and deduction (`GET /api/user/credits`, `POST /api/user/credits/deduct`)
- Model catalog (optional; tutor can use for plan-based access)
- Subscription/plan checks

**The tutor calls the main site only for auth, billing, and credit-related operations.**

---

## What the Tutor Site Implements Locally

- Expert catalog (personas, subjects, modes)
- Chat execution (LLM calls via direct provider APIs)
- Session management (create, list, get)
- Message persistence
- RAG pipeline (when implemented)
- All education-specific logic (hints, mastery, etc.)

**Experts, chat, and sessions do NOT go to the main site.** They are implemented in the tutor backend.

---

## Request Flow Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│ FRONTEND (Next.js)                                                       │
└─────────────────────────────────────────────────────────────────────────┘
         │
         │  Auth: /oauth/login, /oauth/callback, /api/me, /api/logout
         │  Experts: /api/experts
         │  Chat: /api/expert-chat, /api/tutor/sessions/*
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ TUTOR BACKEND (FastAPI)                                                  │
│                                                                          │
│  • Auth routes → OAuth with main site, session stored locally            │
│  • Experts, chat, sessions → LOCAL implementation (no main-site proxy)   │
│  • Credit deduction → Call main site when chat consumes tokens           │
└─────────────────────────────────────────────────────────────────────────┘
         │
         │  Only for: token exchange, user fetch, credit deduct
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ MAIN SITE (C:\AISITENEW)                                                 │
│  Auth, billing, credits only                                             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Common Mistakes to Avoid

1. **Do not** proxy experts or chat to the main site.
2. **Do not** assume `/api/main-site/*` is used for tutor functions — it is only for auth/billing/credits when needed.
3. **Do** implement experts, chat, and sessions as local tutor APIs.
4. **Do** call the main site for credit deduction when a chat consumes tokens.

---

## Implementation Status

> As of the architecture clarification, the codebase may still use the old proxy pattern for experts/chat. Migration to local APIs is required. See `AI_TUTOR_PROGRESS_CHECKLIST.md` for migration tasks.
