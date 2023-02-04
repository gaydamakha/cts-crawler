import click
from proof_of_transport.crawlers import download_last_proof_of_transport


@click.command()
@click.argument('login')
@click.argument('password')
def cli(login: str, password: str):
    download_last_proof_of_transport(login, password)


if __name__ == '__main__':
    cli()
