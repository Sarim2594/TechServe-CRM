# AI-Enhanced CRM & Ticket Management System

This project is a CRM and support-ticket management MVP for TechServe Solutions. It allows managers
and support agents to manage customers, track service requests, review activity history, use
AI-assisted ticket tools, and send or record SMTP email notifications.

## Team

Group 4
BCS-6J
FAST NUCES
Course: Artificial Intelligence (AI-2002)

| Name                       | Student ID |
| -------------------------- | ---------- |
| Muhammad Sarim Khan Ghouri | 23k-0720   |
| Syeda Hamna Uraizee        | 22k-5112   |
| Sohaib Ahmer               | 22k-4784   |

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
Copy-Item .env.example .env
# Edit .env and replace the SECRET_KEY placeholder before starting the API.
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

Backend values belong in `backend/.env`. Create the local file from the committed placeholder
template, then edit the copied file for your environment:

```powershell
cd backend
Copy-Item .env.example .env
```

At minimum, replace the `SECRET_KEY` placeholder with a long random value before starting the API.
Keep real secrets only in `backend/.env`; never add them to `.env.example`.

| Variable                        | Purpose                                                          |
| ------------------------------- | ---------------------------------------------------------------- |
| `DATABASE_URL`                | SQLAlchemy database URL; defaults to local SQLite                |
| `SECRET_KEY`                  | Required secret used to sign JWT access tokens                   |
| `ALGORITHM`                   | JWT signing algorithm; defaults to`HS256`                      |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token lifetime; defaults to`60`                            |
| `AI_PROVIDER`                 | AI adapter:`rule_based`, `openai`, or `gemini`             |
| `AI_API_KEY`                  | Optional hosted AI provider API key                              |
| `OPENAI_MODEL`                | OpenAI model identifier                                          |
| `GEMINI_MODEL`                | Gemini model identifier                                          |
| `ENABLE_MESSAGING`            | Set to`true` to send email; defaults to safe logging-only mode |
| `MESSAGING_PLATFORM`          | Messaging adapter; set to`smtp`                                |
| `SMTP_HOST`                   | SMTP server hostname                                             |
| `SMTP_PORT`                   | SMTP server port; defaults to`587`                             |
| `SMTP_USERNAME`               | SMTP account username                                            |
| `SMTP_PASSWORD`               | SMTP password or provider app password                           |
| `SMTP_FROM_EMAIL`             | Sender email address                                             |
| `SMTP_TO_EMAIL`               | Recipient email address for ticket alerts                        |
| `SMTP_USE_TLS`                | Enables STARTTLS before login; defaults to`true`               |
| `VITE_API_URL`                | Frontend API base URL, configured in`frontend/.env`            |

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

For final demo evidence, configure real SMTP credentials in `backend/.env`, trigger a ticket
notification, and capture the received email screenshot. Do not commit real SMTP passwords or `.env`
files.

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

![Login](docs/screenshots/01_login_page.png)

### Manager Dashboard

![Manager Dashboard](docs/screenshots/02_manager_dashboard.png)

### Customers

![Customers](docs/screenshots/03_customers_list.png)

### Customer Detail

![Customer Detail](docs/screenshots/04_customer_detail.png)

### Tickets

![Tickets](docs/screenshots/05_tickets_list.png)

### Ticket Detail

![Ticket Detail](docs/screenshots/06_ticket_detail.png)

### AI Insights

![AI Insights](docs/screenshots/07_ai_insights.png)

### AI Reply Suggestion

![AI Reply Suggestion](docs/screenshots/08_ai_reply_suggestion.png)

### Activity Log

![Activity Log](docs/screenshots/09_activity_log.png)

### Notification History

![Notification History](docs/screenshots/10_notification_history.png)

### Reports

![Reports](docs/screenshots/11_reports_page.png)

### Agent Dashboard

![Agent Dashboard](docs/screenshots/12_agent_dashboard.png)

### Agent Restricted Reports

![Agent Restricted Reports](docs/screenshots/13_agent_restricted_reports.png)

### Email Notification

![Email Notification](docs/screenshots/14_email_notification.png)

For a public GitHub repository, personal email addresses in screenshots should be cropped or blurred
before publishing.
