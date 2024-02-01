import csv
from faker import Faker
from faker.providers import BaseProvider
import pandas as pd
from rich.console import Console
from rich.progress import track
import typer
from typing import List

app = typer.Typer()

class FinanceProvider(BaseProvider):
    def customer_account(self):
        # Generate a string with 8 characters, each between '10' and '40', and insert dashes
        account = ''.join(str(self.random_int(10, 40)) for _ in range(4))
        formatted_account = '-'.join(account[i:i+2] for i in range(0, len(account), 2))
        return formatted_account


def generate_fake_data(field_name: str, field_type: str, fake: Faker) -> any:
    if field_type == "account":
        return fake.customer_account()
    elif field_type == "string":
        if "name" in field_name.lower():
            return fake.name()
        elif "email" in field_name.lower():
            return fake.email()
        elif "address" in field_name.lower():
            return fake.address().replace('\n', ', ')
        else:
            return fake.word()
    elif field_type == "int":
        return fake.random_int(min=0, max=99)
    elif field_type == "date":
        return fake.date()
    # You can extend this function to generate more specific data based on field_name or field_type
    else:
        return -1

@app.command()
def generate_data(metadata_csv: str = "metadata.csv", output_csv: str = "output.csv", rows: int = 100, seed: int = None):
    """
    Generate fake data based on the metadata described in a CSV file.

    :param metadata_csv: Path to the CSV file containing metadata definitions. Default is 'metadata.csv'.
    :param output_csv: Path for the generated CSV file. Default is 'output.csv'.
    :param rows: Number of data rows to generate. Default is 100.
    """

    fake = Faker('en_AU')
    fake.add_provider(FinanceProvider)
    
    if seed is not None:
        Faker.seed(seed)
    # Read the metadata CSV
    metadata = pd.read_csv(metadata_csv)
    data = []
    
    # Generate data rows with progress bar
    for _ in track(range(rows), "Generating data..."):
        row = {}
        for _, meta in metadata.iterrows():
            row[meta['attribute_name']] = generate_fake_data(meta['attribute_name'], meta['data_type'], fake)
        data.append(row)
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)

    console = Console()
    console.print(f'Generated data saved to "{output_csv}"')

if __name__ == "__main__":
    app()
