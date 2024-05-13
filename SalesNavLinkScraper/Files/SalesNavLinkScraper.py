from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, re, datetime as dt, random as rd, pickle, json, requests as r, json, random as rd
from selenium.webdriver.firefox.options import Options
from nicegui import ui, native
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains



with open('Files/gui-settings.json', 'r') as f:
    settings = json.loads(f.read())


def BeHuman(bb):
    element = bb.find_element(By.XPATH, "//body")
    for x in range(rd.randint(2, 5)):
        element.send_keys(Keys.PAGE_DOWN)


def LoginScreen1(username, password, bb):
    bb.get(
        "https://www.linkedin.com/feed/")

    # Wait for the login form to load
    wait = WebDriverWait(bb, 10)
    login_form = wait.until(EC.presence_of_element_located((By.ID, 'username')))

    # Enter your LinkedIn username and password
    username_field = bb.find_element(By.ID, 'username')
    username_field.send_keys(username)
    password_field = bb.find_element(By.ID, 'password')
    password_field.send_keys(password)

    # Submit the login form
    login_button = bb.find_element(By.XPATH, "//button[@data-litms-control-urn='login-submit']")
    login_button.click()
    time.sleep(3)


def launchBrowser():
    options = Options()
    if firefox_path.value != '':
        options.binary_location = firefox_path.value.replace('"', '')
    bb = webdriver.Firefox(options)
    return bb


def loadDefInputs(settings):
    snav.set_value(settings['snav'])
    firefox_path.set_value(settings['firefox_path'])
    login.set_value(settings['login'])


def saveDefInputs():
    with open('Files/gui-settings.json', 'w') as w:
        json.dump({"snav": snav.value,
                   "firefox_path": firefox_path.value,
                   "login": login.value}, w, indent=4)


def Scroll(bb):
    # bb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    element = bb.find_element(By.XPATH, "//body")
    element.click()
    for x in range(1):
        element.send_keys(Keys.PAGE_DOWN)

def handleSnavNavigation(bb):
    time.sleep(1)
    bb.find_element(By.XPATH, "/html/body/div[5]/header/div/nav/ul/li[8]").click()
    time.sleep(10)
    bb.switch_to.window(bb.window_handles[1])
    bb.close()
    bb.switch_to.window(bb.window_handles[0])
    time.sleep(2)


def saveToLogs(to_save):
    with open('Files/output.txt', 'r') as f:
        logs = f.read().split('\n') + to_save
        lunk = ''
        for l in logs:
            lunk = lunk + f"\n{l}"
        f.close()
    with open('Files/output.txt', 'w') as w:
        w.write(lunk)



def run_button_click():
    print('Open up Browser')
    postChat('opening browser')

    saveDefInputs()
    username = login.value.split(':')[0]
    password = login.value.split(':')[1]

    bb = launchBrowser()

    LoginScreen1(username, password, bb)
    time.sleep(10)
    handleSnavNavigation(bb)

    bb.get(snav.value)
    for page in range(99):
        bb.get(snav.value+f'&page={page+1}')
        time.sleep(3)

        hrefs = []
        for x in range(5):
            hrefs = hrefs + [x.get_attribute('href').split(',')[0].split('lead/')[1] for x in bb.find_elements(By.XPATH, "//a[contains(@href, 'sales/lead')]")]
            Scroll(bb)
            time.sleep(1)

        unique = []
        for h in hrefs:
            if h not in unique:
                print(h)
                unique.append(h)
        print(len(unique))
        saveToLogs(unique)
        time.sleep(rd.randint(2,6))

    time.sleep(100)


@ui.refreshable
def MAIN():
    global login, snav, login, firefox_path

    ui.dark_mode().enable()
    login = ui.input('Login username:password')
    firefox_path = ui.input('Firefox Path (optional)')
    snav = ui.input('SalesNav Q')

    loadDefInputs(settings)
    ui.button('Run', on_click=run_button_click)
    ui.chat_message('Welcome to Salesnav Link Scraper',
                    name='Bremus',
                    stamp='now',
                    avatar='https://storage.googleapis.com/publicbucketboyss/Bremus%20Chemist%20Circle.png')
    ui.link('Guide Found Here', 'https://nicegui.io/documentation/section_text_elements')

def postChat(msg):
    ui.chat_message(msg,
                    name='Bremus',
                    stamp='now',
                    avatar='https://storage.googleapis.com/publicbucketboyss/Bremus%20Chemist%20Circle.png')

MAIN()


ui.run(port=90, title='Bremus Salesnav Scraper', favicon="🤺")
