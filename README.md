# Job & Internship Tracker (v3 — Dark, Animated UI)

A Flask dashboard that pulls live job/internship listings from RemoteOK and
Adzuna APIs, stores them in SQLite, and lets you filter and track your
application status. Email/password auth with Flask-Login.

## What's new in v3

- Full dark theme with glassmorphism (frosted glass cards, blurred backgrounds)
- Animated gradient mesh background that slowly drifts
- Floating glowing orb particles
- Cards fade/slide in on load, staggered for job listings
- Hover lift effects and glow accents throughout
- Same backend as v2 — this is a pure visual upgrade (no logic changes)

## Setup

1. Open this folder in VS Code.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. The `.env` file already has Adzuna API credentials filled in.
4. Delete any old `jobs.db` from a previous version if it exists (schema
   includes a `users` table with `email`).
5. Fetch jobs:
   ```
   python fetch_jobs.py
   ```
6. Run:
   ```
   python app.py
   ```
7. Open `http://localhost:5000` → sign up → log in → enjoy the new look.

## Files

- `app.py` — Flask routes and auth logic (unchanged from v2)
- `database.py` — SQLite setup, user auth, job queries (unchanged from v2)
- `fetch_jobs.py` — pulls listings from RemoteOK + Adzuna APIs (unchanged)
- `templates/login.html` — dark animated login page
- `templates/signup.html` — dark animated signup page with live password checklist
- `templates/index.html` — dark animated dashboard
- `.env` — API keys (never commit this — already in .gitignore)
- `requirements.txt` — Python dependencies

## Security note

Before deploying or pushing to a public GitHub repo, change `app.secret_key`
in `app.py` to a random, unique value via an environment variable.
