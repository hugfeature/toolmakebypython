import logging
import time
import random
from appium import webdriver 
from appium.webdriver.appium_service import AppiumService
from appium.options.android.uiautomator2.base import UiAutomator2Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import common_model

common_model.set_global_logger()
logger = logging.getLogger(__name__)

# ---------------------- 单例模式管理 Driver ----------------------
class AppiumDriver:
    _instance = None
    _appium_service = None

    @classmethod
    def get_driver(cls):
        if cls._instance is None:
            # 启动 Appium 服务
            cls._appium_service = AppiumService()
            cls._appium_service.start()
            
            # 初始化配置
            options = UiAutomator2Options()
            # 设备配置（根据你的模拟器调整）
            options.platform_name = 'Android'
            options.platform_version = '16'  # 对应你的设备
            options.device_name = 'emulator-5554'
            
            # 应用配置（Chrome 示例）
            options.app_package = 'com.android.chrome'
            options.app_activity = 'com.google.android.apps.chrome.Main'
            options.no_reset = True
            
            # 关键配置：禁用超时和优化 uiautomator2
            options.new_command_timeout = 0  # 永不超时
            options.uiautomator2_server_launch_timeout = 60000  # 服务启动超时
            options.disable_window_animation = True  # 禁用动画提升稳定性

            # 创建 Driver
            cls._instance = webdriver.webdriver.WebDriver(
                'http://localhost:4723',
                options=options
            )
            logger.info("Appium Driver 初始化成功")
        return cls._instance

    @classmethod
    def quit_driver(cls):
        if cls._instance:
            cls._instance.quit()
            cls._instance = None
            logger.info("Appium Driver 已关闭")
        if cls._appium_service and cls._appium_service.is_running:
            cls._appium_service.stop()
            logger.info("Appium 服务已停止")

# ---------------------- 搜索逻辑优化 ----------------------
def search_bing(driver, keyword):
    try:
        # 使用显式等待替代固定 sleep
        wait = WebDriverWait(driver, 30)
        
        # 等待搜索框就绪并操作
        search_box = wait.until(
            EC.element_to_be_clickable((By.ID, 'com.android.chrome:id/url_bar'))
        )
        search_box.click()
        
        # 输入关键词（模拟人类输入速度）
        search_box.clear()
        search_box.send_keys(keyword)
        # for char in keyword:
        #     search_box.send_keys(char)
        #     time.sleep(random.uniform(0.1, 0.3))  # 随机输入间隔
            
        # 等待搜索建议并点击
        search_suggestion = wait.until(
            EC.element_to_be_clickable((By.ID, 'com.android.chrome:id/line_1')))
        search_suggestion.click()
        
        # 验证搜索结果（根据页面特征调整）
        wait.until(
            EC.presence_of_element_located((By.XPATH, '//android.webkit.WebView'))
        )
        logger.debug("搜索结果页加载完成")
        
        # 随机滚动模拟浏览
        # for _ in range(random.randint(1, 3)):
        #     driver.swipe(500, 1500, 500, 500, 400)
        #     time.sleep(random.uniform(1.5, 3.0))
            
    except Exception as e:
        logger.error(f"搜索操作失败: {str(e)}", exc_info=True)
        raise  # 抛出异常由上层处理

# ---------------------- 主程序逻辑 ----------------------
def main():
    search_count = 0
    search_num = 260
    driver = None
    
    try:
        driver = AppiumDriver.get_driver()
        
        while search_count < search_num:
            keyword = common_model.generate_hot_keyword()
            logger.info(f"开始第 {search_count+1} 次搜索，关键词：{keyword}")
            
            try:
                search_bing(driver, keyword)
                search_count += 1
                
                # 随机等待（更自然的行为模式）
                sleep_time = random.randint(10, 35)
                logger.info(f"等待 {sleep_time} 秒后继续...")
                time.sleep(sleep_time)
                # 每4次搜索后暂停半小时
                # if search_count % 4 == 0:
                #     logger.info(f"----------已搜索{search_count}次，暂停{sleep_time}分钟...----------")
                #     if search_count != search_num:
                #         time.sleep(sleep_time * 60)  # 暂停时间，*60为分钟
            except Exception:
                logger.warning("单次搜索失败，尝试恢复...")
                # 可选：重启 Driver 的逻辑
                # AppiumDriver.quit_driver()
                # driver = AppiumDriver.get_driver()
                
        logger.info(f"已完成全部 {search_num} 次搜索")

    except Exception as e:
        logger.error(f"主流程异常: {str(e)}", exc_info=True)
    finally:
        AppiumDriver.quit_driver()

if __name__ == "__main__":
    main()
    