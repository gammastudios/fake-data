from typer import Typer

app = Typer()


@app.command('update')
def metadata_update():
    raise NotImplementedError("Not implemented yet")

@app.command('refresh')
def metadata_refresh():
    pass