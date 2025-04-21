"""
彩票预测模型优化版 v1.2
功能：包含特征工程、混合模型训练、结果评估
"""
#%% 环境配置
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 屏蔽TensorFlow信息级日志
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from keras.api.models import Sequential, load_model
from keras.api.layers import LSTM, GRU, Dense, Dropout, Conv1D, MaxPooling1D, Reshape
from keras.api.callbacks import EarlyStopping, ModelCheckpoint
from keras.api.optimizers import Adam
import matplotlib.pyplot as plt
import logging
from typing import Tuple, Dict

# 配置参数
class Config:
    # 数据参数
    LOOK_BACK = 5            # 历史窗口大小
    MAIN_RANGE = (1, 35)     # 主号码范围
    SPECIAL_RANGE = (1, 12)  # 特殊号码范围
    
    # 模型参数
    BATCH_SIZE = 64
    EPOCHS = 200
    VAL_SPLIT = 0.1
    MODEL_TYPE = 'hybrid'    # 可选：lstm/gru/hybrid
    
    # 路径设置
    MODEL_PATH = 'best_model.keras'
    LOG_PATH = 'training.log'

# 初始化日志
logging.basicConfig(filename=Config.LOG_PATH, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

#%% 数据预处理模块
def load_and_preprocess(file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """加载数据并生成时序特征"""
    try:
        df = pd.read_csv(file_path, parse_dates=['draw_date'])
        logging.info(f"成功加载数据，共 {len(df)} 条记录")
    except Exception as e:
        logging.error(f"数据加载失败: {str(e)}")
        raise

    # 生成基础特征
    df['year'] = df['draw_date'].dt.year
    df['month'] = df['draw_date'].dt.month
    df['day'] = df['draw_date'].dt.day
    df['dayofweek'] = df['draw_date'].dt.dayofweek  # 周一=0, 周日=6
    
    # 生成统计特征
    main_cols = [f'main_{i}' for i in range(1,6)]
    special_cols = [f'special_{i}' for i in range(1,3)]
    
    df['main_mean'] = df[main_cols].mean(axis=1)
    df['main_std'] = df[main_cols].std(axis=1)
    df['special_diff'] = df['special_1'] - df['special_2']
    
    # 生成滞后特征（向量化操作提升效率）
    for lag in range(1, Config.LOOK_BACK+1):
        df[[f'{col}_lag_{lag}' for col in main_cols]] = df[main_cols].shift(lag)
        df[[f'{col}_lag_{lag}' for col in special_cols]] = df[special_cols].shift(lag)
    
    # 删除包含NaN的行
    df_clean = df.dropna().reset_index(drop=True)
    
    # 数据标准化
    feature_cols = list(set(df_clean.columns) - set(['draw_date'] + main_cols + special_cols))
    scaler = StandardScaler()
    df_clean[feature_cols] = scaler.fit_transform(df_clean[feature_cols])
    
    return df_clean[feature_cols], df_clean[main_cols + special_cols], scaler

#%% 模型构建模块
def build_model(input_shape: Tuple[int, int], output_dim: int) -> Sequential:
    """构建混合模型架构（CNN + LSTM）"""
    model = Sequential([
        Reshape((input_shape[0], input_shape[1], 1)),  # 添加通道维度
        Conv1D(32, 3, activation='relu', padding='same'),
        MaxPooling1D(2),
        LSTM(64, return_sequences=True),
        LSTM(32),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(output_dim, activation='linear')
    ])
    
    optimizer = Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='mse')
    return model

#%% 训练模块
def train_model(X: np.ndarray, y: np.ndarray) -> tf.keras.Model:
    """模型训练流程"""
    # 时序交叉验证
    tscv = TimeSeriesSplit(n_splits=5)
    
    # 回调函数
    callbacks = [
        EarlyStopping(patience=15, restore_best_weights=True),
        ModelCheckpoint(Config.MODEL_PATH, save_best_only=True),
        tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5)
    ]
    
    # 数据reshape
    X_reshaped = X.reshape((X.shape[0], 1, X.shape[1]))
    
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        logging.info(f"正在训练第 {fold+1} 折交叉验证...")
        X_train, X_val = X_reshaped[train_idx], X_reshaped[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        
        model = build_model((1, X.shape[1]), y.shape[1])
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=Config.EPOCHS,
            batch_size=Config.BATCH_SIZE,
            callbacks=callbacks,
            verbose='2'
        )
        
        # 保存训练曲线图
        plot_training_history(history, fold+1)
    
    return load_model(Config.MODEL_PATH)

