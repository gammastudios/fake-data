# import csv
from datetime import datetime, timedelta
from faker import Faker
from faker.providers import BaseProvider
import os
import pandas as pd
from rich.console import Console
from rich.progress import track
import typer
from typer import Context
from typing import List
import numpy as np
from typing_extensions import Annotated

from fake_data import VERSION
from fake_data.metadata import commands as metadata_commands


# set env var when running via CICD to enable colorised ouput
ci_env_var = "CI"
force_terminal = True if ci_env_var in os.environ else False
console = Console(force_terminal=force_terminal)
console_err = Console(force_terminal=force_terminal, stderr=True)


def global_opts_callback(
    ctx: Context,
    metadata_cache_dir: Annotated[
        str, typer.Option(..., help="fake-data metadata cache directory", envvar="FAKE_DATA_CACHE_DIR")
    ] = ".fake_data_cache",
):
    # ensure the cache directory exists
    os.makedirs(metadata_cache_dir, exist_ok=True)

    # add to the context
    ctx.ensure_object(dict)
    ctx.obj["metadata_cache_dir"] = metadata_cache_dir


app = typer.Typer(no_args_is_help=True, callback=global_opts_callback)
app.add_typer(metadata_commands.app, name="metadata", short_help="manage fake-data metadata", no_args_is_help=True)


@app.command(name="version")
def version():
    """
    Print the version of the fake-data package.
    """
    typer.echo(VERSION)


def load_reference_data(reference_file):
    df = pd.read_csv(reference_file)
    print(df)
    return df["id"].tolist()  # Return a list of all ID values


# ripped from @datwiz
# https://github.com/gammastudios/data-with-gcp/blob/main/bq-external-tables/src/create_fake_csv_data.py
class TxnDatetimeProvider(BaseProvider):
    def __init__(self, generator, days_of_data=365):
        super().__init__(generator)
        self.generator = generator
        self.end_dts = datetime.now()
        self.start_dts = self.end_dts - timedelta(days=days_of_data)
        self.format = "%Y-%m-%d %H:%M:%S"

    def txn_datetime(self):
        fake_date = self.generator.date_time_between(start_date=self.start_dts, end_date=self.end_dts)
        return fake_date.strftime(self.format)

    def txn_amount(self):
        return self.generator.pydecimal(left_digits=3, right_digits=2, positive=True)


class FinanceProvider(BaseProvider):
    def customer_account(self):
        # Generate a string with 8 characters, each between '10' and '40', and insert dashes
        account = "".join(str(self.random_int(10, 40)) for _ in range(4))
        formatted_account = "-".join(account[i : i + 2] for i in range(0, len(account), 2))
        return formatted_account


def build_fk_pools(metadata_df, generated_data):
    """
    Creates a dictionary of foreign key pools from metadata and previously generated data.

    Args:
        metadata_df: A pandas DataFrame containing metadata definitions
        generated_data: Dictionary storing generated data for each table

    Returns:
        A dictionary where keys are (table_name, column_name) tuples and values are lists of valid
        primary key values to be used for generating data with referential integrity.
    """
    fk_pools = {}
    
    # Determine which column name to use
    name_col = 'attribute_name' if 'attribute_name' in metadata_df.columns else 'column_name'
    
    # Find all foreign key relationships
    fk_rows = metadata_df[metadata_df['key_type'] == 'FK']
    for _, fk_row in fk_rows.iterrows():
        table_name = fk_row['table_name']
        column_name = fk_row[name_col]
        ref_table = fk_row['reference_entity']
        
        # Get the primary key values from the referenced table's generated data
        if ref_table in generated_data:
            pk_values = generated_data[ref_table][column_name].tolist()
            fk_pools[(table_name, column_name)] = pk_values
            
    return fk_pools


# Global pools for maintaining referential integrity
shared_values = {
    'policy_number': [],  # List to maintain order and uniqueness within tables
    'quote_number': []
}

