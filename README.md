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
dlp_project/
├── dlp/
│   ├── admin.py                # Django admin setup for managing regex patterns
│   ├── models.py               # Models for Patterns and Scanned Messages
│   ├── serializers.py          # Serializers for API responses
│   ├── views.py                # API views for managing patterns and saving results
│   ├── management/
│   │   └── commands/
│   │       └── create_patterns.py # Management command to create default regex patterns
│   ├── urls.py                 # Django URLs for the API
│   └── ...
├── dlp_manager.py              # DLP Manager for processing messages
├── Dockerfile                  # Dockerfile for the Django app
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # Project readme (this file)
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

Create a `.env` file in the root of your project to store the necessary environment variables. Example:

```
DJANGO_SECRET_KEY=your_secret_key
MYSQL_DATABASE=dlp_project
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_HOST=db
MYSQL_PORT=3306
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
DLP_API_PATTERNS_URL=http://web:8000/dlp/api/patterns/
DLP_API_SAVE_MATCH_URL=http://web:8000/dlp/api/save_match/
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
