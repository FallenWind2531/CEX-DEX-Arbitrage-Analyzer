# backend/config.py
from datetime import datetime, timezone

# 请在此处填入你在 The Graph Studio 申请的 API Key
THE_GRAPH_API_KEY = "example_key" 

# Uniswap V3 相关
# 修正后的 Subgraph ID (Uniswap V3 Ethereum)
UNISWAP_SUBGRAPH_ID = "5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"
POOL_ADDRESS = "0x11b815efb8f581194ae79006d24e0d814b7697f6" # USDT/WETH 0.05%

# Binance 相关
BINANCE_SYMBOL = "ETHUSDT"
BINANCE_YEAR = "2025"
BINANCE_MONTH = "09"

# 数据时间范围 (UTC)
START_DT = datetime(2025, 9, 1, 0, 0, 0, tzinfo=timezone.utc)
END_DT   = datetime(2025, 10, 1, 0, 0, 0, tzinfo=timezone.utc)

# 本地文件路径
DATA_DIR = "./data"
UNI_CSV = f"{DATA_DIR}/uniswap_v3_{BINANCE_MONTH}_{BINANCE_YEAR}.csv"
BIN_CSV = f"{DATA_DIR}/binance_{BINANCE_SYMBOL.lower()}_{BINANCE_MONTH}_{BINANCE_YEAR}.csv"
MERGED_CSV = f"{DATA_DIR}/merged_arbitrage_data.csv"

# 费率模型默认值
DEFAULT_GAS_LIMIT = 150000  # Uniswap Swap Gas Limit
DEFAULT_GAS_PRICE = 30      # Gwei
CEX_TAKER_FEE = 0.001       # 0.1% Binance Fee
FIXED_TRANSFER_FEE = 5.0    # 5 USDT 提币费