import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, drop_create_tables, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432',
                                                       self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question_1 = {'question': 'Q1?', 'answer': 'A1',
                               'difficulty': 1, 'category': 1}
        self.new_question_2 = {'question': 'Q2?', 'answer': 'A2',
                               'difficulty': 2, 'category': 2}
        self.new_question_3 = {'question': 'Q3?', 'answer': 'A3',
                               'difficulty': 3, 'category': 3}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        questions = Question.query.all()
        for question in questions:
            question.delete()

        categories = Category.query.all()
        for category in categories:
            category.delete()

        pass

    # ////////////////////////////////////////////////////////////////////////////////
    # Tests for successful and un-successful GET requests for all categories
    # ////////////////////////////////////////////////////////////////////////////////
    def test_get_categories_success(self):
        category = Category(type="science")
        category.insert()

        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 1)

        category.delete()

    def test_post_categories_fail(self):
        category = Category(type="science")
        category.insert()

        res = self.client().post('/categories', json={'type': 3})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

        category.delete()

    # ////////////////////////////////////////////////////////////////////////////////
    # Tests for successful and un-successful GET requests for all questions
    # ////////////////////////////////////////////////////////////////////////////////
    def test_get_all_questions_success(self):
        question = Question(question=self.new_question_1['question'],
                            answer=self.new_question_1['answer'],
                            difficulty=self.new_question_1['difficulty'],
                            category=self.new_question_1['category'])
        question.insert()

        category = Category(type="science")
        category.insert()

        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['categories']), 1)
        self.assertTrue(data['current_category'])

        question.delete()
        category.delete()

    def test_get_all_questions_fail(self):
        question = Question(question=self.new_question_1['question'],
                            answer=self.new_question_1['answer'],
                            difficulty=self.new_question_1['difficulty'],
                            category=self.new_question_1['category'])
        question.insert()

        category = Category(type="science")
        category.insert()

        res = self.client().get('/questions', json={'type': 3})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

        question.delete()
        category.delete()

    # ////////////////////////////////////////////////////////////////////////////////
    # Tests for successful and un-successful GET requests for questions
    # ////////////////////////////////////////////////////////////////////////////////
    def test_get_questions_paginated_success(self):
        question = Question(question="question?",
                            answer="answer",
                            difficulty=1,
                            category=1)
        question.insert()

        category = Category(type="science")
        category.insert()

        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']), 1)
        self.assertEqual(data['current_category'][0], "1")

        question.delete()
        category.delete()

    def test_get_questions_paginated_fail(self):
        question = Question(question=self.new_question_1['question'],
                            answer=self.new_question_1['answer'],
                            difficulty=self.new_question_1['difficulty'],
                            category=self.new_question_1['category'])
        question.insert()

        category = Category(type="science")
        category.insert()

        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

        question.delete()
        category.delete()

    # ////////////////////////////////////////////////////////////////////////////////
    # Tests for the successful and un-successful DELETE requests for questions
    # ////////////////////////////////////////////////////////////////////////////////
    def test_delete_question_success(self):
        question = Question(question=self.new_question_1['question'],
                            answer=self.new_question_1['answer'],
                            difficulty=self.new_question_1['difficulty'],
                            category=self.new_question_1['category'])
        question.insert()

        category = Category(type="science")
        category.insert()

        res = self.client().delete('/questions/' + str(question.id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'question deleted')

        category.delete()

    def test_delete_question_fail(self):
        category = Category(type="science")
        category.insert()

        res = self.client().delete('/questions/1000000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

        category.delete()

    # ////////////////////////////////////////////////////////////////////////////////
    # Tests for the successful and un-successful GET requests
    # for getting questions by category
    # ////////////////////////////////////////////////////////////////////////////////
    def test_get_questions_by_category_success(self):
        drop_create_tables()

        question = Question(question="question?",
                            answer="answer",
                            difficulty=1,
                            category=1)
        question.insert()

        category = Category(type="science")
        category.insert()

        res = self.client().get('/categories/'
                                + '1'
                                + '/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], 1)
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])

        question.delete()
        category.delete()

    def test_get_questions_by_category_fail(self):
        category = Category(type="science")
        category.insert()

        res = self.client().get('/categories/1245/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

        category.delete()

    # ////////////////////////////////////////////////////////////////////////////////
    # Tests for the successful and un-successful POST requests
    # for generating quizes by category
    # ////////////////////////////////////////////////////////////////////////////////
    def test_generate_quiz_success(self):
        question_1 = Question(question='Q1?', answer='A1',
                              difficulty=1, category=1)
        question_2 = Question(question='Q2?', answer='A2',
                              difficulty=2, category=1)
        question_1.insert()
        question_2.insert()

        category = Category(type="science")
        category.insert()

        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'type': "Science",
                'id': '0'
            }})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['previous_questions'], [])
        self.assertTrue(data['current_question'])

        category.delete()

    def test_generate_quiz_fail(self):
        question_1 = Question(question='Q1?', answer='A1',
                              difficulty=1, category=1)
        question_2 = Question(question='Q2?', answer='A2',
                              difficulty=2, category=1)
        question_1.insert()
        question_2.insert()

        category = Category(type="science")
        category.insert()

        res = self.client().get('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'type': "Science",
                'id': '0'
            }})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

        category.delete()

    # ////////////////////////////////////////////////////////////////////////////////
    # Tests for the successful and un-successful POST requests
    # for getting questions using a search term
    # ////////////////////////////////////////////////////////////////////////////////
    def test_search_questions_success(self):
        question = Question(question='Q4?',
                            answer=self.new_question_3['answer'],
                            difficulty=self.new_question_3['difficulty'],
                            category=self.new_question_3['category'])
        question.insert()

        category = Category(type="science")
        category.insert()

        res = self.client().post('/questions', json={'searchTerm': 'Q4?'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['questions'][0]['question'], 'Q4?')
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(data['current_category'], ['3'])

        question.delete()
        category.delete()

    def test_search_questions_fail(self):
        question = Question(question=self.new_question_3['question'],
                            answer=self.new_question_3['answer'],
                            difficulty=self.new_question_3['difficulty'],
                            category=4)
        question.insert()

        category = Category(type="science")
        category.insert()

        res = self.client().post('/questions', json={'searchTerm': None})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

        category.delete()


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
