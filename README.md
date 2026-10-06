# Job & Internship Tracker

A full-stack web application that pulls live job and internship listings from RemoteOK and Adzuna APIs, stores them in SQLite, and lets users track their application status. 

## 🚀 Live Demo
**[Click here to view the live app!](https://job-tracker-app-qry5.onrender.com)**

*(Note: Because this is hosted on Render's free tier, it may take 30-50 seconds to "wake up" on the first visit).*

## Features
- **User Authentication:** Secure signup and login using Flask-Login and Werkzeug password hashing.
- **Live Job Fetching:** Integrates with RemoteOK and Adzuna APIs to fetch real-time job listings.
- **Category Filters:** Easily filter jobs by Tech, Non-Tech, or Design using the dynamic dashboard.
- **Application Tracking:** Mark jobs as "Interested" or "Applied" and view stats on your dashboard.
- **Modern UI:** Dark theme with glassmorphism, animated particle background, and hover effects.

## Tech Stack
- **Backend:** Python, Flask, Flask-Login, Gunicorn
- **Frontend:** HTML, CSS, JavaScript (Vanilla), Jinja2
- **Database:** SQLite
- **Deployment:** Render

## Local Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/prakhar-d/job-tracker-app.git
   