#%% 后处理模块
def postprocess_predictions(predictions: np.ndarray) -> pd.DataFrame:
    """将预测结果转换为合规格式"""
    main_pred = predictions[:, :5]
    special_pred = predictions[:, 5:]
    
    # 限制取值范围并取整
    main_pred = np.clip(np.round(main_pred), Config.MAIN_RANGE[0], Config.MAIN_RANGE[1]).astype(int)
    special_pred = np.clip(np.round(special_pred), Config.SPECIAL_RANGE[0], Config.SPECIAL_RANGE[1]).astype(int)
    
    # 格式化为DataFrame
    results = []
    for i in range(len(main_pred)):
        main_nums = sorted(main_pred[i])
        special_nums = sorted(special_pred[i])
        results.append({
            'main_1': f"{main_nums[0]:02d}",
            'main_2': f"{main_nums[1]:02d}",
            'main_3': f"{main_nums[2]:02d}",
            'main_4': f"{main_nums[3]:02d}",
            'main_5': f"{main_nums[4]:02d}",
            'special_1': f"{special_nums[0]:02d}",
            'special_2': f"{special_nums[1]:02d}"
        })
    
    return pd.DataFrame(results)

#%% 可视化模块
def plot_training_history(history: tf.keras.callbacks.History, fold: int):
    plt.figure(figsize=(12, 6))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title(f'Training History (Fold {fold})')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend()
    plt.savefig(f'training_history_fold{fold}.png')
    plt.close()

#%% 主程序
if __name__ == "__main__":
    try:
        # 数据预处理
        X, y, scaler = load_and_preprocess('lottery_history.csv')
        logging.info(f"特征维度: {X.shape}, 目标维度: {y.shape}")
        
        # 模型训练
        trained_model = train_model(X.values, y.values)
        
        # 生成预测（使用最后LOOK_BACK期作为输入）
        latest_data = X.iloc[-Config.LOOK_BACK:].values
        latest_data = latest_data.reshape((Config.LOOK_BACK, 1, X.shape[1]))
        predictions = trained_model.predict(latest_data)
        
        # 结果后处理
        pred_df = postprocess_predictions(predictions)
        pred_df.to_csv('optimized_predictions.csv', index=False)
        print("预测结果已保存到 optimized_predictions.csv")
        
        # 评估最后5期的命中率
        true_values = y.iloc[-Config.LOOK_BACK:].values
        evaluate_predictions(true_values, predictions)
        
    except Exception as e:
        logging.error(f"程序运行异常: {str(e)}")
        raise

#%% 评估函数
def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray):
    """模型性能评估"""
    main_true = y_true[:, :5]
    special_true = y_true[:, 5:]
    
    main_pred = np.clip(np.round(y_pred[:, :5]), Config.MAIN_RANGE[0], Config.MAIN_RANGE[1])
    special_pred = np.clip(np.round(y_pred[:, 5:]), Config.SPECIAL_RANGE[0], Config.SPECIAL_RANGE[1])
    
    main_hits = [len(np.intersect1d(true, pred)) for true, pred in zip(main_true, main_pred)]
    special_hits = [len(np.intersect1d(true, pred)) for true, pred in zip(special_true, special_pred)]
    
    print("\n模型评估报告：")
    print(f"主号码平均命中数: {np.mean(main_hits):.2f} (最大值: {max(main_hits)})")
    print(f"特殊号码平均命中数: {np.mean(special_hits):.2f} (最大值: {max(special_hits)})")
    print("注：彩票预测结果仅供参考，请理性购彩！")