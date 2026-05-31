from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time, os
import pyautogui
import wget

# Setup Chrome driver
#driver = webdriver.Chrome(executable_path='C:/chromedriver.exe')
driver = webdriver.Chrome()

##Images loading
files_path = r"C:\Users\pc\Desktop\Selenium\countriesfilled\Choosen"
files_list = [i.replace('.jpg', '') for i in os.listdir(files_path)]

driver.get("https://www.wordsearchlabs.com")

###################################### File name & words list ####################################
filename = files_list[0]
words_list = open(filename + '.txt').read().splitlines()
print(words_list)

############################################## Title #############################################
title = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "wordsearch-title")))
title.send_keys(filename)
print(filename)

time.sleep(10)


############################################## Lines ##############################################
try:
	wslines = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID,  "wordsearch-lines")))
	wslines.clear()
	multiline_text = "\n".join(words_list)
	wslines.send_keys(multiline_text)
	print("multiline_text lines written")
	
except:
	#driver.refresh()
	print("error in lines")


############################################# Selecting Checkbox ###################################
checkbox = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,  "/html/body/div/div[2]/div/form/div/div/div[1]/div[1]/div[1]/label[5]/input")))


# Check if the checkbox is already selected
try:
	if not checkbox.is_selected():
		print("Checkbox is not selected. Clicking to select.")
		checkbox.click()
	else:
		print("Checkbox is already selected.")

except:
	checkbox = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID,  "id_direction_4")))
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
width.send_keys(Keys.CONTROL, 'a')
width.send_keys('40')

height = driver.find_element("id", "wordsearch-height")
height.send_keys(Keys.CONTROL, 'a')
height.send_keys('40')

choose_file = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID,  "btn-upload")))
driver.execute_script("arguments[0].style.display = 'block';", choose_file)
choose_file.send_keys(files_path + filename + str('.jpg')) ## This opens the windows file selector

trim = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID,  "btn-trim")))
trim.click()

invert = driver.find_element("id", "btn-invert")
invert.click()

############################################# Create a Passcode  #################################

passcode = driver.find_element(By.ID, "wordsearch-passcode")
passcode.send_keys(filename)
time.sleep(10)

############################################# Save  ###############################################

###passcode.send_keys(Keys.RETURN)

############################################# Save image  #########################################
#https://wordsearchlabs.com/image/1269748.png?size=large

# Get the current URL
###current_url = driver.current_url

# Print the URL
###print(f"The current URL is: {current_url}")

# Get Image URL
#image_final = current_url.replace("view", "image") + ".png?size=large"
#print(image_final)
#driver.get(image_final)
#time.sleep(10)

# Get Image Answer URL
###image_A_final = current_url.replace("view", "image") + ".png?size=large&show_answers"
###print(image_A_final)
###driver.get(image_A_final)
###time.sleep(10)

############################################# Download image  ######################################

#Image 
#wget.download(image_final)

#Image with Answers
###wget.download(image_A_final)

