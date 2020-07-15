import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = "postgres://{}:{}@{}/{}".format("duke", "Time@1234","localhost:5432","trivia")
        setup_db(self.app)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    #TEST for successfully getting categories
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"],True)
        self.assertTrue(len(data["categories"])>0)


    #TEST for successfully getting paginated questions
    def test_get_paginated_questions(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['totalQuestions']>0)
        self.assertTrue(len(data["categories"])>0)

    # TEST for deleting a specific question
    def test_delete_specific_question(self):
        res = self.client().delete("/questions/10")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['deleted']>0)

    # TEST for getting 404 while deleting a specific question
    def test_404_delete_specific_question(self):
        res = self.client().delete("/questions/1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

    # TEST for posting new question
    def test_post_new_question(self):

        new_question = {
            'question' : 'Who was the lead in Iron Man movie?',
            'answer': 'Robert Downey',
            'difficulty': 2,
            'category': 4
        }
        res = self.client().post("/questions", json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # TEST for 400 error missing argument. Here, category is missing
    def test_400_new_question_missing_argument(self):

        new_question = {
            'question' : 'Who was the lead in Iron Man movie?',
            'answer': 'Robert Downey',
            'difficulty': 2
        }
        res = self.client().post("/questions", json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)

    # TEST for successfully searching a question
    def test_search_a_question(self):

        json_search_term = {
            'searchTerm': 'Who invented Peanut Butter?'
        }
        res = self.client().post("/search", json=json_search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # TEST for 422 when search term not provided
    def test_422_search_term_not_provided(self):

        json_search_term = {
            'searchTerm': ''
        }
        res = self.client().post("/search", json=json_search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)

    # TEST for 404 when question is not found
    def test_404_question_not_found(self):

        json_search_term = {
            'searchTerm': 'This is going to find this search string but is not contained in any question'
        }
        res = self.client().post("/search", json=json_search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

    # TEST for getting question based on categories
    def test_get_question_based_on_categories(self):

        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions'])>0)
        self.assertEqual(data['current_category'], 1)

    # TEST for category_id not given
    def test_400_category_id_not_found(self):

        res = self.client().get("/categories//questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)

    # TEST for quiz without quiz_category
    def test_400_quiz_category_not_given(self):

        json_quiz = {
            'previous_questions' : [1,12,7]            
        }
        res = self.client().post('/quiz', json = json_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
