import time
import requests
import pandas as pd

def fetch_lottery_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None
def fetch_all_lottery_data(api_url):
    all_data = []
    page = 1
    while True:
        response = requests.get(f"{api_url}?page={page}")
        if response.status_code == 200:
            data = response.json()
            if not data:
                break  # 如果没有更多数据，则退出循环
            all_data.extend(data)
            time.sleep(30)
            page += 1
        else:
            print(f"Failed to retrieve data from page {page}: {response.status_code}")
            break
    return all_data
def fetch_all_pages(api_url, total_pages):
    all_data = []
    for page in range(1, total_pages + 1):
        params = {
            'gameNo': 85,
            'provinceId': 0,
            'pageSize': 30,
            'isVerify': 1,
            'pageNo': page
        }
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'result' in data:
                all_data.extend(data['result'])
            else:
                print(f"No result found in page {page}")
        else:
            print(f"Failed to retrieve data from page {page}: {response.status_code}")
    return all_data
def parse_lottery_data(data):
    parsed_data = []
    for entry in data['value']["list"]:
        draw_date = entry['lotteryDrawTime']
        draw_numbers = entry['lotteryDrawResult']
        parts = draw_numbers.strip().split()
        main_numbers = [parts[:5]]
        special_numbers = [parts[5:]]
        parsed_data.append([draw_date] + main_numbers + special_numbers)
    return parsed_data

def save_to_csv(data, filename):
    columns = ['draw_date', 'main_1', 'main_2', 'main_3', 'main_4', 'main_5', 'special_1', 'special_2']
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    api_url = "http://example.com/api/lottery_results"  # 替换为实际的API URL
    data = fetch_lottery_data(api_url)
    
    if data:
        parsed_data = parse_lottery_data(data)
        save_to_csv(parsed_data, 'lottery_history.csv')
        print("Data has been saved to super_lotto_history.csv")
    else:
        print("No data fetched.")
