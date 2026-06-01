# AI-Enhanced CRM & Ticket Management System

This project is a CRM and support-ticket management MVP for TechServe Solutions. Managers and
support agents can manage customers, track service requests, review activity history, use AI-assisted
ticket tools, and record or send SMTP email notifications.

## Features

- JWT login with hashed passwords
- Manager and Agent role-based access control
- Customer create, view, update, delete, search, and ownership management
- Ticket create, view, update, assignment, filtering, and manager-only deletion
- Ticket comments, internal notes, timestamps, and activity logs
- Dashboard analytics with ticket, customer, category, priority, and agent workload indicators
- Manager-only reports for ownership, service demand, and resolution trends
- AI ticket categorization and sentiment analysis
- AI reply suggestions and ticket summaries
- SMTP email notifications for ticket creation, Critical escalation, and resolution
- Notification history with safe local logging when SMTP is disabled
- SQLite persistence and Docker Compose support

## Tech Stack

### Backend

- FastAPI
- SQLAlchemy
- SQLite
- JWT authentication with PyJWT
- Argon2 password hashing through `pwdlib`

### Frontend

- React
- Vite
- Tailwind CSS
- Axios
- React Router

### AI

- Rule-based local fallback that works without API keys
- Optional OpenAI and Gemini provider adapters

### Messaging

- SMTP email through the Python standard library

## Local Setup

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. Interactive API docs are available at
`http://localhost:8000/docs`.

### Frontend

Open a second PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

The UI runs at `http://localhost:5173`.

### Docker Compose

From the repository root:

```powershell
$env:SECRET_KEY = "replace-this-with-a-long-random-value"
docker compose up --build
```

## Environment Variables

Backend values belong in `backend/.env`. The committed `backend/.env.example` contains placeholders.

| Variable                        | Purpose                                                           |
| ------------------------------- | ----------------------------------------------------------------- |
| `DATABASE_URL`                | SQLAlchemy database URL; defaults to local SQLite                 |
| `SECRET_KEY`                  | Required secret used to sign JWT access tokens                    |
| `ALGORITHM`                   | JWT signing algorithm; defaults to `HS256`                      |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token lifetime; defaults to `60`                            |
| `AI_PROVIDER`                 | AI adapter:`rule_based`, `openai`, or `gemini`              |
| `AI_API_KEY`                  | Optional hosted AI provider API key                               |
| `OPENAI_MODEL`                | OpenAI model identifier                                           |
| `GEMINI_MODEL`                | Gemini model identifier                                           |
| `ENABLE_MESSAGING`            | Set to `true` to send email; defaults to safe logging-only mode |
| `MESSAGING_PLATFORM`          | Messaging adapter; set to `smtp`                                |
| `SMTP_HOST`                   | SMTP server hostname                                              |
| `SMTP_PORT`                   | SMTP server port; defaults to `587`                             |
| `SMTP_USERNAME`               | SMTP account username                                             |
| `SMTP_PASSWORD`               | SMTP password or provider app password                            |
| `SMTP_FROM_EMAIL`             | Sender email address                                              |
| `SMTP_TO_EMAIL`               | Recipient email address for ticket alerts                         |
| `SMTP_USE_TLS`                | Enables STARTTLS before login; defaults to `true`               |
| `VITE_API_URL`                | Frontend API base URL, configured in `frontend/.env`            |

Never commit `.env` files, real API keys, SMTP passwords, or production database files.

## Default Login Credentials

| Role    | Email                   | Password        |
| ------- | ----------------------- | --------------- |
| Manager | `manager@example.com` | `password123` |
| Agent   | `agent@example.com`   | `password123` |

Change these demo credentials before any real deployment.

## Role Rules

- Managers can view all customers and tickets, assign ownership, delete records, view reports, and
  send test email notifications.
- Agents can create customers and tickets, then view and update records assigned to them.
- Agents cannot delete customers or tickets, access manager reports, or view another agent's records.
- Customer deletion is blocked while tickets still reference the customer.

## How To Test AI

1. Sign in and create a ticket with a title and description.
2. Confirm the generated AI category and sentiment appear on the ticket detail page.
3. Select **Generate AI reply suggestion** and review the suggested response.
4. Resolve the ticket to generate a summary automatically.
5. Select **Generate/Refresh summary** to refresh the stored summary manually.

With `AI_PROVIDER=rule_based`, these actions work locally without paid API credentials. To test a
hosted adapter, set `AI_PROVIDER=openai` or `AI_PROVIDER=gemini` and provide `AI_API_KEY`.

## How To Test SMTP Email

1. Add SMTP credentials to `backend/.env`.
2. Set `ENABLE_MESSAGING=true` and `MESSAGING_PLATFORM=smtp`.
3. Create a ticket, escalate a ticket to Critical priority, and resolve a ticket.
4. Check the configured `SMTP_TO_EMAIL` recipient inbox.
5. Review Notification history on the ticket detail page.

For Gmail, use `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_USE_TLS=true`, and a Google App
Password instead of the normal account password. With `ENABLE_MESSAGING=false`, workflows remain
safe and notification attempts are recorded with a `logged` status.

## Project Structure

```text
backend/
  app/
    routers/       FastAPI route modules
    services/      AI and SMTP adapters
    auth.py        JWT and password helpers
    database.py    SQLAlchemy engine and sessions
    models.py      Database entities and relationships
    schemas.py     Pydantic request and response models
    seed.py        Idempotent demo-data seeding
frontend/
  src/
    api/           Axios API clients
    components/    Shared layout and UI components
    context/       Authentication state
    pages/         CRM screens
```

## Screenshots

### Login

[Insert screenshot of login here]

### Dashboard

[Insert screenshot of dashboard here]

### Customers

[Insert screenshot of customer list and customer detail here]

### Tickets

[Insert screenshot of ticket list and ticket detail here]

### Ticket AI Section

[Insert screenshot of AI category, sentiment, suggested reply, and summary here]

### Reports

[Insert screenshot of manager reports here]

### Email Notification

[Insert screenshot of received SMTP email here]

## Known Limitations

- Rule-based AI works without API keys, but real OpenAI or Gemini testing requires valid API keys.
- SMTP delivery requires valid SMTP credentials and provider access.
- SQLite is appropriate for the assignment MVP; a production deployment should use a managed
  relational database and production-grade secret management.

## Submission Notes

Use [SUBMISSION_CHECKLIST.md](./SUBMISSION_CHECKLIST.md) before publishing the GitHub repository and
recording the demo video. Use [REPORT_OUTLINE.md](./REPORT_OUTLINE.md) as the report-writing template.
