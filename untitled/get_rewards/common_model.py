import requests
from bs4 import BeautifulSoup
import random
import time
import logging


def set_global_logger():
    logging.basicConfig(
    level=logging.INFO,  # 设置日志级别
    format="%(asctime)s - %(levelname)s - %(message)s",  # 设置日志格式
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        # logging.FileHandler("rewards_log.log", mode="a", encoding="utf-8")  # 输出到文件
    ]
)

# 微博热搜 URL
weibo_hot_search_url = "https://s.weibo.com/top/summary"

# 获取微博热搜关键词的函数
def get_weibo_hot_search():
    headers = {
        'cookie':'SCF=AgaMCkQXUCT-f63_vca3bpBva475CErZCCUAPYuWuRwCSWIFSNn8GDTJWfvcVn7kG0JdnDsPPVRZmmfv5BL8EJ0.; _s_tentry=-; Apache=4373995994157.378.1730774845601; SINAGLOBAL=4373995994157.378.1730774845601; ULV=1730774845916:1:1:1:4373995994157.378.1730774845601:; SUB=_2AkMQdQi8f8NxqwFRmf4UzGLkboR1zA_EieKmKflnJRMxHRl-yT8XqmAJtRB6O_UmUw83HzTvGFbiRtcpmMtncaGp3zI3; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFf5uuiq86jsE7.iIRmKre2'
    }
    response = requests.get(weibo_hot_search_url, headers=headers)
    
    # 检查请求是否成功
    if response.status_code != 200:
        print("无法获取微博热搜。请稍后再试。")
        return []
    
    # 解析网页内容
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(soup)
    # 查找热搜关键词
    hot_searches = []
    for item in soup.select(".td-02 a"):
        hot_searches.append(item.get_text())
    
    return hot_searches

# 随机选择一个热搜关键词的函数
def generate_hot_keyword():
    hot_searches = get_weibo_hot_search()
    
    # 检查是否获取到热搜关键词
    if not hot_searches:
        return "无法获取热搜"
    
    # 随机选择一个热搜关键词
    hot_keyword = random.choice(hot_searches)
    return hot_keyword

# 获取今日积分
def get_today_reward(driver):
     # 直接访问微软积分页面（假设用户已经登录过并保存了会话）
    driver.get("https://rewards.microsoft.com")
    time.sleep(10)

