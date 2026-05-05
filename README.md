# Qatar Foundation — Admin Portal

Flask backend for the Qatar Foundation Admin Portal. Supports admin authentication and opportunity management.

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/Hitan547/Test1
cd Test1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python app.py
```

Then open http://localhost:5000

## Project Structure

```
Test1/
├── sky/                    # Original UI files (unchanged)
│   ├── admin.html
│   ├── admin.css
│   └── admin.js
├── static/
│   ├── admin.css           # Original styles (unchanged)
│   └── admin.js            # Wired to Flask APIs
├── templates/
│   ├── admin.html          # Served by Flask
│   ├── reset_form.html     # Password reset form
│   ├── reset_error.html    # Expired/invalid token page
│   └── reset_success.html  # Success confirmation page
├── app.py                  # Flask app + all API routes
├── models.py               # SQLAlchemy DB models
└── requirements.txt
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/signup | Create admin account |
| POST | /api/login | Login + set session |
| POST | /api/logout | Clear session |
| GET | /api/me | Get current admin info |
| POST | /api/forgot-password | Request password reset link |
| GET | /reset-password/\<token\> | Show reset form |
| POST | /reset-password/\<token\> | Submit new password |
| GET | /api/opportunities | List admin's opportunities |
| POST | /api/opportunities | Create new opportunity |
| PUT | /api/opportunities/\<id\> | Update opportunity |
| DELETE | /api/opportunities/\<id\> | Delete opportunity |

## Security

- Passwords hashed with bcrypt (never stored plain)
- Session cookie: HttpOnly, SameSite=Lax
- Ownership enforced: admins can only edit/delete their own opportunities
- Password reset tokens expire in 1 hour, logged to console
- Generic error messages on login (never reveals which field is wrong)
- Remember Me: 30-day session; unchecked: browser-session only
