from kiteconnect import KiteConnect
from kiteconnect import KiteTicker

from time import sleep
from platform import system
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from send_log import SendLog

def KiteLogin():
    PATH = "C:\Program Files (x86)\chromedriver.exe" if ("Windows" in system()) else "/usr/bin/chromedriver"
    API_KEY = "Enter API Key here"
    API_SECRET = "Enter API Secret here"

    while (True):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(PATH, options=chrome_options)
        driver.get("https://kite.trade/connect/login?api_key=" + API_KEY +
                "&v=3")

        sleep(1.5)

        formDiv = driver.find_element_by_class_name("login-form")
        loginBtn = driver.find_element_by_class_name(
            "actions").find_element_by_tag_name("button")
        loginInputs = formDiv.find_elements_by_tag_name("input")
        userIdInput = loginInputs[0]
        passwordInput = loginInputs[1]

        userIdInput.clear()
        passwordInput.clear()

        userIdInput.send_keys("GR6439")
        passwordInput.send_keys("fenozig761zag")
        loginBtn.click()

        sleep(2)

        pinInput = driver.find_element_by_tag_name("input")
        pinInput.clear()
        pinInput.send_keys("164307")
        driver.find_element_by_class_name("actions").find_element_by_tag_name(
            "button").click()

        sleep(4)

        currUrl = driver.current_url

        if "success" in currUrl:
            REQUEST_TOKEN = currUrl.split("request_token=")[1].split("&action=")[0]
            driver.quit()
            print(f"\nKite Login Request Token is {REQUEST_TOKEN}\n")
            break
        else:
            driver.quit()
            SendLog("Kite Login Failure getting Access Token. Retrying...")
            sleep(8)

    kite = KiteConnect(api_key=API_KEY)
    data = kite.generate_session(REQUEST_TOKEN, api_secret=API_SECRET)
    ACCESS_TOKEN = data["access_token"]
    kite.set_access_token(ACCESS_TOKEN)

    # Initialise
    kws = KiteTicker(API_KEY, ACCESS_TOKEN)
    kws._startedBefore = False

    return kite, kws