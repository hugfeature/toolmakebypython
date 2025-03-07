import pandas as pd
import matplotlib.pyplot as plt

# 加载历史数据
df = pd.read_csv('lottery_history.csv')

# 将日期列转换为日期时间格式
df['draw_date'] = pd.to_datetime(df['draw_date'])

# 绘制主号码的走势图
plt.figure(figsize=(12, 6))
for i in range(1, 6):
    plt.plot(df['draw_date'], df[f'main_{i}'], marker='o', linestyle='-', label=f'Main {i}')

plt.title('大乐透历史主号码走势图')
plt.xlabel('日期')
plt.ylabel('号码')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.grid(True)
plt.show()

# 绘制特殊号码的走势图
plt.figure(figsize=(8, 6))
for i in range(1, 3):
    plt.plot(df['draw_date'], df[f'special_{i}'], marker='o', linestyle='-', label=f'Special {i}')

plt.title('大乐透历史特殊号码走势图')
plt.xlabel('日期')
plt.ylabel('号码')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.grid(True)
plt.show()
