import os
from rich.console import Console
from typer import Argument, Context, Typer
from typing import List

from fake_data.metadata.metadata_cache import MetadataCache
from fake_data.metadata.metadata_csv_parser import MetadataCsvParser

ci_env_var = "CI"
force_terminal = True if ci_env_var in os.environ else False
console = Console(force_terminal=force_terminal)
console_err = Console(force_terminal=force_terminal, stderr=True)

app = Typer(no_args_is_help=True)


@app.command(name="reset")
def metadata_reset(ctx: Context):
    """
    Erase all fake-data data and tables from the metadata cache.
    """
    metadata_cache_dir = ctx.obj["metadata_cache_dir"]
    mdc = MetadataCache(metadata_cache_dir=metadata_cache_dir)

    if len(mdc.fake_tables) > 0:
        console.print(f"Dropping {len(mdc.get_fake_tables())} existing fake table(s) in the metadata cache")
        # drop all the tables
        mdc.drop_fake_tables()
    else:
        console.print("No fake tables to drop")

    mdc.truncate_control_tables()


@app.command("update")
def metadata_update(ctx: Context):
    """
    Update the metadata cache with additional data definitions.
    """
    metadata_cache_dir = ctx.obj["metadata_cache_dir"]
    _ = MetadataCache(metadata_cache_dir=metadata_cache_dir)

    raise NotImplementedError("Not implemented yet")


@app.command("refresh")
def metadata_refresh(ctx: Context, metadata_filenames: List[str] = Argument(..., help="List of metadata files to process")):
    """
    Drops all data and tables in the metadata cache and recreates them based on the supplied data definitions.

    If the filename ends in csv, load as a csv file.
    """
    metadata_cache_dir = ctx.obj["metadata_cache_dir"]
    mdc = MetadataCache(metadata_cache_dir=metadata_cache_dir)

    if len(mdc.fake_tables) > 0:
        console.print(f"Dropping {len(mdc.get_fake_tables())} existing fake table(s) in the metadata cache")
        # drop all the tables
        mdc.drop_fake_tables()
    else:
        console.print("No fake tables to drop")

    mdc.truncate_control_tables()

    for filename in metadata_filenames:
        table_name = os.path.splitext(os.path.basename(filename))[0]
        if filename.endswith(".csv"):
            parser = MetadataCsvParser()
            table_definition = parser.read_csv(filename)

        mdc.create_table(table_name, table_definition)
        console.print(f"Created fake table for {table_name}")


@app.command("ls")
def list_metadata_tables(ctx: Context):
    """
    List the fake-data tables in the metadata cache.
    """
    metadata_cache_dir = ctx.obj["metadata_cache_dir"]

    mdc = MetadataCache(metadata_cache_dir=metadata_cache_dir)
    fake_tables = mdc.get_fake_tables()

    for t in fake_tables:
        console.print(t)
