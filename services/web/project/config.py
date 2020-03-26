import os
# from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv()


class Config(object):
    # Database config
    DATABASE_HOST = os.environ.get('SQL_HOST')
    DATABASE_USERNAME = os.environ.get('POSTGRES_USER')
    DATABASE_PORT = os.environ.get('SQL_PORT')
    DATABASE_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    DATABASE_NAME = os.environ.get('POSTGRES_DB')
    DATABASE_URL = 'postgresql://{user}:{password}@{host}:{port}/{db}'.format(user=DATABASE_USERNAME,
                                                                                password=DATABASE_PASSWORD,
                                                                                host=DATABASE_HOST,
                                                                                port=DATABASE_PORT,
                                                                                db=DATABASE_NAME)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    STATIC_FOLDER = os.path.join(basedir, 'project/static')
    MEDIA_FOLDER = os.path.join(basedir, 'project/media')
