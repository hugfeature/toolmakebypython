import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from keras.api.models import Sequential
from keras.api.layers import Dense, LSTM, GRU

# 固定随机种子
RANDOM_STATE = 42

# 加载数据
df = pd.read_csv('lottery_history.csv')

# 转换日期为datetime格式
df['draw_date'] = pd.to_datetime(df['draw_date'])

# 提取年月日等信息作为特征
df['year'] = df['draw_date'].dt.year
df['month'] = df['draw_date'].dt.month
df['day'] = df['draw_date'].dt.day

# 将主号码和特殊号码分开处理
main_numbers = df[['main_1', 'main_2', 'main_3', 'main_4', 'main_5']]
special_numbers = df[['special_1', 'special_2']]

# 生成目标变量
targets = main_numbers.join(special_numbers)

# 构建特征
features = df[['year', 'month', 'day']]

# 添加前几个开奖的号码作为特征
for i in range(1, 6):
    for j in range(1, 6):
        features[f'main_{j}_lag_{i}'] = main_numbers.shift(i)[f'main_{j}']
    for k in range(1, 2):
        features[f'special_{k}_lag_{i}'] = special_numbers.shift(i)[f'special_{k}']

# 丢弃NaN值
features = features.dropna()
targets = targets.loc[features.index]

# 标准化特征
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# 分割数据集
X_train, X_test, y_train, y_test = train_test_split(features_scaled, targets, test_size=0.2, random_state=RANDOM_STATE)

# 将数据转换为LSTM/GRU输入需要的形状
X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

# 创建LSTM模型
def create_lstm_model(output_dim):
    model = Sequential()
    model.add(LSTM(50, input_shape=(1, X_train.shape[2]), activation='relu', return_sequences=True))
    model.add(LSTM(50, activation='relu'))
    model.add(Dense(output_dim, activation='linear'))  # 预测输出值
    model.compile(optimizer='adam', loss='mse')
    return model

# 创建GRU模型
def create_gru_model(output_dim):
    model = Sequential()
    model.add(GRU(50, input_shape=(1, X_train.shape[2]), activation='relu', return_sequences=True))
    model.add(GRU(50, activation='relu'))
    model.add(Dense(output_dim, activation='linear'))  # 预测输出值
    model.compile(optimizer='adam', loss='mse')
    return model

# 创建并训练LSTM模型
lstm_model_main = create_lstm_model(5)  # 主号码有5个数字
lstm_model_main.fit(X_train, y_train[['main_1', 'main_2', 'main_3', 'main_4', 'main_5']], epochs=100, batch_size=32, verbose='1', validation_data=(X_test, y_test[['main_1', 'main_2', 'main_3', 'main_4', 'main_5']]))

lstm_model_special = create_lstm_model(2)  # 特殊号码有2个数字
lstm_model_special.fit(X_train, y_train[['special_1', 'special_2']], epochs=100, batch_size=32, verbose='1', validation_data=(X_test, y_test[['special_1', 'special_2']]))

# 创建并训练GRU模型
gru_model_main = create_gru_model(5)  # 主号码有5个数字
gru_model_main.fit(X_train, y_train[['main_1', 'main_2', 'main_3', 'main_4', 'main_5']], epochs=100, batch_size=32, verbose='1', validation_data=(X_test, y_test[['main_1', 'main_2', 'main_3', 'main_4', 'main_5']]))

gru_model_special = create_gru_model(2)  # 特殊号码有2个数字
gru_model_special.fit(X_train, y_train[['special_1', 'special_2']], epochs=100, batch_size=32, verbose='1', validation_data=(X_test, y_test[['special_1', 'special_2']]))

# 辅助函数：将个位数补0
def format_number(n):
    return f"{n:02d}"

# 预测并记录结果
predictions = []

# LSTM预测
pred_main_lstm = lstm_model_main.predict(X_test)
pred_special_lstm = lstm_model_special.predict(X_test)

# GRU预测
pred_main_gru = gru_model_main.predict(X_test)
pred_special_gru = gru_model_special.predict(X_test)

# 将预测值转换为整数，并限制在有效范围内
pred_main_lstm = np.clip(np.round(pred_main_lstm), 1, 35).astype(int)
pred_special_lstm = np.clip(np.round(pred_special_lstm), 1, 12).astype(int)

pred_main_gru = np.clip(np.round(pred_main_gru), 1, 35).astype(int)
pred_special_gru = np.clip(np.round(pred_special_gru), 1, 12).astype(int)

# 保存LSTM预测结果
for i in range(pred_main_lstm.shape[0]):
    main_combination = [format_number(n) for n in pred_main_lstm[i]]
    special_combination = [format_number(n) for n in pred_special_lstm[i]]
    predictions.append({
        'model': 'LSTM',
        'main_1': main_combination[0],
        'main_2': main_combination[1],
        'main_3': main_combination[2],
        'main_4': main_combination[3],
        'main_5': main_combination[4],
        'special_1': special_combination[0],
        'special_2': special_combination[1]
    })

# 保存GRU预测结果
for i in range(pred_main_gru.shape[0]):
    main_combination = [format_number(n) for n in pred_main_gru[i]]
    special_combination = [format_number(n) for n in pred_special_gru[i]]
    predictions.append({
        'model': 'GRU',
        'main_1': main_combination[0],
        'main_2': main_combination[1],
        'main_3': main_combination[2],
        'main_4': main_combination[3],
        'main_5': main_combination[4],
        'special_1': special_combination[0],
        'special_2': special_combination[1]
    })

# 将结果输出到CSV文件中
predictions_df = pd.DataFrame(predictions)
predictions_df.to_csv('dlt_predictions_nn_lstm_gru.csv', index=False)

print("预测结果已保存到 dlt_predictions_nn_lstm_gru.csv 文件中。")
