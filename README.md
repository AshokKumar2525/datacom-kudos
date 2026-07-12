# Kudos App (Prototype)

This is a minimal prototype of the Kudos feature described in the specification.

Run locally:

Windows PowerShell:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000/ in your browser.

Login: visit `/login` and select a user. The seeded admin user is `Alice (admin)` (id=1).

Notes: This is a prototype. Replace session-based login with real SSO for production.
