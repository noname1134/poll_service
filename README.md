# Poll Service

A REST API for managing multiple-choice questions, collecting answers from registered users, and retrieving voting statistics.

Built with **Python, FastAPI, and MySQL**, with **Docker Compose** for local deployment.

## Features

- Create, retrieve, update, and delete questions.
- Support four answer options per question.
- Verify user registration through a separate User Service.
- Enforce one answer per user per question.
- Update existing answers.
- Retrieve or delete a user's answers.
- Retrieve voting statistics for individual questions or all questions.
- Validate requests with Pydantic and database constraints.
- Explore endpoints through interactive API documentation.

## Technology Stack

| Component | Technology |
| :--- | :--- |
| Language | Python |
| API framework | FastAPI |
| Validation | Pydantic |
| Database | MySQL 8.4 |
| Database driver | MySQL Connector/Python |
| HTTP client | HTTPX |
| Configuration | Environment variables |
| Containers | Docker and Docker Compose |

## Architecture

The application separates HTTP handling, business logic, and database access.

| File | Responsibility |
| :--- | :--- |
| `main.py` | Application initialization and health endpoint |
| `controllers.py` | API routes and HTTP error responses |
| `services.py` | Business rules and service coordination |
| `repositories.py` | SQL queries and persistence |
| `schemas.py` | Request and response validation |
| `clients.py` | Communication with the User Service |
| `database.py` | MySQL connection configuration |
| `exceptions.py` | Application-specific exceptions |
| `sql/001_create_poll_tables.sql` | Initial database schema |
| `compose.yaml` | Container and network configuration |

Before accepting or updating an answer, the service checks that the question exists and verifies the user's registration through the User Service.

## Database Design

### Questions

Each question contains an automatically generated ID, a title, and four answer options.

### Answers

Each answer contains:

| Field | Description |
| :--- | :--- |
| `user_id` | ID of the user submitting the answer |
| `question_id` | ID of the question being answered |
| `selected_option` | Selected option, between `1` and `4` |

**Design decisions:**

- A composite primary key on `(user_id, question_id)` prevents duplicate answers.
- A database `CHECK` constraint restricts selected options to `1–4`.
- `ON DELETE CASCADE` removes answers when their question is deleted.
- User existence is verified through the User Service rather than a cross-service database foreign key.

## Getting Started

### Prerequisites

- Docker with Docker Compose.
- A compatible User Service.
- Available local ports `8001` and `3308`.

### 1. Clone the repository

```bash
git clone https://github.com/noname1134/poll_service.git
cd poll_service
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Replace the example database passwords in `.env`.

| Variable | Purpose |
| :--- | :--- |
| `MYSQL_DATABASE` | Database name |
| `MYSQL_USER` | Application database user |
| `MYSQL_PASSWORD` | Application database password |
| `MYSQL_ROOT_PASSWORD` | MySQL root password |
| `MYSQL_HOST` | Database host when running Python locally |
| `MYSQL_PORT` | Database port when running Python locally |
| `USER_SERVICE_URL` | User Service URL when running Python locally |

Docker Compose configures the API to connect to MySQL at `db:3306` and the User Service at `http://user-api:8000`.

> Keep real credentials in `.env`. The committed `.env.example` contains placeholders.

### 3. Prepare the shared network

Create the network if it does not already exist:

```bash
docker network create poll-system
```

The User Service must join this network with the alias `user-api` and listen on container port `8000`.

The Poll Service expects the following endpoint:

```http
GET http://user-api:8000/users/{user_id}
```

A successful response must include an `is_registered` boolean. A missing user should return HTTP `404`.

### 4. Start the services

```bash
docker compose up --build -d
```

MySQL initializes the tables when its database volume is first created.

### 5. Explore the API

| Resource | URL |
| :--- | :--- |
| Swagger UI | http://localhost:8001/docs |
| ReDoc | http://localhost:8001/redoc |
| OpenAPI schema | http://localhost:8001/openapi.json |
| Health endpoint | http://localhost:8001/health |

Check that the API is running:

```bash
curl http://localhost:8001/health
```

Expected response:

```json
{
  "status": "ok"
}
```

> The health endpoint checks API availability. It does not check database or User Service connectivity.

### Useful commands

View API logs:

```bash
docker compose logs -f api
```

Stop the services:

```bash
docker compose down
```

The database volume persists after shutdown. Initialization scripts do not automatically reapply to an existing database volume.

## API Reference

### Questions

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/questions` | Create a question |
| `GET` | `/questions/{question_id}` | Retrieve a question |
| `PATCH` | `/questions/{question_id}` | Update question fields |
| `DELETE` | `/questions/{question_id}` | Delete a question and its answers |

### Answers

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/questions/{question_id}/answers` | Submit an answer |
| `PATCH` | `/questions/{question_id}/answers/{user_id}` | Update an answer |
| `GET` | `/users/{user_id}/answers` | Retrieve a user's answers |
| `DELETE` | `/users/{user_id}/answers` | Delete all answers belonging to a user |

### Statistics and Health

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/questions/{question_id}/statistics` | Statistics for one question |
| `GET` | `/questions/statistics` | Statistics for all questions |
| `GET` | `/health` | Check API availability |

## Example Workflow

### Create a question

```bash
curl -X POST http://localhost:8001/questions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Which programming language do you use most?",
    "option_1": "Python",
    "option_2": "JavaScript",
    "option_3": "Java",
    "option_4": "C++"
  }'
```

### Submit an answer

Use the question ID returned above and the ID of a registered user in the User Service.

This example assumes both IDs are `1`:

```bash
curl -X POST http://localhost:8001/questions/1/answers \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "selected_option": 1
  }'
```

### Retrieve statistics

```bash
curl http://localhost:8001/questions/1/statistics
```

For a question with only the answer above:

```json
{
  "question_id": 1,
  "option_counts": {
    "1": 1,
    "2": 0,
    "3": 0,
    "4": 0
  },
  "total_answers": 1
}
```

## Error Handling

| HTTP Status | Example |
| :--- | :--- |
| `403 Forbidden` | User exists but is not registered |
| `404 Not Found` | Requested question, user, or answer does not exist |
| `409 Conflict` | User has already answered the question |
| `422 Unprocessable Entity` | Invalid request data |
| `503 Service Unavailable` | User Service is unreachable or returns an unexpected HTTP status |
