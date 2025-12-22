# backend/config.py
from datetime import datetime, timezone
import os

DATA_DIR = "./data"

# BigQuery 导出的 Uniswap Logs 
UNI_LOGS_JSON = f"{DATA_DIR}/uniswap_logs_2025_09.json"

# 分片后的 Binance Trades CSV 目录
BINANCE_TRADES_DIR = f"{DATA_DIR}/split_trades"

# BigQuery 导出的 Gas 费 CSV
GAS_FEE_CSV = f"{DATA_DIR}/eth_gas_fees_2025_09.csv"

# 处理后的中间缓存文件 (用于加速后续启动)
PROCESSED_DATA_PKL = f"{DATA_DIR}/processed_algo_b_data.pkl"


# 冲击系数 
# 含义：每增加 1 ETH 交易量，且在 1 单位波动率下，滑点增加的比例
# 这是一个经验值，用于模拟 Binance 在没有订单簿数据时的滑点
ALGO_IMPACT_FACTOR = 0.0002 

# 模拟交易的 ETH 数量列表
SIMULATION_AMOUNTS = [0.1, 1.0, 5.0, 10.0, 20.0, 50.0, 100.0]

# 费率常量
CEX_TAKER_FEE = 0.001       # 0.1% Binance Taker Fee
DEX_FEE_TIER = 0.0005       # 0.05% Uniswap Pool Fee

# 链上交互成本
GAS_LIMIT_SWAP = 160000     # Uniswap V3 Swap Gas Estimate (约 16万 Gas)
FIXED_TRANSFER_COST = 5.0   # 5 USDT 跨交易所提币/归集磨损费 (固定门槛)

# 代币精度
DECIMALS_TOKEN0 = 6  # USDT
DECIMALS_TOKEN1 = 18 # WETH