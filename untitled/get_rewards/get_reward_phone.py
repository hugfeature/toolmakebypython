import logging
import time
import random
from appium import webdriver 
from appium.webdriver.appium_service import AppiumService
from appium.options.android.uiautomator2.base import UiAutomator2Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from appium.webdriver.webdriver import WebDriver as Remote
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import requests

import common_model

common_model.set_global_logger()
logger = logging.getLogger(__name__)

# 启动 Appium 服务
def start_appium_service():
    appium_service = AppiumService()
    appium_service.start()
    return appium_service

# 启动 Appium driver
def start_driver():
    options = UiAutomator2Options()
    # 雷电模拟器
    # options.platform_name = 'Android'
    # options.platform_version = '9'
    # options.device_name = 'emulator-5554'
    # mumu 模拟器
    # options.platform_name = 'Android'
    # options.platform_version = '12'
    # options.device_name = '127.0.0.1:16384' 
    # google 模拟器
    options.platform_name = 'Android'
    options.platform_version = '16'
    options.device_name = 'emulator-5554' 
    # bing
    # options.app_package = 'com.microsoft.bing'
    # options.app_activity = 'com.microsoft.sapphire.app.main.SapphireMainActivity'
    # options.app_activity ="com.microsoft.sapphire.app.search.autosuggest.activity.AutoSuggestNativeActivity"
    # chrome
    options.app_package = 'com.android.chrome'
    options.app_activity = 'com.google.android.apps.chrome.Main'
    # edge浏览器
    # options.app_package = ''
    # options.app_activity = ''
    options.no_reset = True
    driver = webdriver.webdriver.WebDriver('http://localhost:4723', options=options)
    return driver

# 在 Bing 中搜索
def search_bing(driver, keyword):
    # 等待浏览打开
    time.sleep(20)
    # edge浏览器
    # search_box = driver.find_element(By.ID,'sb_form_q')
    # Chrome浏览器 
    # 使用的是网页头部的搜索框
    search_box = driver.find_element(By.ID,'com.android.chrome:id/url_bar')
    search_box.click()  # 点击搜索框
    time.sleep(3)
    search_box.send_keys(keyword)  # 输入关键词
    time.sleep(5)
    # Chrome浏览器
    search_button = driver.find_element(By.ID,'com.android.chrome:id/line_1') # 关联的第一个搜索
    # search_button = driver.find_element(By.XPATH,'//androidx.recyclerview.widget.RecyclerView[@resource-id="com.microsoft.bing:id/sapphire_search_list"]/android.view.ViewGroup')
    # search_button = driver.find_element(By.ID, 'sb_form')
    search_button.click()  # 提交搜索
    time.sleep(random.randint(4, 20)) # 模拟人类行为，等待随机时间

# 主程序逻辑
def main():
    search_count = 0  # 初始化计数器
    search_num = 24 # 需要搜索的次数
    time_sleep = 15 # 暂停时间
    try:
        # 启动 Appium 服务
        appium_service = start_appium_service()

        # 启动 Appium Driver
        driver = start_driver()
        while search_count < search_num:
            keyword = common_model.generate_hot_keyword()  # 随机选一个热搜词
            search_bing(driver, keyword)
            search_count += 1
            logger.info(f"完成搜索 {search_count} 次,搜索的关键字：{keyword}")
            # 每3次搜索，暂停15分钟  搜索过快会不增加积分，根据实际调整
            if search_count % 3 == 0:
                driver.quit()  # 退出
                logging.info(f"已搜索{search_count}次，暂停{time_sleep}分钟...")
                if search_count != search_num:
                    time.sleep(time_sleep * 60)  # 暂停时间，*60为分钟
                    driver = start_driver()
                    logging.info("启动appiumdriver")
    except Exception as e:
        logger.error(f"发生异常: {e}", exc_info=True)
    finally:
            if driver:
                driver.quit() # driver退出
            if appium_service:
                appium_service.stop()# 停止 Appium 服务
            logger.info("所有搜索任务完成，退出程序")

if __name__ == "__main__":
    main()
