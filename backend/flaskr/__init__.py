import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql.expression import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories', methods=['GET'])
    def get_all_categories():
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        return jsonify({
            'success': True,
            'categories': formatted_categories
        })
    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    ST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/questions', methods=['GET'])
    def get_all_questions():
        categories = [category.format() for category in Category.query.all()]
        questions = [question.format() for question in Question.query.all()]
        if len(questions) == 0:
            abort(404)
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + QUESTIONS_PER_PAGE
        return jsonify({
            'questions': questions[start:end],
            'totalQuestions': len(questions),
            'categories': categories
        })

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_specific_question(id):
        question = Question.query.get(id)
        if not question:
            return abort(404,
            {
                'message':'Question not exists'
            })
        else:
            question.delete()
            return jsonify({
                'deleted': id
            })

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def post_new_question():
        question = request.json.get('question')
        answer = request.json.get('answer')
        category = request.json.get('category')
        difficulty = request.json.get('difficulty')
        if not (question and answer and category and difficulty):
            return abort(400)
        new_question = Question(question, answer, category, difficulty)
        new_question.insert()
        return jsonify({
            'success': True,
            'added Question': new_question.format()
        })

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    @app.route('/search', methods=['POST'])
    def search_specific_question():
        search_term = request.json.get('searchTerm', '')
        if search_term == '':
            abort(422)

        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

        if len(questions) == 0:
                abort(404)

        return jsonify({
                'success': True,
                'questions': questions,
        })

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        if not category_id:
            return abort(404)
        questions = [question.format() for question in Question.query.filter(Question.category == category_id)]
        return jsonify({
            'questions': questions,
            'current_category': category_id
        })

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():

        previous_questions = request.json.get('previous_questions')
        quiz_category = request.json.get('quiz_category')

        if not quiz_category:
            return abort(400)

        category_id = int(quiz_category.get('id'))

        questions = Question.query.filter(Question.category == category_id,
            ~Question.id.in_(previous_questions)) if category_id else \
            Question.query.filter(~Question.id.in_(previous_questions))

        question = questions.order_by(func.random()).first()

        if not question:
            return jsonify({})
        return jsonify({
            'success': True,
            'question': question.format()
        })

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    #Error handler for 404-Not found
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
            }), 404

    #Error handler for 422-Unprocessable Entity
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
        "success": False, 
        "error": 422,
        "message": "Unprocessable Entity"
        }), 422

    #Error handler for 400-bad request
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad Request"
        }), 400

    #Error handler for 500-Internal Server Error
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
        "success": False, 
        "error": 500,
        "message": "Internal server error"
        }), 500

    return app
