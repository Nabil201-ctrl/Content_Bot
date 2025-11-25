# Content Bot API

This is a FastAPI-based content management API for creating, retrieving, updating, and deleting content entries. It uses MongoDB as its database.

## Features

-   **Content Management:** CRUD operations for content (title, body).
-   **MongoDB Integration:** Uses `motor` for asynchronous MongoDB interactions.
-   **FastAPI:** High-performance, easy-to-use web framework.
-   **Pydantic:** Data validation and settings management.
-   **Middleware:** Request timing and simple API key authentication.

## Project Structure

-   `app/main.py`: Main FastAPI application entry point, sets up event handlers, middleware, and routers.
-   `app/db.py`: Handles MongoDB connection and disconnection.
-   `app/models.py`: Defines Pydantic models for content (request, response, update).
-   `app/core/config.py`: Manages application settings loaded from environment variables or `.env` file.
-   `app/middleware.py`: Custom middleware for request timing and authentication.
-   `app/routers/content.py`: API routes for content operations.
-   `app/controllers/content_controller.py`: Business logic for interacting with the database.

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Content_Bot.git
cd Content_Bot
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root directory of the project with the following content:

```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=content_bot_db
APP_HOST=127.0.0.1
APP_PORT=8000
```

-   `MONGO_URI`: Your MongoDB connection string.
-   `DB_NAME`: The name of your MongoDB database.
-   `APP_HOST`: The host for the FastAPI application.
-   `APP_PORT`: The port for the FastAPI application.

### 4. Run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

All endpoints are prefixed with `/contents`.

### Content Operations

#### Create Content

-   **Endpoint:** `POST /contents/`
-   **Description:** Creates a new content entry.
-   **Request Body:**
    ```json
    {
        "title": "My Awesome Content",
        "body": "This is the body of my awesome content."
    }
    ```
-   **Response:** `201 Created`
    ```json
    {
        "id": "60a...123",
        "title": "My Awesome Content",
        "body": "This is the body of my awesome content.",
        "created_at": "2023-10-27T10:00:00.000Z",
        "updated_at": "2023-10-27T10:00:00.000Z"
    }
    ```

#### List All Content

-   **Endpoint:** `GET /contents/`
-   **Description:** Retrieves a list of all content entries with pagination.
-   **Query Parameters:**
    -   `skip` (int, optional): Number of items to skip (default: 0).
    -   `limit` (int, optional): Maximum number of items to return (default: 50, max: 200).
-   **Response:** `200 OK`
    ```json
    [
        {
            "id": "60a...123",
            "title": "Content 1",
            "body": "Body 1",
            "created_at": "2023-10-27T10:00:00.000Z",
            "updated_at": "2023-10-27T10:00:00.000Z"
        }
    ]
    ```

#### Get Content by ID

-   **Endpoint:** `GET /contents/{content_id}`
-   **Description:** Retrieves a single content entry by its unique ID.
-   **Path Parameters:**
    -   `content_id` (str, required): The ID of the content to retrieve.
-   **Response:** `200 OK`
    ```json
    {
        "id": "60a...123",
        "title": "My Awesome Content",
        "body": "This is the body of my awesome content.",
        "created_at": "2023-10-27T10:00:00.000Z",
        "updated_at": "2023-10-27T10:00:00.000Z"
    }
    ```
-   **Error:** `404 Not Found` if content does not exist.

#### Update Content

-   **Endpoint:** `PUT /contents/{content_id}`
-   **Description:** Updates an existing content entry by its ID.
-   **Path Parameters:**
    -   `content_id` (str, required): The ID of the content to update.
-   **Request Body:** (Partial updates allowed)
    ```json
    {
        "title": "Updated Title"
    }
    ```
-   **Response:** `200 OK`
    ```json
    {
        "id": "60a...123",
        "title": "Updated Title",
        "body": "This is the body of my awesome content.",
        "created_at": "2023-10-27T10:00:00.000Z",
        "updated_at": "2023-10-27T11:00:00.000Z"
    }
    ```
-   **Error:** `404 Not Found` if content does not exist.

#### Delete Content

-   **Endpoint:** `DELETE /contents/{content_id}`
-   **Description:** Deletes a content entry by its ID.
-   **Path Parameters:**
    -   `content_id` (str, required): The ID of the content to delete.
-   **Response:** `204 No Content`
-   **Error:** `404 Not Found` if content does not exist.

## Authentication

This application uses a simple API key authentication middleware for non-GET requests.
To make `POST`, `PUT`, or `DELETE` requests, include the `x-api-key` header with the value `expected-secret`.

Example with `curl`:

```bash
curl -X POST \
  http://127.0.0.1:8000/contents/ \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: expected-secret' \
  -d 
    "title": "New Content",
    "body": "This is some new content."
  
```
