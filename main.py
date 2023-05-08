from interface.elements.models import *
from postgres.builder_source import SELECT
from postgres.models import User, Database, QueryManager
from postgres.query_builder import QueryBuilder


def main():
    username = "postgres"
    password = "k.nsqghbrjk"
    db_name = "django_proj"
    database = Database(user=User(username=username, password=password), db_name=db_name)
    app = CreateTableConfigurationWindow(database)
