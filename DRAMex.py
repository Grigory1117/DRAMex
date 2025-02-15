import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
from datetime import datetime
import locale

# Function to fetch the HTML content from the website
def fetch_website_content(url):
    user_agent = UserAgent().random  # Generate a random User-Agent string to mimic a browser
    response = requests.get(url, headers={"User-Agent": user_agent})
    return response.content

# Function to parse the HTML content and extract the table headers
def extract_table_headers(soup):
    headers = []
    header_row = soup.select('#tb_NationalDramSpotPrice tr')[0]  # Get the first row (header)
    header_cols = header_row.find_all('td')  # Extract each column in the header row
    for header in header_cols:
        headers.append(header.get_text(strip=True))  # Clean and append header text
    return headers

# Function to extract the table data (memory item details)
def extract_dram_data(soup, headers):
    dram_data = []
    rows = soup.select('#tb_NationalDramSpotPrice tr')[1:]  # Skip the header row
    for row in rows:
        cols = row.find_all('td')
        item_data = {
            'Item': cols[0].get_text(strip=True),
            'Daily High': cols[1].get_text(strip=True),
            'Daily Low': cols[2].get_text(strip=True),
            'Session High': cols[3].get_text(strip=True),
            'Session Low': cols[4].get_text(strip=True),
            'Session Average': cols[5].get_text(strip=True),
            'Session Change': cols[6].get_text(strip=True)
        }
        dram_data.append(item_data)
    return dram_data

# Function to format the timestamp for the log filename
def format_timestamp(soup):
    # Extract the "Last Update" time from the page
    time_str = soup.find('span', class_='tab_time').get_text(strip=True)
    time_str = time_str.split('Last Update: ')[1].split(' (GMT+8)')[0].strip()
    
    # Clean up the timestamp string for proper parsing
    time_str = time_str.replace("    ", " ").replace('.', ' ')
    
    # Convert the cleaned time string into a datetime object
    time_obj = datetime.strptime(time_str, '%b %d %Y %H:%M')
    
    # Format the datetime object into a string that can be used in the filename
    return time_obj.strftime('%Y%m%d_%H%M')

# Function to create a folder if it does not exist
def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)  # Create the folder if it doesn't exist
        print(f"Folder '{folder_path}' created successfully.")
    else:
        print(f"Folder '{folder_path}' already exists. Skipping creation.")

# Main function to scrape data, process it, and save it to a CSV file
def main():
    # URL of the website to scrape
    base_url = "https://www.dramexchange.com/"
    
    # Fetch the website content
    html_content = fetch_website_content(base_url)
    
    # Parse the content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Set the locale for datetime formatting (for strptime)
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    
    # Extract table headers and data
    headers = extract_table_headers(soup)
    dram_data = extract_dram_data(soup, headers)
    
    # Convert the data into a pandas DataFrame
    data = pd.DataFrame(dram_data, columns=headers)
    
    # Prepare the folder for saving the log
    folder_path = './DRAMexchange_Log'
    create_folder(folder_path)
    
    # Get the formatted timestamp for the filename
    timestamp = format_timestamp(soup)
    
    # Formulate the CSV file name using the timestamp
    csv_filename = f'{folder_path}/DRAMexchange_{timestamp}.csv'
    
    # Save the DataFrame to the CSV file
    data.to_csv(csv_filename, index=False)
    print(f"Data saved to {csv_filename}")

# Run the main function
if __name__ == "__main__":
    main()
