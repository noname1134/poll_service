# Poll Service

[![Python CI](https://github.com/noname1134/poll_service/actions/workflows/ci.yml/badge.svg)](https://github.com/noname1134/poll_service/actions/workflows/ci.yml)

A REST API for managing multiple-choice questions, collecting answers from registered users, and retrieving voting statistics.

Built with **Python, FastAPI, and MySQL**, with **Docker Compose** for local deployment and **GitHub Actions** for automated testing.

Part of a two-service polling system alongside [User Service](https://github.com/noname1134/user_service). Each service owns its database and communicates over HTTP.

[Getting Started](#getting-started) · [API Reference](#api-reference) · [Example Workflow](#example-workflow) · [Testing](#testing)

## Features

- Create, retrieve, update, and delete questions.
- Support four answer options per question.
- Verify user registration through a separate User Service.
- Enforce one answer per user per question.
- Update existing answers.
- Retrieve or delete a user's answers.
- Retrieve voting statistics for individual questions or all questions.
- Validate requests with Pydantic and database constraints.
- Explore endpoints through interactive Swagger documentation.
- Verify voting behavior and database constraints with API and MySQL integration tests.

## Technology Stack

| Component | Technology |
| :--- | :--- |
| Language | Python |
| API framework | FastAPI |
| Validation | Pydantic |
| Database | MySQL 8.4 |
| Database driver | MySQL Connector/Python |
| HTTP client | HTTPX |
| Configuration | Environment variables and python-dotenv |
| Containers | Docker and Docker Compose |
| Testing | pytest and FastAPI TestClient |
| Code quality | Ruff |
| CI | GitHub Actions |

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
| `compose.yaml` | Application containers and shared service network |
| `compose.test.yaml` | Disposable MySQL integration-test database |
| `tests/test_answers.py` | API voting behavior tests |
| `tests/integration/` | Real MySQL constraint and cascade tests |
| `.github/workflows/ci.yml` | Automated lint, formatting, and test checks |

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
- [User Service](https://github.com/noname1134/user_service) for submitting, updating, and retrieving user answers.
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

Both repositories use the external network `poll-system`. Create it once if it does not already exist:

```bash
docker network create poll-system
```

Start User Service using its own README instructions. It must join this network with the alias `user-api` and listen on container port `8000`.

The Poll Service expects the following endpoint:

```http
GET http://user-api:8000/users/{user_id}
```

A successful response must include an `is_registered` boolean. A missing user should return HTTP `404`. User Service calls this service at `http://poll-api:8000` to remove answers before deleting a user profile.

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

### Update an answer

Use `PATCH` to change a previous vote; submitting another `POST` for the same user and question returns `409`.

```bash
curl -X PATCH http://localhost:8001/questions/1/answers/1 \
  -H "Content-Type: application/json" \
  -d '{"selected_option": 2}'
```

## Error Handling

| HTTP Status | Example |
| :--- | :--- |
| `403 Forbidden` | User exists but is not registered |
| `404 Not Found` | Requested question, user, or answer does not exist |
| `409 Conflict` | User has already answered the question |
| `422 Unprocessable Entity` | Invalid request data |
| `503 Service Unavailable` | User Service is unreachable or returns an unexpected HTTP status |

## Testing

Run commands from the repository root using Python 3.10 or newer.

### Install development dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

### API tests

```bash
python -m pytest tests/test_answers.py -v
```

These three tests exercise real routes and service logic while mocking database access and User Service calls:

- A registered user can submit an answer.
- An unregistered user receives `403`, without an answer being written.
- A duplicate-answer repository error is returned as HTTP `409`.

No running MySQL database or User Service is required for this suite. The duplicate API test checks error handling; the integration test below verifies actual database enforcement.

### MySQL integration tests

Start a temporary MySQL 8.4 database and enable the integration tests:

```bash
docker compose -p poll-integration -f compose.test.yaml up -d --wait --wait-timeout 180
RUN_MYSQL_TESTS=1 python -m pytest tests/integration/ -v
```

These two tests use real repository queries to verify:

- Duplicate votes raise `AnswerAlreadyExistsError`, preserve the original answer, and leave exactly one vote.
- Deleting a question cascades to its answers while preserving another question and its answers.

The test database uses port `3309`, dedicated test credentials, and temporary storage. It initializes from `sql/` and does not use the application's database credentials. Each test removes its own records during cleanup.

Stop the test database afterward:

```bash
docker compose -p poll-integration -f compose.test.yaml down
```

Stopping the container discards the temporary database. On Linux, prefix Docker commands with `sudo` if your user lacks access to the Docker socket; run Python commands from the activated virtual environment without `sudo`.

To run all five test cases with the test database running:

```bash
RUN_MYSQL_TESTS=1 python -m pytest tests/ -v
```

Without `RUN_MYSQL_TESTS=1`, the two database tests are skipped.

### Lint and formatting

```bash
ruff check .
ruff format --check .
```

Apply formatting locally with `ruff format .`.

## Continuous Integration

[Python CI](https://github.com/noname1134/poll_service/actions/workflows/ci.yml) runs on every push and pull request using Python 3.10.

| Job | Checks |
| :--- | :--- |
| `checks` | Ruff lint, formatting, and the three API tests; integration tests are skipped |
| `mysql-integration` | Starts MySQL 8.4 and runs the two database integration tests |

The integration job stops the test database even when tests fail.

## Current Limitations

- Authentication and authorization are not implemented. Checking a supplied user's registration does not authenticate the caller.
- Question options are fixed at four per question.
- Cross-service user checks and answer writes are separate operations; concurrent user deletion is not coordinated by a distributed transaction.
- SQL initialization scripts run for a new database volume; schema migrations are not implemented.
- The health endpoint checks API availability rather than database or dependency readiness.
- Automated coverage focuses on voting rules and database constraints; it does not cover every endpoint or a complete two-service deployment.

## Author

[Liad Illouz](https://www.linkedin.com/in/liad-illouz)
