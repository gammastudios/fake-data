import duckdb

class MetadataCsvParser:
    """
    Parser for schema definitions defined in csv files using duckdb.

    A single entity/dataset/table is expected to be defined in a single csv file.

    Each row in the csv file is expected to contain to following fields:
    - attribute_name
    - data_type
    - key_type: PK for primary key, FK for foreign key, and blank for regular columns.
    - reference_entity: name of the entity to which the foreign key refers.  Blank for regular columns.
    - reference_attribute: name of the attribute in the reference_entity which contains the foreign key.
        Blank for regular columns.
    - relationship: cardinality of the PK-FK relationships.  Blank for regular columns.

    The csv file is expected to contain a header row with the fields names for reference.
    """

    def __init__(self):
        pass

    def read_csv(self, csv_file: str, header: bool = True) -> list:
        """
        Read a csv file and return a list of dictionaries using duckdb.

        Args:
            csv_file (str): path to the csv file.
            header (bool): whether the csv file contains a header row. Defaults to True.

        Returns:
            list: the csv file as a list of dictionaries.
        """
        query = f"SELECT * FROM read_csv_auto('{csv_file}', HEADER={header})"
        result = duckdb.query(query).fetchall()
        columns = duckdb.query(query).description

        # Extracting column names
        column_names = [col[0] for col in columns]

        # Converting list of tuples to list of dictionaries
        metadata_array = [dict(zip(column_names, row)) for row in result]

        return metadata_array