import os
from typer import Context, Typer
from rich.console import Console

from fake_data.metadata.metadata_cache import MetadataCache

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
def metadata_refresh(ctx: Context):
    """
    Drops all data and tables in the metadata cache and recreates them based on the supplied data definitions.
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

    # table_name = "test_table"
    # colums = [
    #     {"name": "id", "type": "int"},
    #     {"name": "name", "type": "string"},
    # ]
    # mdc.create_table(table_name=table_name, columns=colums)


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
