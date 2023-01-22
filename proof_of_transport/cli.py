import click
from .functions import proof_of_transport


@click.command()
@click.argument('login')
@click.argument('password')
def cli(login: str, password: str):
    proof_of_transport(login, password)


if __name__ == '__main__':
    cli()
