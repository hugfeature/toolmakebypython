from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

browser = webdriver.Edge()
browser.get('http://10.141.224.69:31111/user/login')
browser.maximize_window()
time = time.time()
pc_name = str(time) + '.png'
revealed = browser.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[6]/div/div/div[2]/div/div[1]/div/div[1]/div/div")
wait = WebDriverWait(browser, timeout=10)
wait.until(lambda d: revealed.is_displayed())
revealed.screenshot(pc_name)
browser.quit()
