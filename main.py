from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime

service = Service('chromedriver.exe')


def get_driver():
    # Set options to make browsing easier
    options = webdriver.ChromeOptions()
    options.add_argument(
        "disable-infobars")  # to prevent the infobars popups to interfere with the script
    options.add_argument(
        "start-maximized")  # some webpages may change the content depending on the size of the window so we access the maximized version of the browser
    options.add_argument(
        "disable-dev-shm-usage")  # to avoid issues while interacting with the browser on a linux computer and replit is a linux computer
    options.add_argument("no-sandbox")  # to disable sandbox in the browser
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://automated.pythonanywhere.com/login/")
    return driver


def clean_text(text: str) -> str:
    """Extract only the temperature from the text"""
    output = float(text.split(": ")[1])
    return output


def write_to_file(text: str):
    """Write the text to a file"""
    present_time = datetime.now().strftime("%Y-%m-%d.%H-%M-%S")
    with open(f"{present_time}.txt", "w") as file:
        file.write(text)


def main():
    driver = get_driver()

    # time.sleep(2)
    # element = driver.find_element(by='xpath', value='/html/body/div[1]/div/h1[2]')
    # return clean_text(element.text)

    # Find and fill the username and password
    driver.find_element(by='id', value='id_username').send_keys("automated")
    time.sleep(2)
    driver.find_element(by='id', value='id_password').send_keys(
        "automatedautomated" + Keys.RETURN)
    # time.sleep(2)
    # driver.find_element(by='id', value='submit').click()
    time.sleep(2)

    # Click on the Home button on the nav bar
    driver.find_element(by='xpath', value='/html/body/nav/div/a').click()
    time.sleep(2)

    while True:
        # Find and exract on the temperature
        element = driver.find_element(by='xpath',
                                      value='/html/body/div[1]/div/h1[2]')
        # return clean_text(element.text)
        write_to_file(element.text)

        time.sleep(2)
    # return present_time


print(main())
