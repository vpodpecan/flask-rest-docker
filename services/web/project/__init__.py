import os

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
    'texts': fields.List(fields.String, description='list of texts')
})
doc_tokenizer_output = api.model('DocTokenizerOutput', {
    'tokenized_texts': fields.List(fields.List(fields.String), description='tokens')
})



@ns.route('/tokenize_text')
class TextTokenizer(Resource):
    @ns.doc('tokenizes input text')
    @ns.expect(tokenizer_input, validate=True)
    @ns.marshal_with(tokenizer_output, code=201)
    def post(self):
        return {'tokens': api_functions.tokenize_text(api.payload['text'])}


@ns.route('/tokenize_docs')
class DocsTokenizer(Resource):
    @ns.doc('tokenizes a list of texts')
    @ns.expect(doc_tokenizer_input, validate=True)
    @ns.marshal_with(doc_tokenizer_output, code=201)
    def post(self):
        return {'tokenized_texts': api_functions.tokenize_documents(api.payload['texts'])}

@app.route("/test/<int:x>")
def test(x):
    task = celery.send_task('tasks.pow2', args=[x], kwargs={})
    response = {'task_id': task.id, 'check_status_url': url_for('check_task', task_id=task.id, _external=True)}
    return response

@app.route('/check/<string:task_id>')
def check_task(task_id):
    res = celery.AsyncResult(task_id)
    if res.state == states.PENDING:
        return {'state': res.state}
    else:
        return {'state': res.state, 'result': res.get()}

# serving static content
@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)

@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)
