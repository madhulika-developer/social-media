# 🌐 SocialApp - Full-Stack Social Media Platform

A clean, modern, responsive full-stack social media web application built using **Django** and **Python**, designed to connect users and facilitate seamless content sharing. The application features full user authentication, dynamic profile management, and a live post feed, deployed directly on Render.

## 🚀 Key Features

### 1. User Authentication & Security:
* **Secure Registration:** Dynamic user onboarding flow verifying credential parameters and password strength natively.
* **Session Management:** Robust built-in login, logout, and token authorization states handled securely through Django sessions.
* **Validation Guards:** Strict backend password checks preventing weak or common credentials from accessing user data.

### 2. Interactive Feed & Social Dynamics:
* **Unified News Feed:** A centralized dashboard displaying real-time text and media status updates from registered profiles.
* **Dynamic Post Publishing:** Instant status and image upload capabilities supporting multiple media asset types.
* **Responsive Interactions:** Tailored dashboard layouts accommodating timeline viewing on both mobile and desktop screens.

### 3. Profile Architecture:
* **Custom User Spaces:** Dedicated user landing pages aggregating personal status history, custom avatars, and bio details.
* **Flexible Customization:** Direct form interfaces allowing instant changes to registration profiles, profile fields, and display details.

## 🛠️ Tech Stack

* **Backend Framework:** Django (Python 3)
* **Production Server:** Gunicorn WSGI
* **Hosting Platform:** Render Cloud Infrastructure
* **Frontend Basics:** HTML5, CSS3, JavaScript (Django Template System)

## 💻 Local Setup & Deployment

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run local server:**
   ```bash
   python manage.py runserver
   ```
