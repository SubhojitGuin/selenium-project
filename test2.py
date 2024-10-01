from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up the WebDriver (e.g., ChromeDriver)
service = Service('chromedriver.exe')  # Change this to the path where you have placed your chromedriver
driver = webdriver.Chrome(service=service)

# Navigate to the Amazon product page
product_url = 'https://www.amazon.in/dp/B00OTNQPSK?ref_=cm_sw_r_apan_dp_R1YGFATZPKK5T38X905S&language=en-IN'  # Change this to the URL of the product you're interested in
driver.get(product_url)

# Wait for the reviews section to load
wait = WebDriverWait(driver, 10)
reviews_section = wait.until(EC.presence_of_element_located((By.ID, 'reviewsMedley')))

# Scroll down to the reviews section
actions = ActionChains(driver)
actions.move_to_element(reviews_section).perform()

# Extract review star ratings
review_stars = driver.find_elements(By.XPATH, "//i[contains(@class, 'review-rating')]//span[contains(@class, 'a-icon-alt')]")

# Print out the star ratings
for star in review_stars:
    print(star.get_attribute("innerText"))

# Close the WebDriver
driver.quit()
