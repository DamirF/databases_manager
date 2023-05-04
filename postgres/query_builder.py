from typing import Literal, List, Any, Dict

from postgres.builder_source import *


class QueryBuilderBase:
    QUERY_TYPES = Literal[
        "CREATE",
        "SELECT",
        "INSERT",
        "UPDATE",
    ]
    SELECT_OPERATORS = Literal[
        "AND",
        "OR"
    ]

    @staticmethod
    def create_query(_type: QUERY_TYPES,
                     database_name: str = '',   # for database create
                     table_name: str = '',  # for table create
                     table_columns: List[str] = None,
                     values: List[str] = None,
                     select_operation: SELECT_OPERATORS = OR,
                     select_parameters: Dict[str, Any] = None,
                     select_columns: bool = False,
                     select_tables: bool = False
                     ) -> str:

        # Parameters validation
        if select_parameters is None:
            select_parameters = {}
        if table_columns is None:
            table_columns = []
        if values is None:
            values = []
        for key in select_parameters.keys():
            if key not in table_columns:
                raise Exception(f"{key} not found in Table columns")

        query = _type

        match _type:
            case "CREATE":
                ...
            case "SELECT":
                if select_tables:
                    query = f"{_type} {ALL} {FROM} {SCHEMA}.{TABLES} {WHERE} {TABLE_SCHEMA}={PUBLIC_SCHEMA}"
                elif select_columns:
                    query = f"{_type} {ALL} {FROM} {SCHEMA}.{COLUMNS} {WHERE} table_name='{table_name}'"
                else:
                    query = f""
            case "INSERT":
                if len(table_columns) != len(values):
                    raise Exception("Values count must coincide with Table Columns count")
            case "UPDATE":
                if len(table_columns) != len(values):
                    raise Exception("Values count must coincide with Table Columns count")

        return query


class QueryBuilder(QueryBuilderBase):

    @staticmethod
    def select_query() -> str:
        query = super().create_query("SELECT")
        return f""
