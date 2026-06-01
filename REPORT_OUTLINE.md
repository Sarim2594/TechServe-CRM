# AI-Enhanced CRM & Ticket Management System Report Outline

## 1. Cover Page

- Project title: **AI-Enhanced CRM & Ticket Management System**
- Course name, instructor, semester, and submission date
- Team member names, student IDs, and section
- Repository URL and demo-video URL

## 2. Project Overview

- Describe TechServe Solutions and the need for a centralized customer-support workspace.
- Explain the MVP goal: manage customers and tickets while adding useful AI assistance and SMTP
  notifications.
- Summarize the Manager and Agent roles and their different permissions.
- List the main workflows: login, CRM management, ticket lifecycle, AI assistance, reports, and
  notification history.

[Insert screenshot of login here]

## 3. System Architecture

- Add an architecture diagram showing:
  `React/Vite frontend -> FastAPI API -> SQLAlchemy -> SQLite`.
- Show optional outbound connections:
  `FastAPI -> OpenAI or Gemini API` and `FastAPI -> SMTP email server`.
- Explain the router, service, schema, model, and frontend API-client layers.
- Describe JWT authentication, protected React routes, Axios bearer tokens, and backend dependencies.
- Note that environment variables isolate secrets from committed code.

[Insert architecture diagram here]

## 4. Database Schema

- Add an ER diagram.
- Describe these tables:
  `users`, `customers`, `tickets`, `ticket_comments`, `ticket_activities`, and `notification_logs`.
- Explain the User-to-Customer and User-to-Ticket assignment relationships.
- Explain how tickets retain comments, activity history, AI output, resolution timestamps, and
  notification attempts.
- Mention that ticket deletion cascades to comments, activity entries, and notification logs.

[Insert ER diagram here]

## 5. AI Integration

- Describe the rule-based fallback and why it keeps the MVP usable without paid credentials.
- Explain the optional OpenAI and Gemini adapters configured through environment variables.
- Describe categorization, sentiment analysis, suggested replies, and ticket summaries.
- Explain when AI runs: ticket creation, manual re-analysis, reply generation, resolution, and manual
  summary refresh.
- Include one example ticket input and the generated AI output.
- Document fallback behavior when hosted API credentials are absent or requests fail.

[Insert screenshot of ticket AI section here]

## 6. Messaging Integration

- Explain SMTP email delivery through Python's standard-library `smtplib` and `EmailMessage`.
- Document `ENABLE_MESSAGING`, `MESSAGING_PLATFORM`, and the `SMTP_*` environment variables.
- Explain the three automatic triggers: ticket creation, Critical escalation, and resolution.
- Describe the manager-only test-notification action.
- Explain notification statuses: `logged`, `sent`, `skipped`, and `failed`.
- Note that SMTP failures are logged without breaking ticket workflows.

[Insert screenshot of received email here]

[Insert screenshot of notification history here]

## 7. Feature Screenshots

### Authentication

[Insert screenshot of manager login here]

### Dashboard

[Insert screenshot of dashboard analytics here]

### Customers

[Insert screenshot of customer list here]

[Insert screenshot of customer detail and ticket history here]

### Tickets

[Insert screenshot of ticket list and filters here]

[Insert screenshot of ticket detail, comments, and activity log here]

### Reports

[Insert screenshot of manager reports here]

## 8. Challenges and Learnings

- Discuss implementing JWT authentication and enforcing permissions in both API routes and UI routes.
- Explain relationship and serialization choices for SQLAlchemy and Pydantic.
- Describe the safe AI fallback design and SMTP logging-only mode.
- Mention end-to-end testing lessons: CORS, localStorage token handling, role-based visibility, and
  failure-path testing.
- List realistic future improvements such as PostgreSQL, automated test files, charts, and deployment.

## 9. Work Division

- Add each team member's name and student ID.
- List the modules completed by each member.
- Mention shared work such as testing, report writing, diagrams, and demo preparation.

| Team member | Student ID | Responsibilities |
| --- | --- | --- |
| [Name] | [ID] | [Modules and contributions] |

## 10. References

- FastAPI documentation
- SQLAlchemy documentation
- Pydantic documentation
- React, Vite, Tailwind CSS, Axios, and React Router documentation
- PyJWT and `pwdlib` documentation
- Python `smtplib` and `email.message.EmailMessage` documentation
- OpenAI Responses API documentation, if used
- Gemini GenerateContent API documentation, if used
- Any tutorials, articles, or additional resources referenced during implementation
