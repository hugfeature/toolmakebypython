from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys
import time
import random

# Edge WebDriver 路径 (请根据你的实际情况填写)
edge_driver_path = "D:\\webdriver\\msedgedriver.exe"

# Edge 浏览器的选项设置
edge_options = Options()
edge_options.add_argument("start-maximized")

# 启动 Edge 浏览器
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service, options=edge_options)

# 访问微软登录页面
# driver.get("https://login.live.com")

# 等待页面加载
# time.sleep(2)

# 输入微软账号信息
# email_field = driver.find_element(By.NAME, "loginfmt")
# email_field.send_keys("your_email@example.com")  # 替换为你的微软账号
# email_field.send_keys(Keys.RETURN)

# 等待下一步页面加载
# time.sleep(2)

# 输入密码
# password_field = driver.find_element(By.NAME, "passwd")
# password_field.send_keys("your_password")  # 替换为你的密码
# password_field.send_keys(Keys.RETURN)

# 如果启用了两步验证，这里可以模拟更多的验证操作

# 登录成功后，访问积分页面
driver.get("https://rewards.microsoft.com")
# 等待页面加载
time.sleep(5)
# driver.close()
# 打开必应首页
driver.get("https://www.bing.com")
time.sleep(3)

# 关键词库定义
adjectives = ["amazing", "incredible", "wonderful", "spectacular", "fantastic"]
nouns = ["technology", "science", "adventure", "discovery", "exploration"]
verbs = ["learn", "explore", "understand", "study", "imagine"]
topics = ["space", "AI", "quantum computing", "future", "biology"]

# 生成随机关键词的函数
def generate_random_keyword():
    # 从每个词库中随机选择一个单词
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    verb = random.choice(verbs)
    topic = random.choice(topics)
    
    # 随机选择生成方式
    keyword_patterns = [
        f"{verb} {adjective} {noun}",
        f"{adjective} {noun} about {topic}",
        f"{verb} the {adjective} world of {topic}",
        f"{topic} and {noun} study",
    ]
    
    # 返回一个随机生成的关键词
    return random.choice(keyword_patterns)

# 执行搜索任务的循环次数
search_count = 31  # 设定想要进行的搜索次数

# 循环执行搜索任务
for i in range(search_count):
    # 生成一个随机关键词
    search_term = generate_random_keyword()
    
    # 在必应搜索框中输入关键词并提交搜索
    search_field = driver.find_element(By.NAME, "q")
    search_field.clear()
    search_field.send_keys(search_term)
    search_field.send_keys(Keys.RETURN)

    # 等待搜索结果加载
    time.sleep(random.randint(3, 6))  # 模拟人类行为，等待随机的时间间隔

    # 打印搜索进度
    print(f"Completed search {i + 1} for '{search_term}'")

    # 返回必应首页准备下一次搜索
    driver.get("https://www.bing.com")

# 关闭浏览器
driver.quit()
