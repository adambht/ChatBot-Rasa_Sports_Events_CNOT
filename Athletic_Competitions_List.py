import os
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

url = 'https://worldathletics.org/competition/calendar-results?'

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(url)

# Initialize a list to store the scraped data
data = []

try:
    # Optional: Close cookie notice if present
    try:
        cookie_notice = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'cookie-notice__message'))
        )
        close_button = driver.find_element(By.CLASS_NAME, 'cookie-notice__button')
        close_button.click()
    except TimeoutException:
        print("No cookie notice found.")

    # Wait for the table to load
    time.sleep(5)

    # Wait for the table elements to be present
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'ResultsTable_resultsTable__JBH1Y'))
    )

    # Find all rows in the table body
    rows = table.find_elements(By.TAG_NAME, 'tr')

    # Iterate through the rows and extract the data
    for row in rows:
        try:
            # Extract data from each cell in the row
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 7:  # Ensure there are enough columns
                date = cells[0].text
                name = cells[1].text
                location = cells[3].text
                country = cells[4].text
                category = cells[5].text
                discipline = cells[6].text
                competition_group = cells[7].text

                # Append the extracted data to the list
                data.append({
                    'Date': date,
                    'Competition_Name': name,
                    'Location': location,
                    'Country': country,
                    'Category': category,
                    'Discipline': discipline,
                    'Competition Group': competition_group
                })

        except Exception as e:
            print(f"Error extracting data from row: {e}")

except Exception as e:
    print(f"Error finding table: {e}")

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
excel_file_path = os.path.join(excel_folder, 'All_Athletic_Competitions.xlsx')
yaml_file_path = os.path.join(yaml_folder, 'All_Athletic_Competitions.yaml')

# Save the DataFrame to an Excel file
df.to_excel(excel_file_path, index=False)

# Save the list of data to a YAML file
with open(yaml_file_path, 'w') as yaml_file:
    yaml.dump(data, yaml_file, default_flow_style=False, sort_keys=False)

print(f"Data has been saved to '{excel_file_path}' and '{yaml_file_path}'.")