# Track current position in each shared value list for each table
current_table_positions = {
    'policy_number': 0,
    'quote_number': 0
}

def initialize_shared_values(field_key: str, num_rows: int, fake: Faker):
    """Initialize the shared value pool with unique values."""
    if not shared_values[field_key]:  # Only initialize if empty
        for _ in range(num_rows):
            if "policy_number" in field_key:
                value = f"POL-{fake.random_int(min=100000, max=999999)}"
                while value in shared_values[field_key]:  # Ensure uniqueness
                    value = f"POL-{fake.random_int(min=100000, max=999999)}"
            elif "quote_number" in field_key:
                value = f"QUO-{fake.random_int(min=100000, max=999999)}"
                while value in shared_values[field_key]:  # Ensure uniqueness
                    value = f"QUO-{fake.random_int(min=100000, max=999999)}"
            shared_values[field_key].append(value)

def get_next_value(field_name: str) -> str:
    """Get the next value from the shared pool for the current table."""
    field_key = field_name.lower()
    
    # Get next value and increment position
    value = shared_values[field_key][current_table_positions[field_key]]
    current_table_positions[field_key] = (current_table_positions[field_key] + 1) % len(shared_values[field_key])
    return value

def generate_fake_data(field_name: str, field_type: str, fake: Faker, nullable: bool = False, fk_value: any = None) -> any:
    # If this is a foreign key field and we have a value, use it
    if fk_value is not None:
        return fk_value
        
    # Handle nullable fields (only for non-FK fields)
    if nullable and fake.random_int(min=0, max=100) < 20:  # 20% chance of NULL for nullable fields
        return None
        
    if field_type == "account":
        return fake.customer_account()
    elif field_type == "timestamp":
        return fake.txn_datetime()
    elif field_type == "string":
        if field_name.lower() == "change_type":
            change_type = fake.random_element(elements=("U", "I", "D"))
        else:
            change_type = None
        if field_name.lower() == "change_type":
            return change_type
        elif "policy_number" in field_name.lower():
            if change_type == "U" and shared_values['policy_number']:
                return fake.random_element(elements=shared_values['policy_number'])
            else:
                return get_next_value('policy_number')
        elif "quote_number" in field_name.lower():
            return get_next_value('quote_number')
        elif "name" in field_name.lower():
            if "brand" in field_name.lower():
                return "IAG"
            elif "product" in field_name.lower():
                return fake.random_element(elements=("Home", "Car", "Landlord"))
            else:
                return fake.name()
        elif "email" in field_name.lower():
            return fake.email()
        elif "address" in field_name.lower() or "suburb" in field_name.lower():
            return fake.address().replace("\n", ", ")
        elif "state" in field_name.lower():
            return fake.random_element(elements=("NSW", "VIC", "QLD", "WA", "SA", "TAS", "NT", "ACT"))
        elif "postal_code" in field_name.lower():
            return fake.postcode()
        elif "phone" in field_name.lower():
            return fake.phone_number()
        elif "status" in field_name.lower():
            return fake.random_element(elements=("Bound", "Quoted", "Not Taken", "Withdrawn"))
        else:
            return fake.word()
    elif field_type == "integer":
        return int(fake.random_int(min=0, max=99))
    elif field_type == "numeric":
        if "amount" in field_name.lower() or "premium" in field_name.lower():
            return round(fake.random.uniform(100, 5000), 2)
        else:
            return round(fake.random.uniform(0, 1000), 2)
    elif field_type == "date":
        return fake.date()
    elif field_type == "boolean" or field_type == "bool":
        return fake.boolean()
    else:
        return None


