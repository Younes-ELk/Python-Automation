import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# Path to chromedriver executable
chrome_driver_path = "chromedriver.exe"

# Path to download directory
download_directory = "downloads"

# Ensure download directory exists
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Set Chrome options to set download directory
chrome_options = webdriver.ChromeOptions()
prefs = {"download.default_directory": os.path.abspath(download_directory)}
chrome_options.add_experimental_option("prefs", prefs)

# Initialize Chrome driver
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL of the website
url = "https://englishhub.oup.com/myCourses"

# Navigate to the website
driver.get(url)

# Login process
input_element = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.NAME, "j_username"))
)
input_element.clear()
input_element.send_keys("y.elkortih@lpn.ma")

input_element = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.NAME, "j_password"))
)
input_element.clear()
input_element.send_keys("Test@2024")

submit_button = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
)
submit_button.click()

# Wait for the "Teacher" section to be clickable and click on it
teacher_button = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.CLASS_NAME, "_21sG"))
)
teacher_button.click()

# Wait for the "Card" section to be clickable and click on it
card_button = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.CLASS_NAME, "_1FxH"))
)
card_button.click()

# Wait for the "Resources" section to be clickable and click on it
resources_button = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.CLASS_NAME, "_25zj"))
)
resources_button.click()

# Function to handle stale element reference exception
def handle_stale_element(driver, by, value):
    for _ in range(5):
        try:
            return driver.find_elements(by, value)
        except StaleElementReferenceException:
            time.sleep(1)
    return []

# Function to check if a file is completely downloaded
def is_download_complete(download_path, file_name):
    return not file_name.endswith('.crdownload')

# Function to sanitize folder names
def sanitize_folder_name(name):
    # Replace invalid characters with underscores
    return name.replace(':', '_').replace('/', '_').replace('\\', '_')

# Get all folders
folders = handle_stale_element(driver, By.CLASS_NAME, "_23A3")

# Initialize index to keep track of current folder
current_folder_index = 0

# Iterate over each folder starting from the current index
while current_folder_index < len(folders):
    try:
        # Get the folder name
        folder_name = sanitize_folder_name(folders[current_folder_index].text.strip())
        folder_path = os.path.join(download_directory, folder_name)
        
        # Check if the folder has already been processed
        if os.path.exists(folder_path) and os.listdir(folder_path):
            print(f"Skipping already downloaded folder: {folder_name}")
            current_folder_index += 1
            continue
        
        # Ensure category folder exists
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # Click on the folder at the current index
        folders[current_folder_index].click()
        
        # Wait for the files to load
        time.sleep(5)
        
        # Get all download buttons in the folder
        download_buttons = handle_stale_element(driver, By.CLASS_NAME, "_3hPx")
        
        # Iterate over each download button and click it to download the file
        for button in download_buttons:
            file_name = button.get_attribute('download')
            if file_name and os.path.exists(os.path.join(folder_path, file_name)):
                print(f"File already exists: {file_name}")
                continue
            button.click()
            
            # Optional: Wait for download to complete before proceeding
            time.sleep(3)
        
        # Move downloaded files to the specific category folder
        for file_name in os.listdir(download_directory):
            file_path = os.path.join(download_directory, file_name)
            if not os.path.isdir(file_path) and is_download_complete(download_directory, file_name):
                destination_path = os.path.join(folder_path, file_name)
                print(f"Moving file {file_path} to {destination_path}")
                shutil.move(file_path, destination_path)
        
        # Go back to the resources page
        driver.back()
        
        # Wait for the folders to load again
        time.sleep(5)
        
        # Re-fetch the folders
        folders = handle_stale_element(driver, By.CLASS_NAME, "_23A3")
        
        # Increment the current folder index to move to the next folder
        current_folder_index += 1
    
    except (StaleElementReferenceException, TimeoutException) as e:
        # Handle stale element reference exception by re-fetching the folders
        print(f"Exception occurred: {e}. Retrying...")
        folders = handle_stale_element(driver, By.CLASS_NAME, "_23A3")

# Quit the driver
driver.quit()

# Print completion message
print("All downloads are complete. The script has finished execution.")
