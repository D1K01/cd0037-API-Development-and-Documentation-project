import unittest

from sqlalchemy import text

from flaskr import create_app
from models import db, Question, Category
from settings import DB_USER, DB_PASSWORD, DB_HOST, DB_TEST_NAME


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case."""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_path = (
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_TEST_NAME}"
        )

        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            db.session.execute(text("DROP TABLE IF EXISTS questions CASCADE"))
            db.session.execute(text("DROP TABLE IF EXISTS categories CASCADE"))
            db.session.commit()
            db.create_all()

            categories = [
                "Science", "Art", "Geography",
                "History", "Entertainment", "Sports",
            ]
            for category_type in categories:
                db.session.add(Category(type=category_type))
            db.session.commit()

            for i in range(12):
                db.session.add(Question(
                    question=f"Sample question {i}",
                    answer=f"Answer {i}",
                    category=str((i % 6) + 1),
                    difficulty=(i % 5) + 1
                ))
            db.session.commit()

    def tearDown(self):
        """Executed after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            
    def test_get_categories_success(self):
        res = self.client.get("/categories")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["categories"]), 6)

    def test_get_categories_failure_404_when_empty(self):
        # Removing all categories should make the endpoint return 404.
        with self.app.app_context():
            db.session.execute(text("DELETE FROM questions"))
            db.session.execute(text("DELETE FROM categories"))
            db.session.commit()

        res = self.client.get("/categories")
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")

    def test_get_categories_failure_405_wrong_method(self):
        res = self.client.post("/categories")
        data = res.get_json()

        self.assertEqual(res.status_code, 405)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "method not allowed")

    def test_get_paginated_questions_success(self):
        res = self.client.get("/questions")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["total_questions"], 12)
        self.assertEqual(len(data["questions"]), 10)
        self.assertTrue(len(data["categories"]) > 0)

    def test_get_questions_second_page_success(self):
        res = self.client.get("/questions?page=2")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["questions"]), 2)

    def test_get_questions_failure_404_beyond_valid_page(self):
        res = self.client.get("/questions?page=1000")
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")

    def test_create_question_success(self):
        res = self.client.post("/questions", json={
            "question": "Who wrote Hamlet?",
            "answer": "Shakespeare",
            "category": "2",
            "difficulty": 2
        })
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["created"])

        with self.app.app_context():
            created = db.session.get(Question, data["created"])
            self.assertIsNotNone(created)

    def test_create_question_failure_422_missing_fields(self):
        res = self.client.post("/questions", json={
            "question": "",
            "answer": "",
            "category": "1",
            "difficulty": 1
        })
        data = res.get_json()

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "unprocessable")

    def test_create_question_failure_400_no_body(self):
        res = self.client.post(
            "/questions",
            data="not json",
            content_type="application/json",
        )
        data = res.get_json()

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "bad request")

    def test_delete_question_success(self):
        with self.app.app_context():
            question = Question(
                question="Temp", answer="Temp", category="1", difficulty=1
            )
            question.insert()
            question_id = question.id

        res = self.client.delete(f"/questions/{question_id}")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["deleted"], question_id)

        with self.app.app_context():
            deleted = db.session.get(Question, question_id)
        self.assertIsNone(deleted)

    def test_delete_question_failure_404_nonexistent(self):
        res = self.client.delete("/questions/100000")
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")

    def test_search_questions_success(self):
        res = self.client.post(
            "/questions/search", json={"searchTerm": "Sample"}
        )
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["total_questions"], 12)

    def test_search_questions_success_no_results(self):
        res = self.client.post(
            "/questions/search", json={"searchTerm": "zzzznomatch"}
        )
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(len(data["questions"]), 0)

    def test_search_questions_failure_400_missing_term(self):
        res = self.client.post("/questions/search", json={})
        data = res.get_json()

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "bad request")

    def test_get_questions_by_category_success(self):
        res = self.client.get("/categories/1/questions")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["total_questions"] > 0)
        self.assertEqual(data["current_category"], "Science")

    def test_get_questions_by_category_failure_404_invalid_category(self):
        res = self.client.get("/categories/100000/questions")
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")

    def test_play_quiz_success(self):
        res = self.client.post("/quizzes", json={
            "previous_questions": [],
            "quiz_category": {"type": "Science", "id": 1}
        })
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["question"])
        self.assertEqual(data["question"]["category"], "1")

    def test_play_quiz_success_all_categories(self):
        res = self.client.post("/quizzes", json={
            "previous_questions": [],
            "quiz_category": {"type": "click", "id": 0}
        })
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["question"])

    def test_play_quiz_failure_400_missing_category(self):
        res = self.client.post("/quizzes", json={"previous_questions": []})
        data = res.get_json()

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "bad request")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
