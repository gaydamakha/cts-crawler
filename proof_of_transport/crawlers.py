import os.path

from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError

from proof_of_transport.exceptions import LoginException


def download_last_proof_of_transport(login, password) -> str:
    """Downloads a last proof of transport and returns its absolute filepath"""
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto('https://www.cts-strasbourg.eu/fr/connexion/')
        try:
            # Close possible dialogs
            page.get_by_role("button", name="Ok",).click()
        except TimeoutError:
            pass
        page.get_by_label("Adresse email").fill(login)
        page.get_by_label("Mot de passe").fill(password)
        page.locator("#login-form-submit").get_by_role("link",
                                                       name="Se connecter").click()
        page.wait_for_load_state(state="networkidle")
        if page.url.endswith('autherror=true'):
            raise LoginException('Login failed')

        page.wait_for_selector('css=div.my-account')
        page.goto(
            'https://www.cts-strasbourg.eu/fr/Titres-de-transport/agence-en-ligne/historique-dachats/')
        page.wait_for_selector('div#partie2')
        with page.expect_download() as download_info:
            page.locator(
                '//*[@id="table_result"]/tbody/tr[1]/td[6]/button').click()
        download = download_info.value
        filepath = "/tmp/" + download.suggested_filename
        download.save_as(filepath)
        return os.path.abspath(filepath)
