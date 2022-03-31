import os


class Config(object):
    # Database config
    SQLALCHEMY_DATABASE_URI = 'mysql://root:password@localhost:3306/agrosmart'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # Flask Mail config
    MAIL_SERVER = 'smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'abe2fc590fa42a'
    MAIL_PASSWORD = '3203ff2299e5fd'


OBJECTS_PER_PAGE = 20
