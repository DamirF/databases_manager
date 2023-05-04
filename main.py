from interface.elements.models import *
from postgres.builder_source import SELECT
from postgres.models import User, Database, QueryManager
from postgres.query_builder import QueryBuilder


def main():
    app = StartWindow()
