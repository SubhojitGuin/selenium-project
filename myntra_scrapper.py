# -- Import the necessary libraries --
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium. webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
import logging
import openpyxl
import traceback
import re

import time
from datetime import datetime

service = Service('chromedriver.exe')

wb = openpyxl.Workbook()
sheet = wb.active

# -- Get the Driver --
def get_driver(link: str):
    # Set options to make browsing easier
    options = webdriver.ChromeOptions()
    options.add_argument("disable-infobars")  # to prevent the infobars popups to interfere with the script
    options.add_argument("start-maximized")  # some webpages may change the content depending on the size of the window so we access the maximized version of the browser
    options.add_argument("disable-dev-shm-usage")  # to avoid issues while interacting with the browser on a linux computer and replit is a linux computer
    options.add_argument("no-sandbox")  # to disable sandbox in the browser
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("disable-blink-features=AutomationControlled")
    options.add_argument("--incognito")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(link)

    return driver

# ---- New Logging Process ----
def newloggingfunction():
    global print
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger()
    logger.addHandler(logging.FileHandler("log.txt", "w"))
    print = logger.info
    return logger.info

# ---- Remove emoji from the string ----
def remove_emojis(text):
    # Emoji regex pattern
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        "\U0001F700-\U0001F77F"  # Alchemical Symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed Alphanumeric Supplement
        "]+", 
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def navigate_and_extract_review(Driver):
    global OutputPath

    # -- Check for the home page to load --
    try:
        wait(Driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Ratings')]")))
        print("Home Page loaded")
    except:
        print("!!! Unable to load the Home Page")
        return True
    
    # -- Extract the number of iterations --
    try:
        Iterations = wait(Driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Customer Reviews (')]"))).text
        Iterations = Iterations.split("(")[1].split(")")[0]
        Iterations = int(Iterations)
        print("Number of Iterations: ", Iterations)
    except:
        print("!!! Unable to extract the number of iterations")
        return True
    
    # -- Scraping Logic for extracting reviews --
    for Search in range(1, Iterations + 1):
        print("\n============ Running Review : " + str(Search) + " ============\n")

        try:
            # -- Extract the ratings --
            RatingsObj = wait(Driver, 60).until(EC.presence_of_element_located((By.XPATH, "(//span[contains(@class, 'user-review-starRating')])[" + str(Search) + "]")))
            ActionChains(Driver).scroll_to_element(RatingsObj)
            Ratings = RatingsObj.text
            print("Ratings: ", Ratings)

            # -- Extract the review --
            Review = wait(Driver, 10).until(EC.presence_of_element_located((By.XPATH, "(//div[contains(@class, 'user-review-reviewTextWrapper')])[" + str(Search) + "]"))).text
            Review = remove_emojis(Review)
            print("Review: \n", Review)

            row = [Ratings, Review]

            try:
                sheet.append(row)
                wb.save(OutputPath)
            except:
                print(traceback.format_exc())
                print("!!! Issue in writing data")
                raise Exception

            print("\nData written\n")

            # ActionChains(Driver).scroll_to_element(RatingsObj)
            # Driver.execute_script(f"document.querySelector('.user-review-reviewTextWrapper:nth-child({Search})').scrollIntoView();", RatingsObj)
            # Driver.execute_script("window.scrollTo(arguments[0]);", RatingsObj)
            Driver.execute_script("arguments[0].scrollIntoView();", RatingsObj)

        except:
            # try:
            #     wait(Driver, 15).until(EC.presence_of_element_located((By.XPATH, "(//span[contains(@class, 'user-review-starRating')])[" + str(Search - 1) + "]"))).text
            #     ReviewCount += Search - 1
            #     print("\n=============== All the review ended for this page ========================\n")
            #     print("***** Review Count : " + str(ReviewCount) + " *****")
            #     time.sleep(2)
            #     break
            # except:
                print("!!! Issue in fetching review\n")
                print(traceback.format_exc())
                return True

# =============================== Enter the details of the product here ==============================

url = "https://www.myntra.com/reviews/1963297"

OutputPath = "Report.xlsx"

# ================================================================================================

# ---- Logging Process ----
# print = newloggingfunction()


if __name__ == '__main__':
    print("\n************************* Automation process started *********************\n")

    if not url:
        print("!!! Please enter the URL of the product")
        exit

    # -- Create the chrome driver --
    Driver = get_driver(url)

    # -- Navigate to the product page and extract the review --
    navigate_and_extract_review(Driver)

    # -- Close the driver --
    Driver.quit()
    print("\n************************** Automation process ended **********************\n")
