import logging
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException, 
                                      NoSuchElementException,
                                      WebDriverException)
import common_model

common_model.set_global_logger()
logger = logging.getLogger(__name__)

class StealthBrowser:
    """防检测浏览器控制器"""
    def __init__(self):
        self.driver = None
        self.edge_driver_path = "D:\\webdriver\\msedgedriver.exe"
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.62",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.62"
        ]
        
    def _get_stealth_options(self):
        """生成反检测浏览器配置"""
        options = Options()
        # 基础隐身配置
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-popup-blocking")
        options.add_argument(f"user-agent={random.choice(self.user_agents)}")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)
        return options

    # def _clear_automation_flags(self):
    #     """清除自动化特征 (CDP命令)"""
    #     self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #         "source": """
    #             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    #             window.chrome = {runtime: {}};
    #             delete navigator.cookieEnabled;
    #         """
    #     })

    def start(self):
        """启动浏览器实例"""
        try:
            service = Service(self.edge_driver_path)
            options = self._get_stealth_options()
            self.driver = webdriver.Edge(service=service, options=options)
            # self._clear_automation_flags()
            self.driver.maximize_window()
            return self.driver
        except WebDriverException as e:
            logger.critical(f"浏览器启动失败: {str(e)}")
            raise

class BingSearchBot:
    """Bing搜索机器人"""
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout=15, poll_frequency=2)

    def _human_typing(self, element, text):
        """模拟人类输入速度"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))

    def _random_delay(self, min_sec=5, max_sec=15):
        """随机等待时间"""
        delay = random.randint(min_sec, max_sec)
        logger.debug(f"随机等待 {delay} 秒")
        time.sleep(delay)

    def perform_search(self, keyword):
        """执行单次搜索"""
        try:
            # 访问Bing
            self.driver.get("https://cn.bing.com")
            
            # 等待搜索框加载
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "q")))
            
            # 输入关键词
            self._human_typing(search_box, keyword)
            search_box.send_keys(keyword.RETURN)
            
            # 验证搜索结果
            self.wait.until(
                EC.presence_of_element_located((By.ID, "b_results")))
            self._random_delay(8, 20)
            
            # 模拟滚动浏览
            for _ in range(random.randint(2, 4)):
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1.5, 3.5))
            
            return True
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"搜索失败: {str(e)}")
            return False

def main():
    max_retries = 3
    search_num = 370
    session_interval = 60 * 30  # 每30分钟重启浏览器
    
    try:
        for session in range(1, (search_num // 10) + 2):
            browser = StealthBrowser()
            driver = browser.start()
            bot = BingSearchBot(driver)
            
            for count in range(1, 11):
                if session * 10 + count > search_num:
                    break
                
                keyword = common_model.generate_hot_keyword()
                success = False
                retry = 0
                
                while not success and retry < max_retries:
                    success = bot.perform_search(keyword)
                    if success:
                        logger.info(f"成功第 {session*10 + count} 次搜索: {keyword}")
                        break
                    retry += 1
                    logger.warning(f"第{retry}次重试...")
                    
                if not success:
                    logger.error(f"关键词 {keyword} 搜索失败超过最大重试次数")
                
                # 每10次搜索后长暂停
                if count % 10 == 0:
                    logger.info(f"已完成 {count} 次搜索，休息5分钟")
                    time.sleep(300)
                    
            # 定期重启浏览器清理痕迹
            driver.quit()
            logger.info(f"会话 {session} 结束，等待30分钟")
            time.sleep(session_interval)
            
    except Exception as e:
        logger.error(f"主流程异常: {str(e)}", exc_info=True)
    finally:
        if 'driver' in locals() and driver.service.process:
            driver.quit()
        logger.info("所有任务执行完毕")

if __name__ == "__main__":
    main()