import os
from typer import Typer
from rich.console import Console

ci_env_var = "CI"
force_terminal = True if ci_env_var in os.environ else False
console = Console(force_terminal=force_terminal)
console_err = Console(force_terminal=force_terminal, stderr=True)

app = Typer(no_args_is_help=True)


@app.command("update")
def metadata_update():
    raise NotImplementedError("Not implemented yet")


@app.command("refresh")
def metadata_refresh():
    pass


@app.command("ls")
def list_metadata_tables():
    """
    List the fake-data tables in the metadata cache.
    """
    pass
