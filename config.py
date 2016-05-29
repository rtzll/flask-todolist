# -*- coding: utf-8 -*-

import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'development-key'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR,
                                                          'todolist-dev.db')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR,
                                                          'todolist-test.db')
    WTF_CSRF_ENABLED = False
    import logging
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s'
    )
    logging.getLogger().setLevel(logging.DEBUG)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR,
                                                          'todolist.db')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
