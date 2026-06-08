# Backend - Trivia API

## Setting up the Backend

### Install Dependencies

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in `app.py`and can reference `models.py`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

### Set up the Database

With Postgres running, create a `trivia` database:

```bash
createdb trivia
```

Populate the database using the `trivia.psql` file provided. From the `backend` folder in terminal run:

```bash
psql trivia < trivia.psql
```

### Run the Server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## To Do Tasks

These are the files you'd want to edit in the backend:

1. `backend/flaskr/__init__.py`
2. `backend/test_flaskr.py`

One note before you delve into your tasks: for each endpoint, you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior.

1. Use Flask-CORS to enable cross-domain requests and set response headers.
2. Create an endpoint to handle `GET` requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.
3. Create an endpoint to handle `GET` requests for all available categories.
4. Create an endpoint to `DELETE` a question using a question `ID`.
5. Create an endpoint to `POST` a new question, which will require the question and answer text, category, and difficulty score.
6. Create a `POST` endpoint to get questions based on category.
7. Create a `POST` endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.
8. Create a `POST` endpoint to get questions to play the quiz. This endpoint should take a category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.
9. Create error handlers for all expected errors including 400, 404, 422, and 500.

## API Reference

### Getting Started

- Base URL: This app runs locally and is not hosted as a base URL. The backend runs at `http://127.0.0.1:5000/`, which is set as a proxy in the frontend configuration.
- Authentication: This version of the application does not require authentication or API keys.

### Error Handling

Errors are returned as JSON objects in the following format:

```json
{
  "success": false,
  "error": 404,
  "message": "resource not found"
}
```

The API returns the following error types when requests fail:

- 400: Bad Request
- 404: Resource Not Found
- 422: Unprocessable
- 500: Internal Server Error

### Endpoints

#### GET /categories

- Fetches a dictionary of all categories, with `id` as the key and the category type as the value.
- Request Arguments: None
- Returns: An object with `success` and a `categories` object of `id: category_string` pairs.

```json
{
  "success": true,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

#### GET /questions

- Fetches a paginated list of questions (10 per page), the total number of questions, all categories, and the current category.
- Request Arguments: `page` (integer, optional, default `1`)
- Returns: An object with `success`, a list of `questions` for the requested page, `total_questions`, a `categories` object, and `current_category`.
- Errors: Returns 404 if the requested page contains no questions.

```json
{
  "success": true,
  "questions": [
    {
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?",
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4
    }
  ],
  "total_questions": 19,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": null
}
```

#### DELETE /questions/{question_id}

- Deletes the question with the given id.
- Request Arguments: `question_id` (integer, in the URL path)
- Returns: An object with `success` and `deleted`, the id of the removed question.
- Errors: Returns 404 if no question with that id exists.

```json
{
  "success": true,
  "deleted": 5
}
```

#### POST /questions

- Creates a new question.
- Request Body: a JSON object with `question`, `answer`, `category`, and `difficulty`.
- Returns: An object with `success` and `created`, the id of the new question.

```json
{
  "question": "Which planet is known as the Red Planet?",
  "answer": "Mars",
  "category": "1",
  "difficulty": 2
}
```

Response:

```json
{
  "success": true,
  "created": 24
}
```

#### POST /questions/search

- Searches questions whose text contains the search term (case-insensitive).
- Request Body: a JSON object with `searchTerm`.
- Returns: An object with `success`, the matching `questions`, `total_questions` (number of matches), and `current_category`. An empty result returns an empty list, not an error.

```json
{
  "searchTerm": "title"
}
```

Response:

```json
{
  "success": true,
  "questions": [
    {
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?",
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3
    }
  ],
  "total_questions": 2,
  "current_category": null
}
```

#### GET /categories/{category_id}/questions

- Fetches the questions belonging to a specific category.
- Request Arguments: `category_id` (integer, in the URL path)
- Returns: An object with `success`, the `questions` for that category, `total_questions`, and `current_category` (the category type).
- Errors: Returns 404 if no category with that id exists.

```json
{
  "success": true,
  "questions": [
    {
      "id": 20,
      "question": "What is the heaviest organ in the human body?",
      "answer": "The Liver",
      "category": 1,
      "difficulty": 4
    }
  ],
  "total_questions": 3,
  "current_category": "Science"
}
```

#### POST /quizzes

- Returns one random question to play the quiz, filtered by category and excluding questions already asked.
- Request Body: a JSON object with `previous_questions` (a list of question ids already played) and `quiz_category` (an object with `type` and `id`). Use `id` of `0` to draw from all categories.
- Returns: An object with `success` and a single `question`. When no questions remain, `question` is `null`, which signals the end of the game.

```json
{
  "previous_questions": [1, 4, 20],
  "quiz_category": { "type": "Science", "id": 1 }
}
```

Response:

```json
{
  "success": true,
  "question": {
    "id": 21,
    "question": "Who discovered penicillin?",
    "answer": "Alexander Fleming",
    "category": 1,
    "difficulty": 3
  }
}
```

## Testing

Write at least one test for the success and at least one error behavior of each endpoint using the unittest library.

To deploy the tests, run

```bash
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
