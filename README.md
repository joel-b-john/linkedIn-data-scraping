# LinkedIn-Data-Scraping

This project logs into LinkedIn using Selenium, fetches the logged-in user's profile and connections via LinkedIn's internal Voyager API, and exposes the data through a secure API endpoint.

---

## 📆 Features

* LinkedIn login automation via Selenium
* Fetch logged-in user's public profile and connections
* Stores and reuses session cookies
* DRF-based secure API endpoint (requires user authentication)
* Swagger-compatible API documentation (via drf-spectacular)

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/linkedin-scraper-api.git
cd linkedin-scraper-api
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```
Django>=4.2
djangorestframework>=3.14
drf-spectacular>=0.26.2
selenium>=4.10
webdriver-manager>=3.8.6
requests>=2.31
```

### 4. Run Migrations and Start Server

```bash
python manage.py migrate
python manage.py runserver
```

Once running, access the API at:

```
http://127.0.0.1:8000/api/linkedin/profile/
```

Swagger schema (optional):

```
http://127.0.0.1:8000/api/schema/swagger-ui/
```

---

## 🔐 Authentication

This API uses Django's built-in user model and token/session authentication via DRF. You must be authenticated to use the endpoint.

To obtain an auth token, either:

* Use `djoser`/`rest_framework.authtoken` (add to project)
* Log in via Django admin and include the session cookie in API requests

---

## 📘️ API Documentation

### `POST /api/linkedin/profile/`

**Description:**
Log into LinkedIn using your credentials and return your profile + list of connections.

**Authentication:**
✅ Required (DRF Token or Session Auth)

**Request Body:**

```json
{
  "email": "your_linkedin_email@example.com",
  "password": "your_password"
}
```

**Response:**

```json
{
  "loggedInUser": {
    "firstName": "John",
    "lastName": "Doe",
    "profileId": "123456789",
    "publicProfileUrl": "https://www.linkedin.com/in/john-doe"
  },
  "connections": [
    {
      "firstName": "Jane",
      "lastName": "Smith",
      "occupation": "Software Engineer at ABC Corp",
      "publicProfileUrl": "https://www.linkedin.com/in/jane-smith"
    }
  ],
  "pagination": {
    "start": 0,
    "count": 50,
    "nextStart": 50
  }
}
```

**Errors:**

* `400 Bad Request`: Missing email or password
* `500 Internal Server Error`: Login failed, CAPTCHA triggered, or LinkedIn API failure

---

## ⚠️ Notes

* This tool is for **educational and personal use**. Scraping LinkedIn may violate its [Terms of Service](https://www.linkedin.com/legal/user-agreement).
* CAPTCHA or multi-factor authentication (MFA) may prevent Selenium login in headless mode.
* Store cookies securely (`cookies.json`) to reduce LinkedIn login frequency.

---

## 📁 Project Structure

```
linkedin-data-scraper/
├── core/
│   ├── views.py            # LinkedInProfileView API
│   ├── linkedin.py         # Logic for login, cookies, scraping
├── cookies.json            # Saved session cookies (auto-created)
├── requirements.txt        # Python dependencies
├── manage.py               # Django management
├── README.md               # Project documentation
├── linkedin_scraper/       # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
```

---

## ✨ License

This project is provided for educational purposes only. Use responsibly.
