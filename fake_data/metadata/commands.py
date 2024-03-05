import os
from typer import Typer
from rich.console import Console

ci_env_var = "CI"
force_terminal = True if ci_env_var in os.environ else False
console = Console(force_terminal=force_terminal)
console_err = Console(force_terminal=force_terminal, stderr=True)

app = Typer(no_args_is_help=True)


@app.command(name="reset")
def metadata_reset():
    """
    Erase all fake-data data and tables from the metadata cache.
    """
    raise NotImplementedError("Not implemented yet")


@app.command("update")
def metadata_update():
    """
    Update the metadata cache with additional data definitions.
    """
    raise NotImplementedError("Not implemented yet")


@app.command("refresh")
def metadata_refresh():
    """
    Drops all data and tables in the metadata cache and recreates them based on the supplied data definitions.
    """


@app.command("ls")
def list_metadata_tables():
    """
    List the fake-data tables in the metadata cache.
    """
    pass
