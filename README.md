# Hospital Oxygen Plant & Cylinder Monitoring System

## Overview

The Hospital Oxygen Plant & Cylinder Monitoring System is a Django-based web application developed to support the recording, monitoring, and management of oxygen plant measurements in a hospital environment. The system records important operational parameters, including oxygen purity, line pressure, flow rate, and pressure dew point (PDP).

The application allows users to enter daily measurements, review historical records, monitor warning and critical conditions, and acknowledge alerts. It also provides a dashboard that calculates average measurements and presents historical information through visual charts.

I chose this project because of the growth of respiratory diseases and the importance of oxygen availability in hospitals in Malawi. My research experience at Neno District Hospital helped me understand the importance of monitoring oxygen production and maintaining accurate operational records. I wanted to apply what I learned by developing a web application that could help organize monitoring information and make abnormal readings easier to identify.

The system is intended for administrators, technicians, operators, and viewers. In the actual workflow, the operator and technician may be the same person: the individual can enter readings, monitor the results, receive critical notifications, and acknowledge alerts.

## Distinctiveness and Complexity

### Distinctiveness

The Hospital Oxygen Plant & Cylinder Monitoring System is distinctive because it addresses a specialized operational problem rather than a general-purpose application such as an e-commerce store, social network, or email platform. Its purpose is to support oxygen plant monitoring in a hospital context, where accurate records and timely awareness of abnormal readings are important.

The motivation for this project came from my interest in respiratory diseases and concerns about oxygen availability in hospitals in Malawi. Through my research experience at Neno District Hospital, I gained an appreciation of the importance of monitoring oxygen production and keeping reliable operational records. I chose to build a system around this particular problem because I wanted my final project to connect programming with a practical area of need.

The application is designed around oxygen plant measurements rather than generic records. It stores oxygen purity, pressure, flow rate, and pressure dew point, together with information such as the operator, date, time, notes, alert status, and technician acknowledgment. These values are evaluated against configured thresholds, allowing the application to do more than simply store submitted information.

Another distinctive feature is the way the system combines daily data entry, historical reporting, warning conditions, critical alerts, email notifications, and acknowledgment functionality. The operator and technician responsibilities can overlap, so the same person can record measurements and respond to alerts. The application also includes account and role-management functionality for administrators, while viewers are intended to access monitoring information and dashboards.

The project is therefore built around a specific monitoring workflow: recording measurements, evaluating conditions, presenting relevant information, notifying a configured recipient when critical thresholds are reached, and allowing alerts to be acknowledged. This combination of functions is what distinguishes it from a basic CRUD application.

### Complexity

The complexity of this project comes from integrating database design, validation, business logic, alert evaluation, email communication, dashboard calculations, JSON endpoints, authentication, and frontend behavior into one Django application.

One important part of the backend is the relationship between the user responsible for a measurement and the measurement record itself. The daily entry model stores operational values and related information, while validation rules help prevent unreasonable data from being saved. For example, oxygen purity must remain within the 0–100% range, pressure must be positive, and PDP must be below zero. These checks help maintain consistency in the recorded information.

The alert system introduces another layer of logic. The application distinguishes between general alert status and critical conditions. A reading can be evaluated against configured thresholds, while the dashboard also calculates average values over the last 30 days. The dashboard displays warnings when average oxygen purity falls below 93% or average pressure falls below 4.5 bar. Critical individual readings use separate email notification thresholds. Keeping these rules separate required attention to how data is evaluated and how different types of alerts are represented.

A further challenge was deciding how technicians would receive notifications. I explored SMS and email notification services, including Twilio and other platforms. However, many services required payment, and access to foreign currency and international payment methods was a practical difficulty in Malawi. Rather than removing notifications from the project, I explored an alternative and chose Zoho Mail for email delivery through Django's email functionality.

This was not only a coding decision. It required considering the availability, affordability, and practicality of external services in my local environment. The resulting implementation uses configured email settings and a technician notification address. SMS was investigated as an option, but the implemented notification mechanism is email rather than SMS.

The dashboard also adds complexity by calculating averages for oxygen purity, pressure, flow rate, and PDP, retrieving recent records, and preparing data for visual presentation using JavaScript and Chart.js. The application includes JSON endpoints for retrieving measurement records, monthly data, alerts, alert history, and live monitoring information. These endpoints allow the frontend to request structured data without requiring every interaction to be handled through a complete page reload.

Finally, authentication, permissions, user management, and alert acknowledgment connect the monitoring logic to different types of users. Administrators manage users and roles, while the monitoring workflow supports technicians and operators. Together, these components demonstrate the integration of database operations, server-side logic, frontend presentation, external email configuration, and access control in a practical Django application.

