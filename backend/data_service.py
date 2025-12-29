# backend/data_service.py
import os
import json
import glob
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import config

class DataService:
    def __init__(self):
        self.df_final = None

    def initialize(self):
        """初始化：优先加载缓存，若无则处理原始数据"""
        # 1. 检查缓存
        if os.path.exists(config.PROCESSED_DATA_PKL):
            print(f" 发现缓存数据: {config.PROCESSED_DATA_PKL}")
            print("   正在快速加载...")
            try:
                self.df_final = pd.read_pickle(config.PROCESSED_DATA_PKL)
                print(f" 数据加载完毕，共 {len(self.df_final)} 个时间切片。")
                return
            except Exception as e:
                print(f" 缓存加载失败 ({e})，将重新处理原始文件...")
        
        # 2. 处理原始数据
        print(" 开始处理原始数据文件 (这可能需要几分钟)...")
        self._process_raw_data()

    def _process_raw_data(self):
        """从原始数据源构建算法B所需的数据集"""
        
        # --- A. 解析 Uniswap Logs ---
        print(f" 正在解析 Uniswap 日志: {config.UNI_LOGS_JSON}")
        if not os.path.exists(config.UNI_LOGS_JSON):
            print(f" 错误: 找不到文件 {config.UNI_LOGS_JSON}")
            return

        uni_data = []
        try:
            with open(config.UNI_LOGS_JSON, 'r') as f:
                first_char = f.read(1)
                f.seek(0)
                if first_char == '[':
                    raw_list = json.load(f)
                    for record in raw_list:
                        parsed = self._decode_uni_log(record)
                        if parsed: uni_data.append(parsed)
                else:
                    for line in f:
                        if not line.strip(): continue
                        try:
                            record = json.loads(line)
                            parsed = self._decode_uni_log(record)
                            if parsed: uni_data.append(parsed)
                        except:
                            continue
        except Exception as e:
            print(f" Uniswap 解析异常: {e}")
            return

        df_uni = pd.DataFrame(uni_data)
        if df_uni.empty:
            print(" Uniswap 数据为空。")
            return

        df_uni['timestamp'] = pd.to_datetime(df_uni['timestamp'], utc=True)
        df_uni.sort_values('timestamp', inplace=True)
        print(f"   -> Uni 解析成功: {len(df_uni)} 条")

        # --- B. 聚合 Binance 数据 ---
        print(f" 正在聚合 Binance CSV 分片... {config.BINANCE_TRADES_DIR}")
        trade_files = glob.glob(os.path.join(config.BINANCE_TRADES_DIR, "*.csv"))
        if not trade_files:
            print(" 错误: 没有找到 Binance CSV 文件。")
            return

        bin_dfs = []
        for idx, file in enumerate(trade_files):
            if idx % 5 == 0:
                print(f"   -> 读取 {os.path.basename(file)}")
            try:
                chunk = pd.read_csv(file)
                if 'time' not in chunk.columns and 'ts' in chunk.columns:
                    chunk.rename(columns={'ts': 'time'}, inplace=True)
                chunk['datetime'] = pd.to_datetime(chunk['time'], unit='us', utc=True)
                chunk['quote_qty'] = chunk['price'] * chunk['qty']
                
                # 1秒聚合
                resampled = chunk.resample('1s', on='datetime').agg({
                    'price': ['mean', 'std'],
                    'qty': 'sum',
                    'quote_qty': 'sum'
                })
                resampled.columns = ['bin_price_close', 'bin_volatility', 'bin_volume', 'bin_quote_vol']
                resampled['bin_vwap'] = resampled['bin_quote_vol'] / resampled['bin_volume']
                bin_dfs.append(resampled)
            except Exception as e:
                print(f"    读取失败 {file}: {e}")

        if not bin_dfs: return

        df_bin = pd.concat(bin_dfs).sort_index()
        
        # -----------------------------------------------------------
        # 1. 价格填充: 使用前值 (ffill)
        # 2. 波动率填充: 
        #    如果 bin_volatility == 0 (说明该秒无成交或价格未变)，
        #    这不代表风险为0，而是代表延续了上一秒的市场状态。
        #    因此，我们将 0 替换为 NaN，然后使用 ffill() 沿用最近一次有效波动率。
        # -----------------------------------------------------------
        
        # 1. 价格和 VWAP 缺失处理
        df_bin['bin_price_close'] = df_bin['bin_price_close'].ffill()
        df_bin['bin_vwap'] = df_bin['bin_vwap'].fillna(df_bin['bin_price_close'])
        
        # 2. 波动率处理：0 -> NaN -> 前值填充 -> 兜底 0.01
        # 这样能保留“局部市场热度”，例如刚发生过剧烈波动，接下来几秒即使无成交，
        # 波动率依然会保持在高位，从而正确提示高风险。
        df_bin['bin_volatility'] = df_bin['bin_volatility'].replace(0, np.nan)
        df_bin['bin_volatility'] = df_bin['bin_volatility'].ffill()
        df_bin['bin_volatility'] = df_bin['bin_volatility'].fillna(0.01) # 极少数开头的缺失值给个小值

        print(f"   -> Binance 聚合成功: {len(df_bin)} 条, 波动率已清洗。")

        # --- C. Gas 费 ---
        print(" 加载 Gas 费数据...")
        gas_map = {}
        if os.path.exists(config.GAS_FEE_CSV):
            df_gas = pd.read_csv(config.GAS_FEE_CSV)
            if 'number' in df_gas.columns: df_gas.rename(columns={'number': 'block_number'}, inplace=True)
            gas_map = dict(zip(df_gas['block_number'], df_gas['base_fee_per_gas']))

        # --- D. Merge Asof ---
        print(" 执行数据对齐...")
        if df_bin.index.tz is None: df_bin.index = df_bin.index.tz_localize('UTC')

        try:
            df_merged = pd.merge_asof(
                df_uni, df_bin, 
                left_on='timestamp', right_index=True, 
                direction='backward', tolerance=pd.Timedelta('5m')
            )
        except Exception as e:
            print(f" Merge 失败: {e}")
            return

        df_merged['base_fee'] = df_merged['block_number'].map(gas_map)
        df_merged['base_fee'] = df_merged['base_fee'].ffill().fillna(20000000000)
        df_merged.dropna(subset=['bin_vwap'], inplace=True)

        if not df_merged.empty:
            self.df_final = df_merged
            self.df_final.to_pickle(config.PROCESSED_DATA_PKL)
            print(" 数据构建完成并已缓存。")

    def _decode_uni_log(self, record):
        try:
            ts_str = record['block_timestamp'].replace(' UTC', '') if 'UTC' in record['block_timestamp'] else record['block_timestamp']
            raw_data = record['data'].replace('0x', '')
            if len(raw_data) < 256: return None

            sqrt_price_x96 = int(raw_data[128:192], 16)
            liquidity = int(raw_data[192:256], 16)
            price_raw_ratio = (sqrt_price_x96 / (2**96)) ** 2
            
            p1 = price_raw_ratio * (10**12)
            p2 = price_raw_ratio / (10**12)
            
            final_price = p1 if 1000 < p1 < 10000 else (1/p1 if 1000 < 1/p1 < 10000 else (p2 if 1000 < p2 < 10000 else (1/p2 if 1000 < 1/p2 < 10000 else (10**12)/price_raw_ratio)))
            
            if final_price < 100 or final_price > 20000: return None

            return {
                'timestamp': ts_str,
                'block_number': int(record['block_number']),
                'uni_price': final_price,
                'sqrt_price_x96': sqrt_price_x96,
                'uni_liquidity': liquidity,
                'uni_volatility': 0
            }
        except: return None

    def get_chart_data(self, timeframe='1H'):
        if self.df_final is None or self.df_final.empty: return []
        df = self.df_final.set_index('timestamp')
        resampled = df[['uni_price', 'bin_vwap']].resample(timeframe).mean().reset_index()
        resampled['spread_pct'] = (resampled['bin_vwap'] - resampled['uni_price']) / resampled['uni_price'] * 100
        resampled = resampled.replace([np.inf, -np.inf], 0).fillna(0)
        resampled['timestamp'] = resampled['timestamp'].apply(lambda x: x.isoformat())
        return resampled.to_dict(orient='records')
    
    def _calculate_risk_score(self, volatility, uni_slippage_pct, net_profit, gas_cost):
        # 1. 波动率评分 (改为更敏感的系数，假设 0.1 波动率 => 20分)
        # 0.5 波动率 => 100分
        score_vol = min(100, volatility * 200) 
        
        # 2. 深度/滑点评分
        if uni_slippage_pct >= 0.0005: score_depth = 100
        else: score_depth = (uni_slippage_pct / 0.0005) * 80
        
        # 3. 利润鲁棒性
        if gas_cost > 0:
            ratio = net_profit / gas_cost
            score_robust = 100 if ratio < 1.0 else max(0, 100 - (ratio - 1) * 10)
        else: score_robust = 0
            
        return int(max(score_vol, score_depth, score_robust))

    def _calc_uni_v3_slippage(self, liquidity, sqrt_price_x96, amount_eth, is_buying_eth):
        if liquidity == 0: return 1.0
        sqrt_P = sqrt_price_x96 / (2 ** 96)
        amount_0 = amount_eth * 1e18
        try:
            if not is_buying_eth: # Sell ETH
                denominator = liquidity + amount_0 * sqrt_P
                sqrt_P_next = (liquidity * sqrt_P) / denominator
                amount_1 = liquidity * (sqrt_P - sqrt_P_next)
                p_spot, p_exec = sqrt_P ** 2, amount_1 / amount_0
                return max(0.0, (p_spot - p_exec) / p_spot)
            else: # Buy ETH
                if liquidity <= amount_0 * sqrt_P: return 1.0
                denominator = liquidity - amount_0 * sqrt_P
                sqrt_P_next = (liquidity * sqrt_P) / denominator
                amount_1 = liquidity * (sqrt_P_next - sqrt_P)
                p_spot, p_exec = sqrt_P ** 2, amount_1 / amount_0
                return max(0.0, (p_exec - p_spot) / p_spot)
        except: return 1.0

    def identify_opportunities_algo_b(self, min_profit_usd=0.0):
        if self.df_final is None or self.df_final.empty: return []
        results = []
        
        for row in self.df_final.itertuples():
            p_uni, p_bin = row.uni_price, row.bin_vwap
            raw_spread = abs(p_uni - p_bin) / p_uni
            if raw_spread < 0.0015: continue

            liquidity, volatility = row.uni_liquidity, row.bin_volatility
            base_fee, sqrt_price_x96 = row.base_fee, getattr(row, 'sqrt_price_x96', 0)
            
            if p_bin > p_uni:
                direction, spread_val = "Buy_Uni_Sell_Bin", (p_bin - p_uni) / p_uni
            else:
                direction, spread_val = "Buy_Bin_Sell_Uni", (p_uni - p_bin) / p_bin
            
            best_profit, best_amount, best_details = -9999, 0, {}
            
            for amount_eth in config.SIMULATION_AMOUNTS:
                is_buying_eth_on_uni = (direction == "Buy_Uni_Sell_Bin")
                uni_slippage_pct = self._calc_uni_v3_slippage(liquidity, sqrt_price_x96, amount_eth, is_buying_eth_on_uni) if sqrt_price_x96 > 0 else (0.1 if liquidity == 0 else (amount_eth * 1e18) / liquidity * 0.5)
                
                # 直接使用清洗后的 volatility (已无 0 值)
                bin_slippage_pct = config.ALGO_IMPACT_FACTOR * volatility * (amount_eth ** 0.5)
                
                gas_cost_usd = ((config.GAS_LIMIT_SWAP * (base_fee + 2e9)) / 1e18) * p_uni
                total_slippage = uni_slippage_pct + bin_slippage_pct
                gross_profit = amount_eth * p_uni * (spread_val - total_slippage - (config.CEX_TAKER_FEE + config.DEX_FEE_TIER))
                net_profit = gross_profit - gas_cost_usd - config.FIXED_TRANSFER_COST
                
                if net_profit > best_profit:
                    best_profit, best_amount = net_profit, amount_eth
                    best_details = {"uni_slip": uni_slippage_pct, "bin_slip": bin_slippage_pct, "gas": gas_cost_usd, "roi": net_profit / (amount_eth * p_uni)}
            
            if best_profit > min_profit_usd:
                risk_score = self._calculate_risk_score(volatility, best_details['uni_slip'], best_profit, best_details['gas'])
                results.append({
                    "timestamp": row.timestamp.isoformat(),
                    "block_number": row.block_number,
                    "direction": direction,
                    "price_uni": p_uni, "price_bin": p_bin,
                    "spread_pct": spread_val * 100,
                    "volatility": volatility,
                    "optimal_amount_eth": best_amount,
                    "net_profit_usd": best_profit,
                    "roi_pct": best_details['roi'] * 100,
                    "risk_score": risk_score, # 确保包含 risk_score
                    "details": {
                        "est_uni_slippage_pct": best_details['uni_slip'] * 100,
                        "est_bin_slippage_pct": best_details['bin_slip'] * 100,
                        "gas_cost_usd": best_details['gas']
                    }
                })
        
        return sorted(results, key=lambda x: x['net_profit_usd'], reverse=True)

service = DataService()