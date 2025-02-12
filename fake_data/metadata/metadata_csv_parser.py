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
        Read a csv file and return a list of metadata dictionaries.

        Args:
            csv_file (str): path to the csv file.
            header (int): row number to use as the column names. Defaults to 0.

        Returns:
            List[dict]: List of metadata dictionaries with standardized field names
        """
        # Read the CSV with original column names
        metadata_df = pd.read_csv(csv_file)
        
        # Map new column names to expected format
        metadata_df = metadata_df.rename(columns={
            'column_name': 'attribute_name',
            'column_data_type': 'data_type'
        })
        
        # Add required columns if they don't exist
        if 'key_type' not in metadata_df.columns:
            metadata_df['key_type'] = ''
        if 'reference_entity' not in metadata_df.columns:
            metadata_df['reference_entity'] = ''
        if 'reference_attribute' not in metadata_df.columns:
            metadata_df['reference_attribute'] = ''
        if 'relationship' not in metadata_df.columns:
            metadata_df['relationship'] = ''
            
        # Convert data types to lowercase to match generate_fake_data expectations
        metadata_df['data_type'] = metadata_df['data_type'].str.lower()
        
        # Add nullable information from column_data_mode
        metadata_df['nullable'] = metadata_df['column_data_mode'].apply(
            lambda x: True if x == 'NULLABLE' else False
        )
        
        # Convert to list of dictionaries
        metadata_array = metadata_df.to_dict(orient="records")
        
        return metadata_array
