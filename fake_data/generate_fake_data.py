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


def build_fk_pools(metadata):
    """
    Creates a dictionary of foreign key pools from metadata and previously generated CSV files.

    Args:
        metadata: A pandas DataFrame containing metadata definitions.
        output_dir: The directory where generated CSV files containing primary keys are located.

    Returns:
        A dictionary where keys are foreign key attribute names and values are lists of valid
        primary key values to be used for generating data with referential integrity.
    """
    fk_pools = {}
    for i, meta in metadata.iterrows():
        if "key_type" in meta and meta["key_type"] == "FK":  # Only process if 'key_type' exists and is 'FK'
            print(f"Row {i}: {meta}")  # Print the row causing the error

            reference_file = meta["reference_file"]
            fk_pools[meta["attribute_name"]] = load_reference_data(reference_file)
    return fk_pools


def generate_fake_data(field_name: str, field_type: str, fake: Faker, nullable: bool = False) -> any:
    # Handle nullable fields
    if nullable and fake.random_int(min=0, max=100) < 20:  # 20% chance of NULL for nullable fields
        return None
        
    if field_type == "account":
        return fake.customer_account()
    elif field_type == "timestamp":
        return fake.txn_datetime()
    elif field_type == "string":
        if "policy_number" in field_name.lower():
            return f"POL-{fake.random_int(min=100000, max=999999)}"
        elif "quote_number" in field_name.lower():
            return f"QUO-{fake.random_int(min=100000, max=999999)}"
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
        if "term_number" in field_name.lower():
            return fake.random_int(min=1, max=10)
        else:
            return fake.random_int(min=0, max=99)
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

        for (source_name, table_name), group in table_groups:
            data = []  # Reset data for each new table
            console.print(f"Generating data for {source_name}.{table_name}")

            # Generate data rows with progress bar
            for _ in track(range(rows), "Generating data..."):
                row = {}
                for _, meta in group.iterrows():
                    nullable = meta['column_data_mode'] == 'NULLABLE'
                    row[meta["column_name"]] = generate_fake_data(
                        meta["column_name"], 
                        meta["column_data_type"].lower(), 
                        fake,
                        nullable
                    )
                data.append(row)

            # Convert to DataFrame and save to CSV
            df = pd.DataFrame(data)
            
            # Output File Name - use source_name and table_name
            output_file = os.path.join(output_dir, f"{source_name}_{table_name}.csv")
            os.makedirs(output_dir, exist_ok=True)  # Create 'output' if it doesn't exist
            df.to_csv(output_file, index=False)

            console.print(f'Generated data saved to "{output_file}"')


if __name__ == "__main__":
    app()
