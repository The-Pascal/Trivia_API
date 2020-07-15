import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql.expression import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 8


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins.
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
    Function to query all
    '''
    def query_all_function(query_term):
        return query_term.query.all()

    '''
    Function to paginate
    '''
    def do_pagination(page_no):
        start = (page_no - 1) * 10
        end = start + QUESTIONS_PER_PAGE
        return start

    '''
    @TODO:
    endpoint to handle GET requests
    for categories.
    '''
    @app.route('/categories', methods=['GET'])
    def fetch_all_available_categories():
        all_categories = query_all_function(Category)
        after_format_categories = [category.format() for category in all_categories]
        return jsonify({
            'success': True,
            'categories': after_format_categories
        })
    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    '''
    @app.route('/questions', methods=['GET'])
    def get_all_questions():

        all_categories = [category.format() for category in Category.query.all()]
        all_questions = [question.format() for question in Question.query.all()]

        if len(all_questions) == 0:
            abort(404)

        page_no = request.args.get('page', 1, type=int)
        #doing pagination here
        start_point_for_questions = do_pagination(page_no)

        return jsonify({
            'questions': all_questions[start_point_for_questions:start_point_for_questions + QUESTIONS_PER_PAGE],
            'totalQuestions': len(all_questions),
            'categories': all_categories
        })

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
    TEST: When you click the trash icon next to a question, the question will be removed
    '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def specific_question_deletion(id):

        question = query_all_function(Question)

        if (len(question)==0):
            return abort(404)
        else:
            question.delete()
            return jsonify({
                'success': True,
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

        new_question = request.json.get('question')
        new_answer = request.json.get('answer')
        new_category = request.json.get('category')
        new_difficulty = request.json.get('difficulty')
        new_rating = request.json.get('rating')

        if not (new_question and new_answer and new_category and new_difficulty and new_rating):
            return abort(400)

        framed_question = Question(new_question, new_answer, new_category, new_difficulty, new_rating)

        framed_question.insert()

        return jsonify({
            'success': True,
            'message': 'New question framed',
            'added Question': framed_question.format()
        })

    '''
    Endpoint to create new category. Just an attempt.
    '''
    @app.route('/categories', methods=['POST'])
    def post_new_category():

        new_type = request.json.get("new_type")
        
        if(new_type==""):
            abort(400)
        
        new_category = Category(new_type)
        new_category.insert()
        return jsonify({
            'success': True,
            'message': 'created new category'
        })

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_category(id):
        if not id:
            return abort(404)
        questions = [question.format() for question in Question.query.filter(Question.category == id)]
        return jsonify({
            'questions': questions,
            'current_category': id
        })


    '''
    Function to find questions by categories and previous questions
    '''
    def required_questions_func(found_category_id, previous_questions):
        questions_found = Question.query.filter(Question.category == found_category_id)
        questions_found = questions_found.format()
        for question_ in questions_found:
            if(question_.id not in previous_questions):
                final_questions = question_
        return final_questions

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz.
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quiz', methods=['POST'])
    def get_quiz_questions():

        previous_questions = request.json.get('previous_questions')

        quiz_category = request.json.get('quiz_category')

        if (len(quiz_category)<=0):
            return abort(400)

        found_category_id = quiz_category.get('id')

        final_questions = required_questions_func(found_category_id, previous_questions)

        required_questions = final_questions.order_by(func.random())

        if (len(required_questions)<=0):
            return jsonify(404)

        return jsonify({
            'success': True,
            'message': 'question is found',
            'question': required_questions
        })



    '''
    Function to search questions and return founded questions
    '''
    def fun_to_search(term_to_be_searched):
        going_to_search = Question.question.like('%{term_to_be_searched}%')
        questions_found = Question.query.filter(going_to_search).all()
        return questions_found

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    @app.route('/search', methods=['POST'])
    def search_specific_question():

        term_to_be_searched = request.json.get('searchTerm', '')

        if (term_to_be_searched == ''):
            abort(422)

        questions_found = fun_to_search(term_to_be_searched)

        if len(questions_found) == 0:
                abort(404)

        return jsonify({
                'success': True,
                'message': 'Questions are found',
                'questions': questions_found,
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
            "error status code": 404,
            "message": "Resource you are looking is not found"
            }), 404

    #Error handler for 422-Unprocessable Entity
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
        "success": False, 
        "error status code": 422,
        "message": "  Unprocessable Entity  "
        }), 422

    #Error handler for 400-bad request
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
        "success": False, 
        "error status code": 400,
        "message": "Bad Request. Format you request correctly and then try again!!"
        }), 400

    #Error handler for 500-Internal Server Error
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
        "success": False, 
        "error status code": 500,
        "message": "Internal server error. Try again after sometime !!"
        }), 500

    return app
