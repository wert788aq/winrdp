import os
import time
import base64
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

# =========================================
# SETTINGS
# =========================================

# How many files to process
START_INDEX = 0
END_INDEX = None   # change for testing (5, 30, 100, etc.)

# Images/Text folder
files_path = Path(".")

# Output folders
PUZZLES_DIR = Path("Puzzles")
ANSWERS_DIR = Path("Answers")

PUZZLES_DIR.mkdir(exist_ok=True)
ANSWERS_DIR.mkdir(exist_ok=True)

# =========================================
# CHROME SETUP (Cloud Headless Mode)
# =========================================

chrome_options = Options()

# Essential flags for running inside a Linux Docker container
chrome_options.add_argument("--headless=new") 
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")

prefs = {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.password_manager_leak_detection": False
}

chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20)

# =========================================
# LOAD FILES
# =========================================

files_list = []

for f in files_path.iterdir():
    if f.suffix.lower() in ['.jpg', '.jpeg']:
        files_list.append(f.stem)

files_list = sorted(list(set(files_list)))

print(f"Total files found: {len(files_list)}")

if not files_list:
    print("No image files found.")
    driver.quit()
    exit()

# Apply iteration range
files_list = files_list[START_INDEX:END_INDEX]

print(f"Processing {len(files_list)} files...")
print(files_list)

# =========================================
# PDF SAVE FUNCTION
# =========================================

def save_page_pdf(filepath):
    pdf = driver.execute_cdp_cmd(
        "Page.printToPDF",
        {
            "printBackground": True
        }
    )

    with open(filepath, "wb") as f:
        f.write(base64.b64decode(pdf['data']))

    print(f"Saved: {filepath}")

# =========================================
# MAIN LOOP
# =========================================

print(files_list)

for filename in files_list:

    try:
        # Define output target file locations
        puzzle_pdf = PUZZLES_DIR / f"{filename} Puzzle.pdf"
        answers_pdf = ANSWERS_DIR / f"{filename} Answers.pdf"

        # Check if both files exist before spinning up the browser workflow
        if puzzle_pdf.exists() and answers_pdf.exists():
            print(f"\n⏭️ Skipping {filename} - Both Puzzle and Answers PDFs already exist.")
            continue
        elif puzzle_pdf.exists() or answers_pdf.exists():
            print(f"\n⚠️ Re-running {filename} - One or more output files were missing.")

        print("\n" + "="*60)
        print(f"CURRENT FILE: {filename}")
        print("="*60)

        driver.get("https://www.wordsearchlabs.com")

        # =========================================
        # LOAD WORDS FILE
        # =========================================

        words_file_path = files_path / f"{filename}.txt"

        if not words_file_path.exists():
            words_file_path = files_path / f"{filename}.TXT"

        if not words_file_path.exists():
            print("TXT file not found. Skipping...")
            continue

        words_list = open(words_file_path, encoding="utf-8").read().splitlines()

        # =========================================
        # TITLE
        # =========================================

        title = wait.until(
            EC.presence_of_element_located((By.ID, "wordsearch-title"))
        )

        title.send_keys(filename)

        # =========================================
        # WORDS
        # =========================================

        wslines = wait.until(
            EC.presence_of_element_located((By.ID, "wordsearch-lines"))
        )
        
        wslines.clear()
        multiline_text = "\n".join(words_list)

        wslines.send_keys(multiline_text)

        # =========================================
        # CHECKBOX
        # =========================================
        
        try:

            checkbox = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/div/div[2]/div/form/div/div/div[1]/div[1]/div[1]/label[3]/input",
                    )
                )
            )

            if checkbox.is_selected():
                checkbox.click()

        except:

            try:
                checkbox = wait.until(
                    EC.presence_of_element_located((By.ID, "id_direction_2"))
                )

                if checkbox.is_selected():
                    checkbox.click()

            except:
                print("Checkbox selection failed.")


        # =========================================
        # TEMPLATE
        # =========================================

        select = driver.find_element(By.ID, "id_template")
        select.send_keys(Keys.ARROW_DOWN)

        # =========================================
        # WIDTH / HEIGHT
        # =========================================

        width = driver.find_element(By.ID, "wordsearch-width")
        width.send_keys(Keys.CONTROL, "a")
        width.send_keys("35")

        height = driver.find_element(By.ID, "wordsearch-height")
        height.send_keys(Keys.CONTROL, "a")
        height.send_keys("35")

        # =========================================
        # IMAGE
        # =========================================

        choose_file = wait.until(
            EC.presence_of_element_located((By.ID, "btn-upload"))
        )

        driver.execute_script(
            "arguments[0].style.display = 'block';",
            choose_file
        )

        actual_image_path = None

        for ext in ['.jpg', '.JPG', '.jpeg', '.JPEG']:

            test_path = files_path / f"{filename}{ext}"

            if test_path.exists():
                actual_image_path = test_path
                break

        if not actual_image_path:
            print("Image not found. Skipping...")
            continue

        choose_file.send_keys(str(actual_image_path.resolve()))

        trim = wait.until(
            EC.presence_of_element_located((By.ID, "btn-trim"))
        )

        trim.click()

        time.sleep(1)

        try:
            invert = driver.find_element(By.ID, "btn-invert")
            invert.click()
        except:
            pass

        # =========================================
        # PASSCODE
        # =========================================

        passcode = driver.find_element(By.ID, "wordsearch-passcode")

        passcode.send_keys(filename)

        time.sleep(1)

        passcode.send_keys(Keys.RETURN)

        print("Puzzle generated.")

        time.sleep(5)

        # =========================================
        # SAVE PUZZLE PDF
        # =========================================

        save_page_pdf(puzzle_pdf)

        # =========================================
        # OPEN ANSWERS PAGE PROPERLY
        # =========================================

        answers_btn = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//*[contains(text(),'Answers')]"
                )
            )
        )

        driver.execute_script("arguments[0].click();", answers_btn)

        print("Clicked Answers button.")

        time.sleep(2)

        # =========================================
        # PASSWORD PAGE (OPTIONAL)
        # =========================================

        try:

            password = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "passcode"))
            )

            password.clear()
            password.send_keys(filename)
            password.send_keys(Keys.RETURN)

            print("Password entered.")

            time.sleep(3)

        except TimeoutException:

            print("No password page detected.")

        # =========================================
        # VERY IMPORTANT:
        # ACTUALLY ENABLE ANSWERS CHECKBOX
        # =========================================

        try:

            # wait until answers checkbox/toggle exists
            answers_toggle = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//input[contains(@type,'checkbox')]"
                    )
                )
            )

            # enable it if not enabled
            if not answers_toggle.is_selected():
                driver.execute_script(
                    "arguments[0].click();",
                    answers_toggle
                )

            print("Answers checkbox enabled.")

        except Exception as e:

            print("Could not enable answers checkbox.")
            print(e)

        # =========================================
        # WAIT FOR ANSWERS TO RENDER
        # =========================================

        time.sleep(5)

        # =========================================
        # SAVE ANSWERS PDF
        # =========================================

        save_page_pdf(answers_pdf)

        print("Answers PDF saved.")

        print(f"DONE: {filename}")

    except Exception as e:

        print(f"ERROR processing {filename}")
        print(e)

        continue

# =========================================
# FINISHED
# =========================================

print("\nALL DONE")

input("Press Enter to close...")

driver.quit()