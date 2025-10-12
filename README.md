
<div align="center"> <a href="https://rent.carolinac-e.com/">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://rent.carolinac-e.com/static/CCE-LOGO-WEBSITE-WHITE2.png">
    <source media="(prefers-color-scheme: light)" srcset="https://rent.carolinac-e.com/static/CCE-LOGO-BLACK.png">
    <img alt="CCE" src="https://rent.carolinac-e.com/static/CCE-LOGO-BLACK.png" height="100" >
  </picture>
</a>
 </div>

# CCE Equipment Rental Web Application

This is a Flask-based web application for managing equipment rentals and reservations, specifically tailored for Carolina CE, Inc (CCE). It provides a secure, user-friendly platform for browsing equipment, creating reservations, handling payments, and administrative management. The app supports Google OAuth authentication, Square payment integration, and Azure file storage.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features
- **User Authentication**: Secure login via Google OAuth 2.0 with session management and temporary access tokens for reservations.
- **Equipment Catalog**: Browse equipment by category, view details, and check availability via an interactive calendar.
- **Reservation Management**: Create, view, edit, and sign digital rental agreements for equipment reservations.
- **Profile System**: Users can complete renter profiles, upload ID photos, and manage billing information.
- **Payment Processing**: Integrated Square API for adding billing profiles, credit cards, and processing deposits.
- **Admin Dashboard**: Approve/deny reservations, manage fulfillment status, edit equipment, and generate access links.
- **Document Handling**: PDF generation for rental agreements with e-signing support, stored in Azure Blob Storage.
- **Email Notifications**: Automated admin alerts for new reservations.
- **Error Handling**: Custom pages for authentication, permission, and not-found errors.

## Technologies Used
- **Backend**: Python 3, Flask, Flask-Login
- **Authentication**: Google OAuth 2.0 (oauthlib)
- **Payments**: Square API
- **Database**: Postgres
- **Storage**: Azure Blob Storage
- **PDFs**: Custom generation and e-signing
- **Calendar**: Custom event library
- **Frontend**: Jinja2 templates, HTML/CSS/JavaScript
- **Other**: Requests, Pathlib, Random/String utilities

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/macklellan/cce_equipment_rental_app.git
   cd cce_equipment_rental_app
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the project root with the following:
   ```plaintext
   SECRET_KEY=your_secure_random_key_here
   GOOGLE_CLIENT_ID=your_google_oauth_client_id
   GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
   SQUARE_APP_ID=your_square_application_id
   SQUARE_LOC=your_square_location_id
   SQUARE_ENV=sandbox  # or production
   AZURE_STORAGE_CONNECTION_STRING=your_azure_blob_storage_connection_string
   AZURE_STORAGE_CONTAINER=your_azure_container_name
   EMAIL_SERVICE_HOST=your_email_service_host
   EMAIL_SERVICE_PORT=your_email_service_port
   EMAIL_SERVICE_USER=your_email_service_username
   EMAIL_SERVICE_PASSWORD=your_email_service_password
   ADMIN_EMAILS=admin@email.com (list, separated by single space " ")
   ```
   - `SECRET_KEY`: Random string for Flask session security.
   - `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`: From Google Cloud Console for OAuth.
   - `SQUARE_APP_ID`/`SQUARE_LOC`/`SQUARE_ENV`: From Square Developer Dashboard.
   - `AZURE_STORAGE_CONNECTION_STRING`/`AZURE_STORAGE_CONTAINER`: For Azure Blob Storage (used in `files.py` for image/PDF uploads).
   - `EMAIL_SERVICE_*`: For email notifications (used in `email_lib.py`; e.g., SMTP credentials for services like Gmail or SendGrid).

5. **Initialize Database**:
   Configure `db_lib.py` and run any setup scripts to create necessary tables.

6. **Run the Application Locally**:
   ```bash
   python app.py
   ```
   Access at `https://localhost:5000` (SSL enabled via adhoc context).

