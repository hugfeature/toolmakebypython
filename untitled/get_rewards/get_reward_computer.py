
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys
import common_model
import requests
from bs4 import BeautifulSoup
import time
import random

common_model.set_global_logger()
logger = logging.getLogger(__name__)


# 设置edge浏览器
def setup_browser():
    # Edge WebDriver 路径 (请根据你的实际情况填写)
    edge_driver_path = "D:\\webdriver\\msedgedriver.exe"

    # Edge 浏览器的选项设置
    edge_options = Options()
    # 窗口最大化
    edge_options.add_argument("start-maximized")
    # 忽略证书错误
    edge_options.add_argument('--ignore-certificate-errors')
    # 忽略 Bluetooth: bluetooth_adapter_winrt.cc:1075 Getting Default Adapter failed. 错误
    edge_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    # 忽略 DevTools listening on ws://127.0.0.1... 提示
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # 启动 Edge 浏览器
    service = Service(edge_driver_path)
    driver = webdriver.Edge(service=service, options=edge_options)
    return driver

# 执行bing搜素任务
def perform_bing_search(driver, keyword):
    # 搜索页面打开空白
    driver.get("http://cn.bing.com")
    time.sleep(10)
    # 在必应搜索框中输入关键词并提交搜索
    search_field = driver.find_element(By.NAME, "q")
    search_field.clear()
    search_field.send_keys(keyword)
    search_field.send_keys(Keys.RETURN)
    # 等待搜索结果加载
    time.sleep(random.randint(4, 20))  # 模拟人类行为，等待随机的时间间隔



# 主程序
def main():
    # 启动浏览器
    driver = setup_browser()
    search_count = 0  # 初始化计数器
    search_num = 36 # 需要搜索的次数
    sleep_time = 15 # 暂停时间，持续搜索会不计分
    try:
        # 获取每日热搜并进行搜索
        while search_count < search_num:  
            hot_keyword = common_model.generate_hot_keyword()
            search_count += 1  # 增加搜索计数
            # 打印搜索进度
            perform_bing_search(driver, hot_keyword)
            logger.info(f"完成搜索 {search_count} 次，搜索词：'{hot_keyword}'")
                             
            # 每4次搜索后暂停半小时
            if search_count % 4 == 0:
                logger.info(f"----------已搜索{search_count}次，暂停{sleep_time}分钟...----------")
                if search_count != search_num:
                    time.sleep(sleep_time * 60)  # 暂停时间，*60为分钟
    except Exception as e:
         logger.error(f"发生异常: {e}", exc_info=True)         
    finally:
        # 关闭浏览器
        if driver:
            driver.quit() 
        logger.info("所有搜索任务完成。")

# 运行主程序
if __name__ == "__main__":
    main()

