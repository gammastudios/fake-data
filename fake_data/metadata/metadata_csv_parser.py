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
        
        # Map column names to expected format if needed
        if 'attribute_name' not in metadata_df.columns and 'column_name' in metadata_df.columns:
            metadata_df = metadata_df.rename(columns={'column_name': 'attribute_name'})
        if 'data_type' not in metadata_df.columns and 'column_data_type' in metadata_df.columns:
            metadata_df = metadata_df.rename(columns={'column_data_type': 'data_type'})
        
        # Initialize key relationship columns
        metadata_df['key_type'] = ''
        metadata_df['reference_entity'] = ''
        metadata_df['reference_attribute'] = ''
        metadata_df['relationship'] = ''

        # Ensure we have source_name and table_name
        if 'source_name' not in metadata_df.columns or 'table_name' not in metadata_df.columns:
            raise ValueError("CSV must contain 'source_name' and 'table_name' columns")

        # Create a unique table identifier combining source and table name
        metadata_df['full_table_name'] = metadata_df['source_name'] + '.' + metadata_df['table_name']

        # Determine which column name to use for grouping
        name_col = 'attribute_name' if 'attribute_name' in metadata_df.columns else 'column_name'
        
        # Group by column name to find relationships
        column_groups = metadata_df.groupby(name_col)
        for col_name, group in column_groups:
            if len(group) > 1:  # Column appears in multiple tables
                # Find the first occurrence as primary key
                first_table = group.iloc[0]['full_table_name']
                
                # Mark as PK in first table
                metadata_df.loc[(metadata_df['full_table_name'] == first_table) & 
                              (metadata_df[name_col] == col_name), 'key_type'] = 'PK'
                
                # Mark other occurrences as foreign keys
                fk_mask = (metadata_df['full_table_name'] != first_table) & \
                         (metadata_df[name_col] == col_name)
                metadata_df.loc[fk_mask, 'key_type'] = 'FK'
                metadata_df.loc[fk_mask, 'reference_entity'] = first_table.split('.')[1]  # Just use table name without source
                metadata_df.loc[fk_mask, 'reference_attribute'] = col_name
                metadata_df.loc[fk_mask, 'relationship'] = '1:N'  # Default cardinality
            
        # Convert data types to lowercase to match generate_fake_data expectations
        metadata_df['data_type'] = metadata_df['data_type'].str.lower() if 'data_type' in metadata_df.columns else metadata_df['column_data_type'].str.lower()
        
        # Add nullable information from column_data_mode
        metadata_df['nullable'] = metadata_df['column_data_mode'].apply(
            lambda x: True if x == 'NULLABLE' else False
        )
        
        # Convert to list of dictionaries
        metadata_array = metadata_df.to_dict(orient="records")
        
        return metadata_array
