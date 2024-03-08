import pandas as pd
from typing import List


class MetadataCsvParser:
    """
    Parser for schema definitions defined in csv files.

    A single entity/dataset/table is expected to be defined in a single csv file.

    Each row in the csv file is expected to contain to following fields:
    - attribute_name
    - data_type
    - key_type: PK for primary key, FK for foreign key, and blank for regular columns.
    - reference_entity: name of the entity to which the foreign key refers.  Blank for regular columns.
    - reference_attribute: name of the attribute in the refernece_entity which contains the foreign key.
        Blank for regular columns.
    - relationship: cardinality of the PK-FK relationships.  Blank for regular columns.

    The csv file is expected to contain a header row with the fields names for reference.
    """

    def __init__(self):
        pass

    def read_csv(self, csv_file: str, header: int = 0) -> List[dict]:
        """
        Read a csv file and return a pandas DataFrame.

        Args:
            csv_file (str): path to the csv file.
            header (int): row number to use as the column names.  Defaults to 0.

        Returns:
            pd.DataFrame: the csv file as a pandas DataFrame.
        """
        columns = [
            "attribute_name",
            "data_type",
            "key_type",
            "reference_entity",
            "reference_attribute",
            "relationship",
        ]
        metadata_df = pd.read_csv(csv_file, names=columns, header=header)
        metadata_array = metadata_df.to_dict(orient="records")

        return metadata_array
