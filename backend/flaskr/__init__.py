from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def pagination(request, select):
    """Return the slice of formatted questions for the requested page."""
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in select]
    return questions[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    """
    DONE: Set up CORS. Allow '*' for origins.
    """
    CORS(app, resources={r"/*": {"origins": "*"}})

    with app.app_context():
        db.create_all()

    """
    DONE: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true")
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response

    """
    DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()
        if len(categories) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "categories": {
                category.id: category.type for category in categories
            }
        })

    """
    DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint returns a list of questions, number of total
    questions, current category, and all categories.
    """
    @app.route("/questions", methods=["GET"])
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        current = pagination(request, questions)
        if len(current) == 0:
            abort(404)

        categories = Category.query.order_by(Category.id).all()
        return jsonify({
            "success": True,
            "questions": current,
            "total_questions": len(questions),
            "categories": {
                category.id: category.type for category in categories
            },
            "current_category": None
        })

    """
    DONE:
    Create an endpoint to DELETE a question using a question ID.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        if question is None:
            abort(404)

        question.delete()
        return jsonify({
            "success": True,
            "deleted": question_id
        })

    """
    DONE:
    Create an endpoint to POST a new question, which requires the
    question and answer text, category, and difficulty score.
    """
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        new_question = body.get("question")
        new_answer = body.get("answer")
        new_category = body.get("category")
        new_difficulty = body.get("difficulty")

        # Require non-empty question and answer text.
        if not new_question or not new_answer:
            abort(422)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty,
            )
            question.insert()
        except Exception:
            db.session.rollback()
            abort(422)

        return jsonify({
            "success": True,
            "created": question.id
        })

    """
    DONE:
    Create a POST endpoint to get questions based on a search term.
    It returns any questions for which the search term is a
    substring of the question.
    """
    @app.route("/questions/search", methods=["POST"])
    def search_question():
        body = request.get_json()
        search_term = body.get("searchTerm", None)

        if search_term is None:
            abort(400)

        selection = Question.query.order_by(Question.id).filter(
            Question.question.ilike(f"%{search_term}%")
        ).all()

        current = pagination(request, selection)
        return jsonify({
            "success": True,
            "questions": current,
            "total_questions": len(selection),
            "current_category": None
        })

    """
    DONE:
    Create a GET endpoint to get questions based on category.
    """
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def questions_by_category(category_id):
        category = Category.query.filter(
            Category.id == category_id).one_or_none()
        if category is None:
            abort(404)

        selection = Question.query.order_by(Question.id).filter(
            Question.category == str(category_id)
        ).all()
        current = pagination(request, selection)

        return jsonify({
            "success": True,
            "questions": current,
            "total_questions": len(selection),
            "current_category": category.type
        })

    """
    DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint takes category and previous question parameters
    and returns a random question within the given category,
    if provided, that is not one of the previous questions.
    """
    @app.route("/quizzes", methods=["POST"])
    def quiz():
        body = request.get_json()
        previous_questions = body.get("previous_questions", [])
        category = body.get("quiz_category", None)

        if category is None:
            abort(400)

        category_id = category["id"]

        if category_id == 0:
            questions = Question.query.filter(
                Question.id.notin_(previous_questions)
            ).all()
        else:
            questions = Question.query.filter(
                Question.category == str(category_id),
                Question.id.notin_(previous_questions)
            ).all()

        if len(questions) > 0:
            next_question = random.choice(questions).format()
        else:
            next_question = None

        return jsonify({
            "success": True,
            "question": next_question
        })

    """
    DONE:
    Create error handlers for all expected errors
    including 400, 404, 405, 422, and 500.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
