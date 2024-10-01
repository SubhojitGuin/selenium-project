from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
from datetime import datetime
import logging
import re
import pandas as pd
import openpyxl
import traceback

service = Service('chromedriver.exe')

file_path = "Report.xlsx"
wb = openpyxl.Workbook()
sheet = wb.active


# ---- Get the driver ----
def get_driver(url: str):
    # Set options to make browsing easier
    options = webdriver.ChromeOptions()
    options.add_argument("disable-infobars")  # to prevent the infobars popups to interfere with the script
    options.add_argument("start-maximized")  # some webpages may change the content depending on the size of the window so we access the maximized version of the browser
    options.add_argument("disable-dev-shm-usage")  # to avoid issues while interacting with the browser on a linux computer and replit is a linux computer
    options.add_argument("no-sandbox")  # to disable sandbox in the browser
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("disable-blink-features=AutomationControlled")
    options.add_argument('--incognito')

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

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

# ---- Navigate to the product page and extract the review ----
def navigate_and_extract_review(Driver):

    Driver.implicitly_wait(10)

    # check if the home page is loaded successfully
    try:
        ProductText = WebDriverWait(Driver, 90).until(EC.visibility_of_element_located((By.XPATH, "//span[contains(@id, 'productTitle')]"))).text
        time.sleep(1)
        print("Product page loaded successfully")
        print("Product : '" + ProductText + "'")
    except:
        print("!!! Unable to load the Home Page")
        return True
    
    # click on the review link
    try:
        WebDriverWait(Driver, 90).until(EC.visibility_of_element_located((By.XPATH, "//a[contains(text(), 'See more reviews')]"))).click()
        time.sleep(1)
        print("'See more reviews' link clicked successfully")
    except:
        print("!!! Unable to click the 'See more reviews' link")
        return True
    
    # check if the review page is loaded successfully
    try:
        WebDriverWait(Driver, 90).until(EC.visibility_of_element_located((By.XPATH, "//h2[contains(text(), 'Customer reviews')]")))
        time.sleep(1)
        print("Review page loaded successfully")
    except:
        print("!!! Unable to load the Review Page")
        return True

    # # Create an Excel file and add headers if it doesn't exist
    # excel_file = 'reviews.xlsx'
    # try:
    #     load_workbook(excel_file)
    # except:
    #     df = pd.DataFrame(columns=['Ratings', 'Review1', 'Review2'])
    #     df.to_excel(excel_file, index=False)
    
    # extract the reviews - using Pagination
    PageNo = 1
    ReviewCount = 0

    while True:
        print("\n================================ Page No. : " + str(PageNo) + " ===============================\n")

        # Extract review star ratings
        review_stars = Driver.find_elements(By.XPATH, "//i[contains(@data-hook,'review-star-rating')]//span[contains(text(), 'out of 5 stars')]")
        # extract the reviews
        for Search in range(1, 1000):
            print("\n============= Running review : " + str(Search) + " ==================\n")
            try:
                # extract the review 1
                ReviewText1 = WebDriverWait(Driver, 15).until(EC.visibility_of_element_located((By.XPATH, "(//div[contains(@data-hook, 'review')]//div[contains(@id, 'customer_review')]//*[@data-hook='review-title']/span[last()])[" + str(Search) + "]"))).text
                ReviewText1 = remove_emojis(ReviewText1)
                print("Review 1 : \n" + ReviewText1)

                # extract the review 2
                ReviewText2 = WebDriverWait(Driver, 15).until(EC.visibility_of_element_located((By.XPATH, "(//span[contains(@data-hook, 'review-body')]/span)[" + str(Search) + "]"))).text
                ReviewText2 = remove_emojis(ReviewText2)
                print("\nReview 2 : \n" + ReviewText2)

                # extract the ratings
                Ratings = review_stars[Search - 1].get_attribute("innerText")
                Ratings = Ratings.split(" ")[0]
                print("\nRatings : " + str(Ratings))

                # Log the extracted review data
                # print(f"Logged Review {Search}:\n Ratings: {Ratings}\n Review 1: {ReviewText1}\n Review 2: {ReviewText2}")

                row = [Ratings, ReviewText1, ReviewText2]

                try:
                    sheet.append(row)
                    wb.save(file_path)
                except:
                    print(traceback.format_exc())
                    print("!!! Issue in writing data")
                    raise Exception

                print("\nData written\n")
                
            except:
                try:
                    WebDriverWait(Driver, 15).until(EC.visibility_of_element_located((By.XPATH, "(//span[contains(@data-hook, 'review-body')]//span)[" + str(Search - 1) + "]"))).text
                    ReviewCount += Search - 1
                    print("\n=============== All the review ended for this page ========================\n")
                    print("***** Review Count : " + str(ReviewCount) + " *****")
                    time.sleep(2)
                    break
                except Exception as e:
                    print("!!! Issue in fetching review\n")
                    print(traceback.format_exc())
                    time.sleep(5000)
                    return True
                
        try:
            # click on the next page
            WebDriverWait(Driver, 15).until(EC.visibility_of_element_located((By.XPATH, "//a[contains(text(), 'Next page')]"))).click()
            time.sleep(1)
            PageNo += 1
            print("Next page clicked successfully")
        except:
            print("\n================================= All the review ended  ==============================================\n")
            break
    
    time.sleep(5)
    print("\nReviews have been saved to 'reviews.xlsx'\n")


# =============================== Enter the url of the product here ==============================

# url = 'Product URL'
# url = 'https://www.amazon.in/dp/B0D2D54Q5M/ref=QAHzEditorial_en_IN_1?pf_rd_r=PMT39WEKVTAJQENGBGRY&pf_rd_p=0447edbc-ea13-4a53-b7b4-1dcedf1ef7ce&pf_rd_m=A1VBAL9TL5WCBF&pf_rd_s=merchandised-search-3&pf_rd_t=&pf_rd_i=1389401031&th=1'

# url = 'https://www.amazon.in/dp/B00OTNQPSK?ref_=cm_sw_r_apan_dp_R1YGFATZPKK5T38X905S&language=en-IN'

url = 'https://www.amazon.in/Apple-iPhone-13-128GB-Starlight/dp/B09G9D8KRQ/ref=sr_1_3?dib=eyJ2IjoiMSJ9.OCoJgZ8ghdguKvc7Ozmt3KaCD--RvXmzm6jcMLd6bpmK_O4aZboegL4nccF38CUd3NBq-Q-bn2jnEiAKvRVW0Mqy770EeqlJ8MqsNzg1GYK-n2_sTMHDNZ-kwbzl7tcdF1DwUm9RGbDxDRxyKY8umFDMxSvp80qGtcaEbnbmKLcsVbp5BKocsjPahTN9OHTfzwAPJ8uuO4SUx6fKstE8vqJUHfgfs-nPMwlOowK4fqHhe9prFzBQm2M_Gg9VwHZyMXkIM-B7iVTu8jW9XDG4BVc1d-EzVpoG05QrE8kODJo.Su3sp_ouJEjPI_T8AUrUBAcB3VrnG18STMTeXYTkqh8&dib_tag=se&keywords=iphone&qid=1722327078&s=electronics&sr=1-3'

# ================================================================================================

# ---- Logging Process ----
print = newloggingfunction()


if __name__ == '__main__':
    print("\n************************* Automation process started *********************\n")
    # create the chrome driver
    Driver = get_driver(url)

    # navigate to the product page and extract the review
    navigate_and_extract_review(Driver)

    # close the driver
    Driver.quit()
    print("\n************************** Automation process ended **********************\n")
