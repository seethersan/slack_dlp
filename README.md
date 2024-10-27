# Data Loss Prevention (DLP) System

## Overview

This project is a system designed to scan messages and files flowing through communication channels (like Slack) for sensitive information, such as credit card numbers, Social Security Numbers (SSNs), passport numbers, and driver's license numbers. It uses regex patterns to identify sensitive data and reports any matches.

The project consists of:
- A **Django backend** for managing regex patterns, storing scanned message results, and exposing APIs.
- A **DLP Manager** running in a separate container that processes messages asynchronously, using RabbitMQ for local queue management or AWS SQS in production.
- Integration with **Slack** to monitor communication channels and scan messages for sensitive data.

## Architecture

### Components:
1. **Django Application**: 
    - Manages patterns via Django Admin.
    - Exposes two APIs: one for fetching patterns (`/api/patterns/`) and another for saving scan results (`/api/save_match/`).
    - Provides a web interface for monitoring scanned messages.
    - Connected to a MySQL database to store patterns and scan results.
    
2. **DLP Manager**:
    - Listens for messages from RabbitMQ (or SQS in production).
    - Asynchronously processes messages, scanning for sensitive data using regex patterns.
    - Communicates with the Django API to retrieve patterns and store scan results.
    - Runs in its own Docker container.

3. **Message Queue (RabbitMQ or AWS SQS)**:
    - In development, RabbitMQ is used as the message queue.
    - In production, the system can be configured to use AWS SQS.
    - The queue holds messages to be processed by the DLP Manager asynchronously.

4. **Slack Integration**:
    - The Slack Events API is used to listen for messages sent in Slack channels.
    - These messages are forwarded to the message queue for processing by the DLP Manager.

## Project Structure

```
├── README.md
├── app
│   ├── Dockerfile
│   ├── db.sqlite3
│   ├── dlp
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── api
│   │   │   ├── serializers.py
│   │   │   └── views.py
│   │   ├── apps.py
│   │   ├── management
│   │   │   └── commands
│   │   │       └── create_patterns.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_pattern_enabled.py
│   │   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── dlp_project
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── entrypoint.sh
│   ├── manage.py
│   └── requirements.txt
├── dlp_container
│   ├── Dockerfile
│   ├── manager.py
│   ├── requirements.txt
│   ├── run.py
│   └── tasks.py
└── docker-compose.yaml
```

## Prerequisites

- **Docker** and **Docker Compose** installed on your machine.
- A **Slack account** with a Slack App created to use the Events API (see the Slack integration section below).

## Running the Project Locally

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd dlp_project
```

### Step 2: Create the Environment Variables

Create a `.env` file in the app folder of your project to store the necessary environment variables. Example:

```
DJANGO_DEBUG="1"
DJANGO_SECRET_KEY="secret-key"
DJANGO_ALLOWED_HOSTS="*"
DJANGO_CSRF_TRUSTED_ORIGINS="*"
MYSQL_DATABASE="dlp_project"
MYSQL_USER="user"
MYSQL_PASSWORD="password"
MYSQL_HOST="db"
MYSQL_PORT="3306"
QUEUE_SERVICE="rabbitmq"
RABBITMQ_URL="amqp://guest:guest@rabbitmq:5672/"
QUEUE_NAME="dlp_queue"
SLACK_SIGNING_SECRET=""
SLACK_BOT_TOKEN=""
```

Create a `.env` file in the app folder of your project to store the necessary environment variables. Example:

```
QUEUE_SERVICE="rabbitmq"
RABBITMQ_URL="amqp://guest:guest@rabbitmq:5672/"
QUEUE_NAME=""
DLP_API_PATTERNS_URL="http://web:8000/dlp/api/patterns/"
DLP_API_SAVE_MATCH_URL="http://web:8000/dlp/api/save_match/"
```

### Step 3: Build and Run the Containers

Use Docker Compose to build and run the project:

```bash
docker-compose up --build
```

This will start the following services:
- Django application on `http://localhost:8000`
- RabbitMQ (message broker) on `http://localhost:15672`
- DLP Manager to asynchronously process messages.

### Step 4: Create the Default Regex Patterns

Once the project is running, create the default regex patterns by running the following command:

```bash
docker-compose exec web python manage.py create_patterns
```

This command will populate the database with predefined regex patterns for detecting sensitive information like credit card numbers, SSNs, and email addresses.

### Step 5: Access the Admin Interface

To manage regex patterns and view scanned message results, visit the Django admin interface:

```bash
http://localhost:8000/admin/
```

Log in with the superuser credentials you created during the setup process.

## Slack Integration

To integrate with Slack:
1. Create a new Slack App from the Slack API dashboard.
2. Enable Event Subscriptions and configure the request URL to point to your Django app (e.g., `http://your-ngrok-url/slack/events/`).
3. Add the necessary OAuth permissions to allow the app to listen to channel messages (`channels:history`).
4. Use ngrok to expose your local development server to the internet for Slack to send events to your app.

```bash
ngrok http 8000
```

Then set your Event Subscriptions Request URL in Slack to `http://your-ngrok-url/slack/events/`.

## Configuration

### RabbitMQ

RabbitMQ is used as the message broker in local development. The DLP Manager listens to the queue (`dlp_queue`) and processes messages asynchronously.

### AWS SQS (Production)

In production, you can configure the DLP Manager to use AWS SQS instead of RabbitMQ by setting the `QUEUE_SERVICE` environment variable to `sqs` and providing the `AWS_SQS_QUEUE_URL`.

## Testing

To manually test the system:
- Send messages containing sensitive data (e.g., credit card numbers) through Slack or manually via the API.
- The DLP Manager will process the messages and save the results.
- View the scanned messages and detected sensitive data via the Django Admin interface.

## API Endpoints

- `GET /api/patterns/` - Fetch all regex patterns.
- `POST /api/save_match/` - Submit a scanned message result.

## Conclusion

This system is designed to detect sensitive information flowing through communication channels like Slack and store results in a secure database. It can be extended to integrate with more channels and use different patterns for detecting sensitive data.
