import duckdb
import os
from typing import List


class MetadataCache:
    """
    Metadata cache for the fake data generator.
    """

    def __init__(self, metadata_cache_dir: str = ".fake_data_cache") -> None:
        # create the cache dir if it does not exist
        self.metadata_cache_dir = metadata_cache_dir

        # Connect to the database file
        self.db = duckdb.connect(database=os.path.join(self.metadata_cache_dir, "fake_data.db"))

        # TODO load any existing metadata from the cache database
        self.tables = []

    def create_table(self, table_name: str, columns: List[dict]) -> None:
        """
        Create a table in the metadata cache.

        Args:
            table_name (str): name of the table.
            columns (List[dict]): columns of the table.  Each column is a dictionary at least with the following keys:
                - name: name of the column.
                - type: type of the column.

        Returns:
            None
        """
        sttmt = self._create_table_sttmt(table_name, columns)
        try:
            self.db.execute(sttmt)
            self.tables.append(table_name)
        except duckdb.duckdb.ParserException as e:
            print(f"Error creating table {table_name}: {e}")
            print(f"Statement: {sttmt}")

    def _create_table_sttmt(self, table_name, columns: List[dict]) -> str:
        """
        Assemble create table DDL statement.

        Args:
            table_name (str): name of the table.
            columns (List[dict]): columns of the table.  Each column is a dictionary at least with the following keys:
                - name: name of the column.
                - type: type of the column.

        Returns:
            (str): DDL string for the create table statement.
        """

        try:
            cols_str = ", ".join(f"{c['name']} {c['type']}" for c in columns)
            sttmt = f"CREATE TABLE {table_name} ({cols_str})"
        except KeyError as e:
            raise ValueError(f"Column definition missing key: {e}")
        return sttmt
