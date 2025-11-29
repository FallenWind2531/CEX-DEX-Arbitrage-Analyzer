# backend/data_service.py
import os
import time
import requests
import zipfile
import io
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import config

class DataService:
    def __init__(self):
        self.df_merged = None
        # 确保数据目录存在
        if not os.path.exists(config.DATA_DIR):
            os.makedirs(config.DATA_DIR)

    def initialize(self):
        """系统初始化：检查本地是否有数据，没有则下载，最后加载内存"""
        print("检查数据完整性...")
        
        # 1. 检查 Uniswap 数据
        if not os.path.exists(config.UNI_CSV):
            print("未找到 Uniswap 本地数据，开始从 The Graph 抓取...")
            self._fetch_uniswap_data()
        
        # 2. 检查 Binance 数据
        if not os.path.exists(config.BIN_CSV):
            print("未找到 Binance 本地数据，开始从 Binance Vision 下载...")
            self._fetch_binance_data()
            
        # 3. 加载并对齐数据
        self._load_and_merge()

    def _fetch_uniswap_data(self):
        """从 The Graph 抓取全量数据"""
        url = f"https://gateway.thegraph.com/api/{config.THE_GRAPH_API_KEY}/subgraphs/id/{config.UNISWAP_SUBGRAPH_ID}"
        start_ts = int(config.START_DT.timestamp())
        end_ts = int(config.END_DT.timestamp())
        
        query_template = """
        {
          swaps(first: 1000, orderBy: timestamp, orderDirection: asc, where: {pool: "%s", timestamp_gte: %d, timestamp_lt: %d}) {
            id, timestamp, amount0, amount1, transaction { id, blockNumber }
          }
        }
        """
        all_swaps = []
        current_ts = start_ts
        
        while current_ts < end_ts:
            query = query_template % (config.POOL_ADDRESS, current_ts, end_ts)
            try:
                resp = requests.post(url, json={'query': query})
                if resp.status_code != 200:
                    print(f"Graph API Error: {resp.text}")
                    break
                
                data = resp.json().get('data', {}).get('swaps', [])
                if not data:
                    break
                    
                all_swaps.extend(data)
                last_ts = int(data[-1]['timestamp'])
                print(f"   -> 已抓取至: {datetime.fromtimestamp(last_ts, timezone.utc)}")
                
                # 更新游标
                current_ts = last_ts + 1 if last_ts >= current_ts else last_ts
                time.sleep(0.1) # 防限流
                
            except Exception as e:
                print(f"抓取异常: {e}")
                break
        
        # 处理并保存
        if all_swaps:
            df = pd.DataFrame(all_swaps)
            df['tx_hash'] = df['transaction'].apply(lambda x: x['id'])
            df['block_number'] = df['transaction'].apply(lambda x: x['blockNumber'])
            df.drop(columns=['transaction'], inplace=True)
            
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s', utc=True)
            df['amount0'] = df['amount0'].astype(float) # ETH
            df['amount1'] = df['amount1'].astype(float) # USDT
            
            # 计算价格 (USDT / ETH)
            df['price_usdt_eth'] = df.apply(lambda r: abs(r['amount1']/r['amount0']) if r['amount0']!=0 else 0, axis=1)
            
            df = df[['timestamp', 'block_number', 'tx_hash', 'price_usdt_eth', 'amount0', 'amount1']]
            df.to_csv(config.UNI_CSV, index=False)
            print(f"Uniswap 数据已保存: {len(df)} 条")

    def _fetch_binance_data(self):
        """从 Binance Vision 下载 ZIP"""
        url = f"https://data.binance.vision/data/spot/monthly/aggTrades/{config.BINANCE_SYMBOL}/{config.BINANCE_SYMBOL}-aggTrades-{config.BINANCE_YEAR}-{config.BINANCE_MONTH}.zip"
        print(f"   -> 正在下载: {url}")
        
        resp = requests.get(url)
        if resp.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                fname = z.namelist()[0]
                # 读取并处理时间戳
                df = pd.read_csv(z.open(fname), header=None, names=['id','price','qty','f','l','ts','is_maker','best'])
                
                # 自动判断微秒/毫秒
                sample_ts = df['ts'].iloc[0]
                unit = 'us' if sample_ts > 1e14 else 'ms'
                df['datetime'] = pd.to_datetime(df['ts'], unit=unit, utc=True)
                
                df = df[['datetime', 'price']].sort_values('datetime')
                df.to_csv(config.BIN_CSV, index=False)
                print(f"Binance 数据已保存: {len(df)} 条")
        else:
            print(f"下载失败 HTTP {resp.status_code}")

    def _load_and_merge(self):
        """加载 CSV 并执行 Merge AsOf"""
        print("正在加载并对齐数据...")
        try:
            # 使用 format='mixed' 解决时间戳格式不一致问题
            df_uni = pd.read_csv(config.UNI_CSV)
            df_uni['timestamp'] = pd.to_datetime(df_uni['timestamp'], format='mixed', utc=True)
            df_uni.sort_values('timestamp', inplace=True)
            # 过滤异常价格
            df_uni = df_uni[(df_uni['price_usdt_eth'] > 1000) & (df_uni['price_usdt_eth'] < 10000)]

            df_bin = pd.read_csv(config.BIN_CSV)
            df_bin['datetime'] = pd.to_datetime(df_bin['datetime'], format='mixed', utc=True)
            df_bin.sort_values('datetime', inplace=True)

            # 核心对齐：Uniswap 时间点回头看 Binance 价格
            self.df_merged = pd.merge_asof(
                df_uni, df_bin,
                left_on='timestamp', right_on='datetime',
                direction='backward', suffixes=('_uni', '_bin')
            )
            
            # 预计算价差 (Binance - Uniswap)
            # spread > 0: Binance 贵 (DEX->CEX)
            # spread < 0: Uniswap 贵 (CEX->DEX)
            self.df_merged['spread_val'] = self.df_merged['price'] - self.df_merged['price_usdt_eth']
            self.df_merged['spread_pct'] = (self.df_merged['spread_val'] / self.df_merged['price']) * 100
            
            self.df_merged.dropna(subset=['price', 'price_usdt_eth'], inplace=True)
            print(f"数据准备就绪, 有效记录: {len(self.df_merged)}")
            
        except Exception as e:
            print(f"数据加载失败: {e}")
            raise e

    def get_chart_data(self, timeframe='1H'):
        """图表数据重采样"""
        if self.df_merged is None: return []
        
        df = self.df_merged.set_index('timestamp')
        resampled = df[['price_usdt_eth', 'price', 'spread_pct']].resample(timeframe).mean().reset_index()
        resampled['timestamp'] = resampled['timestamp'].apply(lambda x: x.isoformat() if pd.notnull(x) else "")
        return resampled.fillna(0).to_dict(orient='records')

    def analyze_opportunities(self, threshold_pct, capital):
        """非原子套利识别算法"""
        if self.df_merged is None: return []

        # 1. 初筛
        mask = self.df_merged['spread_pct'].abs() >= threshold_pct
        df_ops = self.df_merged[mask].copy()
        
        if df_ops.empty: return []

        # 2. 真实成本计算函数
        def calc_logic(row):
            eth_price = row['price_usdt_eth'] # 当前 ETH 价格
            spread_pct = row['spread_pct']
            
            # 成本结构
            # A. 交易所手续费
            cost_cex = capital * config.CEX_TAKER_FEE
            # B. 链上 Gas (ETH -> USDT)
            cost_gas = config.DEFAULT_GAS_LIMIT * (config.DEFAULT_GAS_PRICE * 1e-9) * eth_price
            # C. 提币费
            cost_total = cost_cex + cost_gas + config.FIXED_TRANSFER_FEE
            
            # 利润计算
            # 假设全额投入，买入量 = 本金 / 买入价
            if spread_pct > 0:
                # 正溢价 (Binance贵): Uni买 -> Bin卖
                direction = "DEX_TO_CEX"
                buy_price = row['price_usdt_eth']
                sell_price = row['price']
            else:
                # 负溢价 (Uni贵): Bin买 -> Uni卖
                direction = "CEX_TO_DEX"
                buy_price = row['price']
                sell_price = row['price_usdt_eth']
            
            gross_profit = (capital / buy_price) * (sell_price - buy_price)
            net_profit = gross_profit - cost_total
            
            return pd.Series([gross_profit, net_profit, cost_gas, direction])

        # 3. 应用计算
        cols = df_ops.apply(calc_logic, axis=1)
        cols.columns = ['gross_profit', 'estimated_profit', 'cost_gas', 'direction']
        df_final = pd.concat([df_ops, cols], axis=1)
        
        # 4. 只保留净利润 > 0 并排序
        df_final = df_final[df_final['estimated_profit'] > 0]
        df_final.sort_values('estimated_profit', ascending=False, inplace=True)
        
        # 5. 格式化
        df_final['timestamp'] = df_final['timestamp'].apply(lambda x: x.isoformat())
        
        # 返回前 100 条
        return df_final.to_dict(orient='records')

# 单例
service = DataService()