The complexity of the project is therefore not based on the number of pages alone. It comes from making the different parts work together to support a real monitoring workflow while adapting the notification design to practical constraints.

## Main Features

### Daily Measurement Entry

Users can submit daily oxygen plant readings, including:

* Oxygen purity
* Pressure
* Flow rate
* Pressure dew point (PDP)
* Operator
* Date and time
* Optional notes

### Dashboard and Reporting

The dashboard displays records from the last 30 days and calculates average oxygen purity, pressure, flow rate, and PDP. It also prepares data for charts to help users review measurement trends.

### Warning Alerts

The dashboard displays warning messages when:

* Average oxygen purity falls below 93%.
* Average pressure falls below 4.5 bar.

These warnings help users identify measurements that may require attention.

### Critical Alerts and Email Notifications

The application evaluates individual measurements against configured critical conditions:

* Oxygen purity below 90%.
* Pressure below 4.0 bar.
* Flow rate below 3.0.
* PDP above -50.0.

When a critical condition is detected through the relevant notification logic, the application attempts to send an email using the configured email settings and technician notification address.

### Alert Acknowledgment

Users with the appropriate permissions can acknowledge alerts. This helps distinguish alerts that have been reviewed from those that remain unacknowledged.

### User and Role Management

The application supports four intended account roles:

* **Admin:** Manages users, roles, and system administration.
* **Technician:** Monitors readings and responds to alerts.
* **Operator:** Enters daily oxygen plant readings.
* **Viewer:** Views monitoring information and dashboards.

The operator and technician responsibilities may be performed by the same person. Actual access to individual actions is controlled by the application's implemented authentication and permission checks.

### JSON API Endpoints

The application provides endpoints for retrieving entries, monthly data, alerts, alert history, and live monitoring information.

## Technologies Used

* Python
* Django
* HTML
* CSS
* JavaScript
* Chart.js
* SQLite
* Django authentication and permissions
* SMTP email configuration
* Zoho Mail for configured email notifications

## Project Structure

### Root Directory

* `manage.py`: Django command-line utility for running the development server, applying migrations, and executing tests.
* `requirements.txt`: Lists Python packages used by the project.
* `README.md`: Documentation for the application, its features, architecture, and setup instructions.
* `.gitignore`: Specifies files and directories that should be excluded from version control.
* `.env`: Local environment configuration. It should not contain credentials in a public submission.
* `db.sqlite3`: SQLite database used for local development.
* `templates/`: Contains shared and application-specific HTML templates.

### Project Configuration (`oxygen_monitoring_project/`)

* `settings.py`: Contains Django configuration, installed applications, database settings, middleware, static file configuration, email settings, and other project settings.
* `urls.py`: Defines the main URL routing for the project and includes application routes.
* `wsgi.py`: WSGI application entry point.
* `asgi.py`: ASGI application entry point.

### Daily Entries Application (`daily_entries/`)

* `models.py`: Defines the Technician and DailyEntry database models, measurement fields, validation, and alert-related fields.
* `views.py`: Handles measurement submission, dashboard rendering, alert pages, JSON APIs, live monitoring, acknowledgment requests, and user-management views.
* `forms.py`: Defines forms used to collect and validate measurement data.
* `urls.py`: Maps application URLs to their corresponding views.
* `admin.py`: Registers application models with Django's administrative interface.
* `apps.py`: Contains the Django application configuration.
* `context_processors.py`: Provides shared context for templates.
* `serializers.py`: Defines data serialization for supported application data.
* `tables.py`: Contains table configuration for displaying records.
* `migrations/`: Contains database migration files.
* `static/`: Contains application-specific static assets.
* `test/`: Contains application test files.

### Weekly Records Application (`weekly_records/`)

* `models.py`: Defines data structures used by the weekly records application.
* `views.py`: Handles weekly record-related functionality.
* `urls.py`: Defines routes for the weekly records application.
* `admin.py`: Provides administrative registration where configured.
* `migrations/`: Contains database migration files.
* `tests.py` or test files: Contains tests where implemented.

### Alerts Application (`alerts/`)

* `utils.py`: Contains the email notification utility used to send alert messages through Django's email functionality.

### Core Application (`core/`)

Contains core project functionality, including the custom logout view used by the project.

### Templates

The `templates/` directory contains the HTML pages used by the application.

