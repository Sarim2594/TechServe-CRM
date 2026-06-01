# Submission Checklist

Use this checklist before publishing the repository and recording the final demo. Items marked as
verified were exercised during the local final audit. Manual submission tasks remain unchecked.

## Functional Verification

- [X] Backend starts
- [X] Frontend starts
- [X] Manager login works
- [X] Agent login works
- [X] Customer CRUD works
- [X] Ticket CRUD works
- [X] Ticket comments work
- [X] Activity log works
- [X] Dashboard works
- [X] Reports work for manager
- [X] Reports are blocked for agent
- [X] AI category works
- [X] AI sentiment works
- [X] AI reply suggestion works
- [X] AI summary works
- [X] SMTP fallback works without credentials
- [X] SMTP real email tested with credentials
- [X] Notification history works

## Documentation And Submission

- [X] README is complete
- [X] Report outline is complete
- [X] Final report content is complete
- [X] Screenshots are added
- [ ] Demo video is recorded
- [X] Local secret scan is clean
- [ ] GitHub repository is created and accessible

## Security Review

- [X] `.env` files are ignored
- [X] SQLite database files are ignored
- [X] `node_modules`, bytecode, `dist`, and `build` output are ignored
- [X] `.env.example` contains placeholders only
- [ ] Confirm no secrets are present in Git history after repository initialization
