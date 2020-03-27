import os
import json

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    redirect,
    url_for
)
from flask_sqlalchemy import SQLAlchemy
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_restx import Api, Resource, fields, abort, reqparse

from celery import Celery
import celery.states as states

from . import api_functions


# global variables
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)
api = Api(app, version='1.0',
          title='API services',
          description='dockerized flask+flask_restx+gunicorn+celery+redis+postgres+nginx skeleton for REST APIs')
ns = api.namespace('rest_api', description='REST services API')


# input and output definitions
tokenizer_input = api.model('TokenizerInput', {
    'text': fields.String(required=True, description='input text')
})
tokenizer_output = api.model('TokenizerOutput', {
    'tokens': fields.List(fields.String, description='tokens')
})

doc_tokenizer_input = api.model('DocTokenizerInput', {
    'texts': fields.List(fields.String, required=True, description='list of texts')
})
doc_tokenizer_output = api.model('DocTokenizerOutput', {
    'tokenized_texts': fields.List(fields.List(fields.String), description='tokens')
})

# async
check_task_input = api.model('CheckTaskInput', {
    'task_id': fields.String(required=True, description='task ID')
})
check_task_output = api.model('CheckTaskOutput', {
    'state': fields.String(description='task state'),
})

get_task_result_input = api.model('GetTaskResultInput', {
    'task_id': fields.String(required=True, description='task ID')
})
get_task_result_output = api.model('GetTaskResultOutput', {
    'result': fields.String(description='result as JSON string')
})

async_translate_input = api.model('AsyncTranslateInput', {
    'text': fields.String(required=True, description='text to translate'),
    'target_lang': fields.String(required=True, description='target language')
})
async_translate_output = api.model('AsyncTranslateOutput', {
    'task_id': fields.String(description='task ID'),
    'check_status_url': fields.Url(description='URL for task status checking')
})


@ns.route('/tokenize_text')
class TextTokenizer(Resource):
    @ns.doc('tokenizes input text')
    @ns.expect(tokenizer_input, validate=True)
    @ns.marshal_with(tokenizer_output)
    def post(self):
        return {'tokens': api_functions.tokenize_text(api.payload['text'])}


@ns.route('/tokenize_docs')
class DocsTokenizer(Resource):
    @ns.doc('tokenizes a list of texts')
    @ns.expect(doc_tokenizer_input, validate=True)
    @ns.marshal_with(doc_tokenizer_output)
    def post(self):
        return {'tokenized_texts': api_functions.tokenize_documents(api.payload['texts'])}


@ns.route('/check_task')
class CheckTask(Resource):
    @ns.doc('checks the status of the task')
    @ns.expect(check_task_input, validate=True)
    @ns.marshal_with(check_task_output)
    def post(self):
        res = celery.AsyncResult(api.payload['task_id'])
        return {'state': res.state}


@ns.route('/get_task_result')
class GetTaskResult(Resource):
    @ns.doc('gets the result of a completed task')
    @ns.expect(get_task_result_input, validate=True)
    @ns.marshal_with(get_task_result_output)
    def post(self):
        res = celery.AsyncResult(api.payload['task_id'])
        if res.state != states.SUCCESS:
            abort(404, 'Cannot get result!', task_state=res.state)
        else:
            return {'state': res.state, 'result': res.get()}


@ns.route('/async_translate_text')
class AsyncTranslator(Resource):
    @ns.doc('translates input text asynchronously')
    @ns.expect(async_translate_input, validate=True)
    @ns.marshal_with(async_translate_output, code=201)
    def post(self):
        task = celery.send_task('tasks.translate', args=[api.payload['text'], api.payload['target_lang']], kwargs={})
        return {'task_id': task.id}
    

# serving static content
@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)

@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)
