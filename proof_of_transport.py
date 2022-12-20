from playwright.sync_api import sync_playwright
import click


@click.command()
@click.argument('login')
@click.argument('password')
def proof_of_transport(login, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://www.cts-strasbourg.eu/fr/connexion/')
        page.get_by_label("Adresse email").fill(login)
        page.get_by_label("Mot de passe").fill(password)
        page.locator("#login-form-submit").get_by_role("link",
                                                       name="Se connecter").click()
        page.wait_for_selector('css=div.my-account')
        page.goto(
            'https://www.cts-strasbourg.eu/fr/Titres-de-transport/agence-en-ligne/historique-dachats/')
        page.wait_for_selector('div#partie2')
        with page.expect_download() as download_info:
            page.locator(
                '//*[@id="table_result"]/tbody/tr[1]/td[6]/button').click()

        download = download_info.value
        print(download.path())

        download.save_as("./proof.pdf")


if __name__ == '__main__':
    proof_of_transport()
