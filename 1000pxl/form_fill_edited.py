import os
import time
from pathlib import Path
import pyautogui
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import wget
import requests

# save as save_wordsearch_pdf.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import base64
import time


# Configure Chrome options to disable the security data breach messages
chrome_options = Options()
prefs = {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.password_manager_leak_detection": False
}
chrome_options.add_experimental_option("prefs", prefs)

# Initialize the driver with these options
driver = webdriver.Chrome(options=chrome_options)

## Images loading - Updated path based on your exact folder structure
# Change this path below if the files are in a different folder!
files_path = Path(r"C:\Users\pc\Desktop\OLD\Selenium\countriesfilled\Choosen\1000pxl")

# Look for .jpg, .JPG, .jpeg, and .JPEG to be safe against Windows extension quirks
extensions = ('*.jpg', '*.JPG', '*.jpeg', '*.JPEG')
files_list = []
for ext in extensions:
    files_list.extend([f.stem for f in files_path.glob(ext)])

# Debugging helper prints:
print(f"Checking directory: {files_path.resolve()}")
print(f"Total files found matching criteria: {len(files_list)}")

if not files_list:
    print(f"\n[ERROR] No images found. Real contents of this folder are:")
    try:
        for item in files_path.iterdir():
            print(f" - {item.name}")
    except Exception as e:
        print(f" Could not read directory: {e}")
    driver.quit()
    exit()

driver.get("https://www.wordsearchlabs.com")



###################################### File name & words list ####################################
filename = files_list[-2]

# Dynamically find whether the text file matches the exact case
words_file_path = files_path / f"{filename}.txt"
if not words_file_path.exists():
    words_file_path = files_path / f"{filename}.TXT"

words_list = open(words_file_path).read().splitlines()
print(f"Current File: {filename}")
print(f"Words List: {words_list}")

############################################## Title #############################################
title = WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.ID, "wordsearch-title"))
)
title.send_keys(filename)


############################################## Lines ##############################################
try:
    wslines = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "wordsearch-lines"))
    )
    wslines.clear()
    multiline_text = "\n".join(words_list)
    wslines.send_keys(multiline_text)
    print("multiline_text lines written")

except Exception as e:
    print(f"error in lines: {e}")


############################################# Selecting Checkbox ###################################
checkbox = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located(
        (
            By.XPATH,
            "/html/body/div/div[2]/div/form/div/div/div[1]/div[1]/div[1]/label[5]/input",
        )
    )
)


# Check if the checkbox is already selected
try:
    if not checkbox.is_selected():
        print("Checkbox is not selected. Clicking to select.")
        checkbox.click()
    else:
        print("Checkbox is already selected.")

except:
    checkbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "id_direction_4"))
    )
    checkbox.click()

# Verify the state after the action
if checkbox.is_selected():
    print("Checkbox is now selected.")
else:
    print("Checkbox is still not selected (issue occurred).")


############################################# UPLOAD IMAGES ########################################

select = driver.find_element("id", "id_template")
select.send_keys(Keys.ARROW_DOWN)

width = driver.find_element("id", "wordsearch-width")
width.send_keys(Keys.CONTROL, "a")
width.send_keys("40")

height = driver.find_element("id", "wordsearch-height")
height.send_keys(Keys.CONTROL, "a")
height.send_keys("40")

choose_file = WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.ID, "btn-upload"))
)
driver.execute_script("arguments[0].style.display = 'block';", choose_file)

# Find the exact original image extension used
actual_image_path = None
for ext in ['.jpg', '.JPG', '.jpeg', '.JPEG']:
    test_path = files_path / f"{filename}{ext}"
    if test_path.exists():
        actual_image_path = test_path
        break

choose_file.send_keys(str(actual_image_path))

trim = WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.ID, "btn-trim"))
)
trim.click()

invert = driver.find_element("id", "btn-invert")
invert.click()
############################################# Passcode & Save #################################
passcode = driver.find_element(By.ID, "wordsearch-passcode")
passcode.send_keys(filename)
time.sleep(2)

# CRITICAL: We MUST submit the form to get the actual view/image URL
passcode.send_keys(Keys.RETURN)
print("Form submitted. Waiting for page redirection...")
time.sleep(5) 

############################################# Download PDF #####################################
current_url = driver.current_url
print(f"Generated Puzzle URL: {current_url}")


# ----------------------------
# FUNCTION TO SAVE CURRENT PAGE AS PDF
# ----------------------------
def save_page_pdf(filename):
    pdf = driver.execute_cdp_cmd(
        "Page.printToPDF",
        {
            "printBackground": True
        },
    )

    with open(filename, "wb") as f:
        f.write(base64.b64decode(pdf['data']))

    print(f"Saved PDF: {filename}")


# ----------------------------
# OPEN PAGE
# ----------------------------

wait = WebDriverWait(driver, 20)

# Save BEFORE password page
time.sleep(3)
save_page_pdf(f"{filename} puzzle.pdf")


# ----------------------------
# CLICK ANSWERS
# ----------------------------
answers_btn = wait.until(
    EC.element_to_be_clickable(
        (
            By.XPATH,
            "//*[contains(text(),'Answers')]"
        )
    )
)

driver.execute_script("arguments[0].click();", answers_btn)

print("Clicked Answers.")


# ----------------------------
# ENTER PASSWORD
# ----------------------------
password = WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.NAME, "passcode"))
)

password.send_keys(filename)
password.send_keys(Keys.RETURN)

print("Password Done")


# ----------------------------
# CLICK ANSWERS AGAIN
# ----------------------------
answers_btn = wait.until(
    EC.element_to_be_clickable(
        (
            By.XPATH,
            "//*[contains(text(),'Answers')]"
        )
    )
)

driver.execute_script("arguments[0].click();", answers_btn)

print("Clicked Answers Checkbox.")


# Wait for answers page to fully load
time.sleep(5)

# Save AFTER password page
save_page_pdf(f"{filename} Answers.pdf")


input("Press Enter to close...")
driver.quit()

