import os  # Import os to handle directories
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
import yaml

url = 'https://www.worldaquatics.com/results?year=2024&month=latest&disciplines=SW'

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(url)

# Initialize a list to store the scraped data
data = []

try:
    # Wait for the cookie notice and close it if present
    try:
        cookie_notice = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'cookie-notice__message'))
        )
        close_button = driver.find_element(By.CLASS_NAME, 'cookie-notice__button')
        close_button.click()
    except TimeoutException:
        print("No cookie notice found.")

    # Wait for 5 seconds before starting the scraping
    time.sleep(5)

    # Wait for elements with class name 'competition-item' to be present
    competitions = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'competition-item'))
    )

    for competition in competitions:
        try:
            # Find the name, location, and date of the competition
            name = competition.find_element(By.CLASS_NAME, 'competition-item__name').text if competition.find_element(
                By.CLASS_NAME, 'competition-item__name') else "N/A"
            location = competition.find_element(By.CLASS_NAME,
                                                'competition-item__location').text if competition.find_element(
                By.CLASS_NAME, 'competition-item__location') else "N/A"
            # Extract the date using the correct class and structure
            date_element = competition.find_element(By.CSS_SELECTOR, 'div.competition-item__date.u-hide-tablet')
            date = date_element.text if date_element else "N/A"

            # Append the extracted data to the list
            data.append({'Name': name, 'Location': location, 'Date': date})

        except Exception as e:
            print(f"Error finding competition details: {e}")

except Exception as e:
    print(f"Error finding competitions: {e}")

finally:
    driver.quit()

# Convert the list of data into a pandas DataFrame
df = pd.DataFrame(data)

# Define the folder paths
excel_folder = 'EXCEL_FILES'
yaml_folder = 'YAML_FILES'

# Create directories if they don't exist
os.makedirs(excel_folder, exist_ok=True)
os.makedirs(yaml_folder, exist_ok=True)

# Define file paths
excel_file_path = os.path.join(excel_folder, 'All_Natation_Competitions.xlsx')
yaml_file_path = os.path.join(yaml_folder, 'All_Natation_Competitions.yaml')

# Save the DataFrame to an Excel file
df.to_excel(excel_file_path, index=False)

# Save the list of data to a YAML file
with open(yaml_file_path, 'w') as yaml_file:
    yaml.dump(data, yaml_file, default_flow_style=False, sort_keys=False)

print(f"Data has been saved to '{excel_file_path}' and '{yaml_file_path}'.")
