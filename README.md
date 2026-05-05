# Qatar Foundation — Admin Portal Backend

Flask backend for the Qatar Foundation Admin Portal. Supports admin auth and opportunity management.

## Setup

```bash
# 1. Clone and enter project
git clone https://github.com/Neerajvs32/Test1
cd Test1

# 2. Copy backend files into the repo root (or run from project folder)
# Make sure qatar_admin/ structure is inside the repo

# 3. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the server
python app.py
```

Then open http://localhost:5000

## Project Structure

```
qatar_admin/
├── app.py                  # Flask app + all API routes
├── models.py               # SQLAlchemy DB models
├── requirements.txt
├── templates/
│   ├── admin.html          # Original UI (unchanged)
│   ├── reset_form.html     # Password reset form
│   ├── reset_error.html    # Expired/invalid token page
│   └── reset_success.html  # Success confirmation page
└── static/
    ├── admin.css           # Original styles (unchanged)
    └── admin.js            # Wired to Flask APIs
```

## API Endpoints

| Method | Endpoint                          | Description                    |
|--------|-----------------------------------|--------------------------------|
| POST   | /api/signup                       | Create admin account           |
| POST   | /api/login                        | Login + set session            |
| POST   | /api/logout                       | Clear session                  |
| GET    | /api/me                           | Get current admin info         |
| POST   | /api/forgot-password              | Request password reset link    |
| GET    | /reset-password/<token>           | Show reset form                |
| POST   | /reset-password/<token>           | Submit new password            |
| GET    | /api/opportunities                | List admin's opportunities     |
| POST   | /api/opportunities                | Create new opportunity         |
| PUT    | /api/opportunities/<id>           | Update opportunity             |
| DELETE | /api/opportunities/<id>           | Delete opportunity             |

## Security

- Passwords hashed with bcrypt (never stored plain)
- Session cookie: HttpOnly, SameSite=Lax
- Ownership enforced: admins can only edit/delete their own opportunities
- Password reset tokens expire in 1 hour, logged to console
- Generic error messages on login (never reveals which field is wrong)
- Remember Me: 30-day session; unchecked: browser-session only
