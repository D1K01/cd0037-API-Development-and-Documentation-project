import os
import unittest

from sqlalchemy import text

from flaskr import create_app
from models import db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_user = "postgres"
        self.database_password = "password"
        self.database_host = "localhost:5432"
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.session.execute(text("DROP TABLE IF EXISTS questions CASCADE"))
            db.session.execute(text("DROP TABLE IF EXISTS categories CASCADE"))
            db.session.commit()
            db.create_all()

            for category_type in ["Science", "Art", "Geography", "History", "Entertainment", "Sports"]:
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
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    def test_get_categories(self):
        res = self.client.get("/categories")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(len(data["categories"]) > 0)

    def test_get_paginated_questions(self):
        res = self.client.get("/questions")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["total_questions"] > 0)
        self.assertEqual(len(data["questions"]), 10)

    def test_404_get_questions_beyond_valid_page(self):
        res = self.client.get("/questions?page=1000")
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")

    def test_create_question(self):
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

    def test_delete_question(self):
        with self.app.app_context():
            question = Question(question="Temp", answer="Temp", category="1", difficulty=1)
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

    def test_404_delete_nonexistent_question(self):
        res = self.client.delete("/questions/100000")
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")

    def test_search_questions(self):
        res = self.client.post("/questions/search", json={"searchTerm": "Sample"})
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["total_questions"] > 0)

    def test_get_questions_by_category(self):
        res = self.client.get("/categories/1/questions")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["total_questions"] > 0)
        self.assertEqual(data["current_category"], "Science")

    def test_404_get_questions_by_invalid_category(self):
        res = self.client.get("/categories/100000/questions")
        data = res.get_json()

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")

    def test_play_quiz(self):
        res = self.client.post("/quizzes", json={
            "previous_questions": [],
            "quiz_category": {"type": "Science", "id": 1}
        })
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["question"])
        self.assertEqual(data["question"]["category"], "1")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
