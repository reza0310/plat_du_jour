from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from pynput.keyboard import Key, Controller


def init_nav():
    binary = FirefoxBinary(r"C:\\Program Files\\Mozilla Firefox\\firefox.exe")
    caps = DesiredCapabilities.FIREFOX.copy()
    caps['marionette'] = True
    navigateur = webdriver.Firefox(firefox_binary=binary, capabilities=caps,
                                   executable_path="geckodriver.exe") #Modifier le chemin ici
    navigateur.wait = WebDriverWait(navigateur, 5)
    return navigateur


def cliquer(methode, chemin):
    try:
        if methode == "xpath":
            bouton = navigateur.wait.until(EC.visibility_of_element_located((By.XPATH, chemin)))
        elif methode == "element":
            bouton = navigateur.wait.until(EC.visibility_of_element_located(chemin))
        elif methode == "selec_css":
            bouton = navigateur.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, chemin)))
    except:
        if methode == "xpath":
            bouton = navigateur.find_element_by_xpath(chemin)
        elif methode == "element":
            bouton = chemin
        elif methode == "selec_css":
            bouton = navigateur.find_element_by_css_selector(chemin)
    bouton.click()


def cliquer_droit(methode, chemin):
    try:
        if methode == "xpath":
            bouton = navigateur.wait.until(EC.visibility_of_element_located((By.XPATH, chemin)))
        elif methode == "element":
            bouton = navigateur.wait.until(EC.visibility_of_element_located(chemin))
        elif methode == "selec_css":
            bouton = navigateur.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, chemin)))
    except:
        if methode == "xpath":
            bouton = navigateur.find_element_by_xpath(chemin)
        elif methode == "element":
            bouton = chemin
        elif methode == "selec_css":
            bouton = navigateur.find_element_by_css_selector(chemin)
    actions.context_click(bouton).perform()


def remplir(xpath, texte, soumettre):
    box = navigateur.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
    sleep(1)
    box.send_keys(texte)
    if soumettre[0]:
        cliquer("xpath", soumettre[1])


def prendre_donnees(chemin):
    try:
        element = navigateur.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, chemin)))
    except:
        element = navigateur.find_element_by_css_selector(chemin)
    return element.text


navigateur = init_nav()
actions = ActionChains(navigateur)
clavier = Controller()
page = 1
navigateur.get(f"https://www.marmiton.org/recettes/?type=platprincipal&page={str(page)}")
cliquer("xpath", "/html/body/div[1]/div/div/div/div/div/div[3]/button[2]/span")

with open("donnees.txt", "w", encoding="utf-8") as fichier:
    while page < 900:
        for recette in range(30):
            navigateur.execute_script(f"window.scrollTo(0, {str(360 + 200 * recette)})")
            try:
                cliquer("selec_css", f"div.recipe-card:nth-child({recette+1}) > a:nth-child(1) > div:nth-child(1) > picture:nth-child(1) > img:nth-child(3)")
            except:
                try:
                    cliquer("selec_css", "img.ls-is-cached:nth-child(1)")
                except:
                    continue
            navigateur.execute_script("window.scrollTo(0, 200)")
            try:
                temps = prendre_donnees(".recipe-infos__total-time__value")
                difficulte = prendre_donnees(".recipe-infos__level")
                prix = prendre_donnees(".recipe-infos__budget")
                url = navigateur.current_url
                fichier.write(temps+"; "+difficulte+"; "+prix+"; "+url+"\n")
            except:
                continue
            try:
                navigateur.execute_script("window.history.go(-1)")
            except:
                continue
        print("page "+str(page)+" terminée")
        page += 1
        navigateur.get(f"https://www.marmiton.org/recettes/?type=platprincipal&page={str(page)}")
    navigateur.quit()