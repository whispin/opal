
import os
import sys
from fastapi.applications import FastAPI
import typer
from typer.main import Typer

# Add parent path to use local src as package for tests
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(root_dir)

from opal_client.config import opal_client_config
from opal_common.config import opal_common_config
from opal_common.corn_utils import run_gunicorn, run_uvicorn
from opal_common.cli.typer_app import get_typer_app

app = get_typer_app()


@app.command()
def run(engine_type: str = typer.Option("uvicron", help="uvicorn or gunicorn")):
    """
    Run the client as a deamon 
    """
    typer.echo(f"-- Starting OPAL client (with {engine_type}) --")

    if engine_type == 'gunicorn':
        app:FastAPI 
        from opal_client.main import app
        run_gunicorn(app, opal_client_config.CLIENT_API_SERVER_WORKER_COUNT,
                     host=opal_client_config.CLIENT_API_SERVER_HOST,
                     port=opal_client_config.CLIENT_API_SERVER_PORT)
    else:
        run_uvicorn("opal_client.main:app",
                    workers=opal_client_config.CLIENT_API_SERVER_WORKER_COUNT,
                    host=opal_client_config.CLIENT_API_SERVER_HOST,
                    port=opal_client_config.CLIENT_API_SERVER_PORT)


@app.command()
def print_config():
    """
    To test config values, print the configuration parsed from ENV and CMD
    """
    typer.echo("Printing configuration values")
    typer.echo(str(opal_client_config))
    typer.echo(str(opal_common_config))


cli_header = """\b
OPAL-CLIENT
Open-Policy Administration Layer - client\b\f"""

cli_docs = """\b
Config top level options:
 - Use env-vars (same as cmd options) but uppercase and with "_" instead of "-"; all prefixed with "OPAL_"
 - Use command line options as detailed by '--help'
 - Use .env or .ini files    

\b
Examples:
 - opal-client run --help                       Help on run command
 - opal-client run --engine-type gunicorn       Run client with gunicorn
\b
"""

def cli():
    def on_start(**kwargs):
        typer.secho(cli_header, bold=True, fg=typer.colors.MAGENTA)
    opal_client_config.cli([opal_common_config], typer_app=app, help=cli_docs, on_start=on_start)

if __name__ == "__main__":
    cli()