* `base.html`: Shared page structure and navigation.
* `daily_entries/homepage.html`: Main application landing page.
* `daily_entries/entry_form.html`: Measurement entry form.
* `daily_entries/alerts.html`: Alert display page.
* `daily_entries/weekly_dashboard.html`: Dashboard for historical measurements and averages.
* `daily_entries/manage_roles.html`: User role-management interface.
* `daily_entries/register.html`: User registration page.
* `daily_entries/users.html`: User listing and management page.
* `registration/`: Authentication-related templates, including password reset pages.

### Static Files

The static assets include JavaScript and CSS used for dashboard behavior, alert interactions, data presentation, and page styling. The daily entries application includes scripts for application behavior, dashboard functionality, and alert-related interactions.

## Alert Thresholds and Validation

### Validation Rules

The application applies validation to measurement values:

* Oxygen purity must be between 0% and 100%.
* Pressure must be greater than 0 bar.
* PDP must be below 0°C.
* Flow rate must not be negative.

### Alert Status Rules

The model identifies a standard alert when oxygen purity is below 93% or PDP is warmer than -55°C.

The critical flag is set when both conditions are true:

* Oxygen purity is below 93%.
* PDP is warmer than -55°C.

Email notification thresholds are evaluated separately from these model alert-status rules.

These values are software-configured thresholds for this project. They should not be interpreted as approved clinical or engineering safety limits without confirmation from qualified personnel.

## How to Run the Application

### Prerequisites

Before running the application, ensure that you have:

* Python installed.
* pip installed.
* A terminal or command prompt.

### 1. Navigate to the Project Directory

Open a terminal and navigate to the directory containing `manage.py`.

```bash
cd oxygen_monitoring_project
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

On macOS or Linux:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

If model changes have been made and migrations need to be created:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create an Administrator Account

```bash
python manage.py createsuperuser
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

Open the following address in your browser:

```text
http://127.0.0.1:8000/
```

### 7. Run Tests

```bash
python manage.py test
```

## Email Configuration

The application uses Django's email functionality for critical alert notifications.

Email settings can be supplied through environment variables, including:

* `EMAIL_HOST`
* `EMAIL_PORT`
* `EMAIL_USE_TLS`
* `EMAIL_HOST_USER`
* `EMAIL_HOST_PASSWORD`

The technician notification address must also be configured in the project settings.

Sensitive credentials should be stored in environment variables or a local `.env` file excluded from version control. Do not publish email passwords, app passwords, or secret keys in the repository or README.

The email notification feature depends on valid email configuration and network access. The application should be tested with the intended email account before being used in an operational environment.

## Additional Information for CS50 Staff

### Dashboard Data Processing

The dashboard retrieves records from the last 30 days, calculates averages, and prepares JSON data for Chart.js. This allows measurement information to be presented through numerical summaries and visual charts.

### Alert Handling

Warning messages are displayed on the dashboard when average measurements fall below configured thresholds. Critical individual measurements can trigger email notifications. Alert acknowledgment is handled separately so that users can identify alerts that have been reviewed.

### Authentication and Permissions

The application uses Django authentication and permission functionality to restrict access to selected operations, including alert acknowledgment and user management. The intended roles are Admin, Technician, Operator, and Viewer. The operator and technician responsibilities may overlap in actual use.

### Database

The project uses SQLite for local development. Django migrations are used to create and update the database schema.

### Notification Service Decision

I explored SMS and email notification services, including Twilio. Many available services required paid subscriptions or payment methods that were difficult to use in my circumstances in Malawi. I therefore implemented email notifications using Django's email functionality and Zoho Mail configuration. The application implements email alerts; SMS delivery is not included.

### Operational Disclaimer

This project is an educational software application developed as a CS50 final project. Its configured thresholds and alerts are intended to demonstrate monitoring logic and should not replace approved hospital procedures, qualified engineering judgment, or clinical safety systems.

## Acknowledgments

I would like to express my heartfelt gratitude to my mentor, Brian Yu, and my professor, David J. Malan, for their guidance, encouragement, and inspiring teaching.

I am also sincerely grateful to Neno District Hospital for welcoming me and allowing me to conduct my research there. The support and experience I gained during this research contributed significantly to the development of this project.

## Conclusion

The Hospital Oxygen Plant & Cylinder Monitoring System provides a web-based platform for recording, reviewing, and monitoring oxygen plant measurements. By combining data validation, historical reporting, threshold-based alerts, email notifications, alert acknowledgment, and user permissions, the application demonstrates how web technologies can be applied to a specialized operational problem.

The project represents an application of Django and Python to a practical monitoring workflow. It also reflects the need to consider technical limitations and local circumstances when choosing external services. The result is a foundation for further development and evaluation of digital oxygen plant monitoring tools.