# customer_account needs to go first here, bc of the FK relationship so
# id's in customer_account need to be created first, then referenced in customer
# TODO: determine dependencies when generating fake-data between FK and PK
@app.command("generate-data")
def generate_data(
    metadata_csvs: List[str] = typer.Option(
        ["columns_metadata.csv"], help="List of metadata CSV files to process"
    ),
    output_dir: str = "output",
    rows: int = 100,
    seed: int = None,
    cache_dir: str = typer.Option("./fake_data_cache", help="fake data working cache directory", envvar="FAKE_DATA_CACHE_DIR"),
):
    """
    Generate fake data for multiple metadata CSV files.

    :param metadata_csvs: A list of paths to metadata CSV files.
    :param output_dir: Directory to save the generated output CSV files.
    :param rows: Number of data rows to generate per file. Default is 100.
    """
    # Clear shared value pools at start of each generation
    shared_values['policy_number'].clear()
    shared_values['quote_number'].clear()

    fake = Faker("en_AU")
    fake.add_provider(FinanceProvider)
    fake.add_provider(TxnDatetimeProvider)

    if seed is not None:
        Faker.seed(seed)

    # Read the metadata CSV's
    for metadata_csv in metadata_csvs:
        # Group metadata by table_name and source_name to generate separate files
        metadata_df = pd.read_csv(metadata_csv)
        table_groups = metadata_df.groupby(['source_name', 'table_name'])

        # Store generated data for FK relationships
        generated_data = {}
        
        # Process tables in order (PKs first, then FKs)
        for pass_num in [1, 2]:  # Two passes: first for non-FK tables, then FK tables
            for (source_name, table_name), group in table_groups:
                # Skip FK tables in first pass and non-FK tables in second pass
                has_fks = False
                if 'key_type' in group.columns:
                    has_fks = group['key_type'].eq('FK').any()
                
                if (pass_num == 1 and has_fks) or (pass_num == 2 and not has_fks):
                    continue
                
                data = []  # Reset data for each new table
                console.print(f"Generating data for {source_name}.{table_name}")
                
                # Reset positions for new table
                current_table_positions['policy_number'] = 0
                current_table_positions['quote_number'] = 0
                
                # Initialize shared pools if this is first table
                initialize_shared_values('policy_number', rows, fake)
                initialize_shared_values('quote_number', rows, fake)
                
                # Build FK pools if needed
                fk_pools = build_fk_pools(metadata_df, generated_data) if pass_num == 2 else {}
                
                # Generate data rows with progress bar
                for _ in track(range(rows), f"Generating data for {table_name}..."):
                    row = {}
                    for _, meta in group.iterrows():
                        nullable = meta['column_data_mode'] == 'NULLABLE'
                        
                        # Determine which column name to use
                        name_col = 'attribute_name' if 'attribute_name' in meta else 'column_name'
                        type_col = 'data_type' if 'data_type' in meta else 'column_data_type'
                        
                        # Get FK value if this is a foreign key
                        fk_value = None
                        if 'key_type' in meta and meta['key_type'] == 'FK':
                            pool_key = (table_name, meta[name_col])
                            if pool_key in fk_pools and fk_pools[pool_key]:
                                fk_value = fake.random_element(elements=fk_pools[pool_key])
                        
                        row[meta[name_col]] = generate_fake_data(
                            meta[name_col],
                            meta[type_col].lower(),
                            fake,
                            nullable,
                            fk_value
                        )
                    data.append(row)
                
                # Determine dtypes
                dtypes = {}
                for _, meta in group.iterrows():
                    name_col = 'attribute_name' if 'attribute_name' in meta else 'column_name'
                    type_col = 'data_type' if 'data_type' in meta else 'column_data_type'
                if meta[type_col].lower() == 'integer':
                    dtypes[meta[name_col]] = np.int64

                # Convert to DataFrame and store for FK relationships
                df = pd.DataFrame(data)
                generated_data[table_name] = df

                # Output File Name - use source_name and table_name
                output_file = os.path.join(output_dir, f"{source_name}_{table_name}.csv")
                os.makedirs(output_dir, exist_ok=True)  # Create 'output' if it doesn't exist
                df.to_csv(output_file, index=False)

                console.print(f'Generated data saved to "{output_file}"')


if __name__ == "__main__":
    app()
