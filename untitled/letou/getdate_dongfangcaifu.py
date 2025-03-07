import time
import requests
from bs4 import BeautifulSoup
import csv

# Base URL of the page to scrape
base_url = "https://caipiao.eastmoney.com/pub/Result/History/dlt?page="

# Function to fetch and parse a page
def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {url}: {e}")
        return None

# Function to extract data from a page
def extract_data(soup):
    data = []
    table = soup.find('table')
    if table is None:
        return data
    for row in table.find_all('tr')[2:]:  # Skip the header row
        columns = row.find_all('td')
        date = columns[1].get_text(strip=True).split('(')[0]
        numbers = columns[3].get_text(strip=True)
        if len(numbers) == 14:
                        main_numbers = numbers[:10]
                        special_numbers = numbers[10:]
                        # Split numbers into individual digits
                        main_numbers_split = [main_numbers[i:i+2] for i in range(0, len(main_numbers), 2)]
                        special_numbers_split = [special_numbers[i:i+2] for i in range(0, len(special_numbers), 2)]
                        data.append([date] + main_numbers_split + special_numbers_split)
                        # print(f'data===== {data}')
    return data

# Open a CSV file to write the results
with open('lottery_history.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(['draw_date', 'main_1', 'main_2', 'main_3', 'main_4', 'main_5', 'special_1', 'special_2'])

    # Fetch and process each page
    page_number = 31
    while True:
        url = base_url + str(page_number)
        print(f'page_number====={page_number}')
        soup = fetch_page(url)
        if soup is None:
              print('最后一页')
              break
        data = extract_data(soup)
        # time.sleep(5)
        if not data:  # Stop if no data is found (no more pages)
            break
        for row in data:
            writer.writerow(row)
        page_number += 1

print("Data has been written to lottery_history.csv")