## Configuration
- **Flask Settings**:
  - `SESSION_COOKIE_SECURE=True`: Ensures HTTPS-only cookies.
  - `SESSION_COOKIE_SAMESITE=None`: Allows cross-site cookies for OAuth.
  - `PERMANENT_SESSION_LIFETIME=60 minutes`: Session timeout duration.
- **Google OAuth**:
  - Register app in Google Cloud Console; add redirect URI (e.g., `https://yourdomain.com/login/callback`).
- **Square**:
  - Create app in Square Developer Dashboard; use sandbox for testing.
- **Azure Storage**:
  - Set up an Azure Blob Storage account and configure connection strings in `files.py`.
- **Email Notifications**:
  - Configure SMTP settings in `email_lib.py` (e.g., Gmail, SendGrid).
- **Equipment Data**:
  - Update `equipment_defs.py` for categories, pricing, and availability.
- **Database**:
  - Configure connection details in `db_lib.py` (e.g., SQLite or MySQL).

## Usage
1. **Public Access**:
   - Home: `/` – Landing page.
   - Rentals: `/rentals` – Browse categories; `/rentals/<category>` – View equipment list.
   - About/Terms: `/about`, `/terms`, `/terms/reserve`.

2. **User Flow**:
   - Login: `/login` via Google.
   - Profile: `/profile` – Complete renter info and upload ID.
   - Calendar: `/calendar/<equipment>` – Check availability.
   - Reserve: POST to `/reserve/<equipment>` – Create booking.
   - View Reservations: `/reservations`.

3. **Admin Flow** (requires admin user):
   - Reservations: `/admin2` – List, approve/deny, manage status.
   - Users: `/admin/renters` – View renter profiles.
   - Equipment: `/admin/equipment` – Edit catalog.
   - Access Links: `/admin5/<res_id>` – Generate temp access.

4. **Temporary Access**:
   - Use `/logintoken/<code>` for reservation-specific links.

## Directory Structure
```
cce_equipment_rental_app/
├── app.py                  # Main Flask application
├── equipment_defs.py       # Equipment categories, pricing, and details
├── pdfer.py                # PDF rental agreement generation and e-signing
├── user.py                 # User model for Flask-Login
├── db_lib.py               # Database operations (reservations, profiles)
├── calendar_lib.py         # Event calendar for availability
├── square_lib.py           # Square payment integration
├── email_lib.py            # Notification emails
├── files.py                # Azure Blob Storage for images/PDFs
├── templates/              # Jinja2 HTML templates (e.g., index.html, profile.html)
├── static/                 # CSS, JS, images (e.g., favicon.ico)
├── requirements.txt        # Dependencies (Flask, oauthlib, etc.)
├── .env.example            # Environment variable template
└── README.md               # This file
```

## Deployment
For local testing with SSL:
```bash
python app.py  # Runs on https://localhost:5000 with debug mode
```

**Genezio Deployment** (optional):
1. Install Genezio CLI:
   ```bash
   npm install -g genezio
   ```
2. Login: `genezio login`
3. Local Test: `genezio local`
4. Deploy: `genezio deploy`

For production, configure environment variables on your hosting platform (e.g., Heroku, AWS, Vercel). Set `SQUARE_ENV=production` and update `app.config['SERVER_NAME']` if needed. Ensure HTTPS is enforced for OAuth and sessions.

## Contributing
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit changes: `git commit -m "Add your feature"`.
4. Push: `git push origin feature/your-feature`.
5. Open a Pull Request.

Report issues or suggest improvements via GitHub Issues.

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details (add if not present).

## Contact
For support, questions, or collaboration:
- Email: westerncarolinarentals@gmail.com
- GitHub Issues: https://github.com/macklellan/cce_equipment_rental_app/issues
- Genezio Discord (for deployment help): https://discord.gg/uc9H5YKjXv

---

*Built with ❤️ for efficient equipment rentals. © 2025 Ryan McClellan*
