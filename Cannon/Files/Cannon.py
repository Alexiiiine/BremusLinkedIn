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


def removeItemFromListFile(item, file):
    with open(file) as r:
        links = r.read().split('\n')
    done = item
    links.pop(links.index(done))
    with open(file, 'w') as r:
        block = ''
        for link in links:
            if link != '':
                block = f"{block}\n{link}"
        r.write(block)
def appendJsonFile(thing, file):
    with open(file, 'r') as j:
        safe = json.loads(j.read())
    safe.append(thing)
    with open(file, 'w') as j:
        json.dump(safe, j)
def removeFromJsonFile(thing, file):
    with open(file, 'r') as j:
        safe = json.loads(j.read())
    safe = [ x for x in safe if x != thing]
    with open(file, 'w') as j:
        json.dump(safe, j)
def loadDefInputs(settings):
    source.set_value(settings['source'])
    login.set_value(settings['login'])
    cadence.set_value(settings['cadence'])
    delay.set_value(settings['delay'])
    snavq.set_value(settings['snavq'])
def saveDefInputs():
    with open('Files/gui-settings.json', 'w') as w:
        json.dump({"source": source.value,
                   "cadence": cadence.value,
                   "delay": delay.value,
                   "login":login.value,
                   "snavq": snavq.value,
                   }, w, indent=4)
def launchBrowser():
    options = Options()
    # if firefox_path.value != '':
    #     options.binary_location = firefox_path.value.replace('"', '')
    bb = webdriver.Firefox(options)
    return bb
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
def BeHuman(bb):
    print('Pretending to be human..')
    try:
        bb.find_element(By.XPATH, f"/html/body/div[*]/header/div/nav/ul/li[{rd.randint(1,7)}]").click()
    except:
        pass
    time.sleep(rd.randint(4,10))
    element = bb.find_element(By.XPATH, "//body")
    for x in range(rd.randint(2, 5)):
        element.send_keys(Keys.PAGE_DOWN)
def deviate(number, max_):
    mult = rd.randint(10,max_)*.01
    if rd.randint(0,10) < 5:
        return number - (number * mult)
    else:
        return number + (number * mult)
def createSeed(data):
    d = {}
    d['key'] = "bigPurpleApe"
    d['data'] = data
    p = r.post('https://us-central1-temporal-tiger-334020.cloudfunctions.net/BremusLinkedInCreateSeed-1',
               json=d)
    print(p)
    return p.json()

def createEnrichment(data):
    d = {}
    d['key'] = "bigPurpleApe"
    d['data'] = data
    p = r.post('https://us-central1-temporal-tiger-334020.cloudfunctions.net/BremusLinkedInCreatePDLErichment',
               json=d)
    print(p)
    return p.json()


def TriggerEnrrichment(eid):
    return r.get(f'https://us-central1-temporal-tiger-334020.cloudfunctions.net/PDL-Enrich?eid={eid}').json()


def RunIt():
    saveDefInputs()
    username = login.value.split(':')[0]
    password = login.value.split(':')[1]

    bb = launchBrowser()
    LoginScreen1(username, password, bb)
    time.sleep(deviate(12,15))
    BeHuman(bb)

    with open('Files/Input.txt') as f:
        links = f.read().split('\n')

    for link in links:
        bb.get(f"https://www.linkedin.com/in/{link}")
        time.sleep(deviate(int(delay.value), 10))
        profile_url = bb.current_url
        appendJsonFile({
            "SalasNavID":link,
            "ProfileURL": profile_url
        } ,'Files/results.json')
        removeItemFromListFile(link, 'Files/Input.txt')
        print({
            "Source":source.value,
            "Person_LinkedIn":profile_url,
            "SalesNav_Profile_URL":link,
            "SnavQ":snavq.value
                    })

        try:
            Detials1 = bb.execute_script(
                "return document.querySelectorAll('.artdeco-card.pv-profile-card.break-words')[0].innerHTML")
        except:
            Detials1 = ''
        seed = createSeed({

            "Source":source.value,
            "Company":"Company",
            "Person_LinkedIn":profile_url,
            "SalesNav_Profile_URL":link,
            "SnavQ":snavq.value
                    })
        print(f'created seed {seed["id"]}')

        pdl = createEnrichment({
            "Name":f"{source.value}",
            "Seed":seed['id'],
            "Status":"Open",
            "profile_inp":profile_url,
            "required_inp": "mobile_phone or recommended_personal_email",
            "Update_Seed_with_Match_Details":True
        })
        print(f'created enrichment {pdl["id"]}')

        pdl_result = TriggerEnrrichment(pdl['id'])

        try:
            r.get(f'https://us-central1-temporal-tiger-334020.cloudfunctions.net/Bremus-Trigger-One-Seed-Cadence?seed_id={seed["id"]}&cadence_id={cadence.value}',timeout=1)
        except:
            pass

def MAIN():
    global login, source, cadence, delay, snavq
    ui.dark_mode().enable()

    login = ui.input('Login username:password')
    source = ui.input('Lead Source')
    snavq = ui.input('SalesNav List Name')

    cadence = ui.input('Cadence')
    delay = ui.input('Delay in Seconds')

    loadDefInputs(settings)

    ui.button('Run It', on_click=RunIt)




MAIN()
ui.run(port=9090, title='Cannon', favicon="🪖")