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
        
        # --- A. 解析 Uniswap Logs (BigQuery JSON) ---
        print(f" 正在解析 Uniswap 日志: {config.UNI_LOGS_JSON}")
        if not os.path.exists(config.UNI_LOGS_JSON):
            print(f" 错误: 找不到文件 {config.UNI_LOGS_JSON}")
            return

        uni_data = []
        try:
            # 自动识别 JSON Array 或 JSON Lines 格式
            with open(config.UNI_LOGS_JSON, 'r') as f:
                first_char = f.read(1)
                f.seek(0)
                
                if first_char == '[':
                    print("   -> 格式识别: JSON Array")
                    raw_list = json.load(f)
                    for record in raw_list:
                        parsed = self._decode_uni_log(record)
                        if parsed: uni_data.append(parsed)
                else:
                    print("   -> 格式识别: JSON Lines")
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
            print(" Uniswap 数据为空，请检查 JSON 内容。")
            return

        # 转换时间戳并排序 (确保 UTC)
        df_uni['timestamp'] = pd.to_datetime(df_uni['timestamp'], utc=True)
        df_uni.sort_values('timestamp', inplace=True)
        
        print(f"   -> Uni 解析成功: {len(df_uni)} 条")
        print(f"   -> Uni 价格样本: {df_uni['uni_price'].iloc[0]:.2f} - {df_uni['uni_price'].iloc[-1]:.2f}")

        print(f" 正在聚合 Binance CSV 分片... 目录: {config.BINANCE_TRADES_DIR}")
        trade_files = glob.glob(os.path.join(config.BINANCE_TRADES_DIR, "*.csv"))
        if not trade_files:
            print(" 错误: 没有找到 Binance CSV 文件。")
            return

        bin_dfs = []
        total_files = len(trade_files)
        for idx, file in enumerate(trade_files):
            if idx % 5 == 0:
                print(f"   -> 进度: {idx}/{total_files} | 读取 {os.path.basename(file)}")
            
            try:
                chunk = pd.read_csv(file)
                
                # 标准化列名 (处理 ts vs time)
                if 'time' not in chunk.columns and 'ts' in chunk.columns:
                    chunk.rename(columns={'ts': 'time'}, inplace=True)
                
                # 转换时间戳 (单位是 us 微秒)
                chunk['datetime'] = pd.to_datetime(chunk['time'], unit='us', utc=True)
                
                # 预计算成交额
                chunk['quote_qty'] = chunk['price'] * chunk['qty']
                
                # 按 1秒 重采样聚合
                resampled = chunk.resample('1s', on='datetime').agg({
                    'price': ['mean', 'std'],  # std 即波动率
                    'qty': 'sum',
                    'quote_qty': 'sum'
                })
                
                resampled.columns = ['bin_price_close', 'bin_volatility', 'bin_volume', 'bin_quote_vol']
                # 计算 VWAP (加权均价)
                resampled['bin_vwap'] = resampled['bin_quote_vol'] / resampled['bin_volume']
                
                bin_dfs.append(resampled)
            except Exception as e:
                print(f"    读取失败 {file}: {e}")

        if not bin_dfs:
            print(" Binance 数据聚合失败。")
            return

        df_bin = pd.concat(bin_dfs).sort_index()
        
        # 填充空值
        df_bin['bin_price_close'] = df_bin['bin_price_close'].ffill()
        df_bin['bin_vwap'] = df_bin['bin_vwap'].fillna(df_bin['bin_price_close'])
        df_bin['bin_volatility'] = df_bin['bin_volatility'].fillna(0)
        
        print(f"   -> Binance 聚合成功: {len(df_bin)} 条秒级快照")

        # ---  加载 Gas 费 ---
        print(" 加载 Gas 费数据...")
        if os.path.exists(config.GAS_FEE_CSV):
            df_gas = pd.read_csv(config.GAS_FEE_CSV)
            if 'number' in df_gas.columns:
                df_gas.rename(columns={'number': 'block_number'}, inplace=True)
            # 建立 Block -> BaseFee 映射
            gas_map = dict(zip(df_gas['block_number'], df_gas['base_fee_per_gas']))
            print(f"   -> Gas 数据就绪: {len(gas_map)} 条记录")
        else:
            print(" 未找到 Gas 文件，将使用默认值。")
            gas_map = {}

        # --- D. 数据合并 (Merge Asof) ---
        print(" 执行数据对齐 (Merge Asof)...")
        
        # 确保索引具有时区信息
        if df_bin.index.tz is None:
            df_bin.index = df_bin.index.tz_localize('UTC')

        try:
            # 以 Uniswap 事件为基准，向后查找最近的 Binance 状态
            df_merged = pd.merge_asof(
                df_uni, 
                df_bin, 
                left_on='timestamp', 
                right_index=True, 
                direction='backward', 
                tolerance=pd.Timedelta('5m') # 允许最大5分钟的延迟
            )
        except Exception as e:
            print(f" Merge 失败: {e}")
            return

        # 映射 Gas
        df_merged['base_fee'] = df_merged['block_number'].map(gas_map)
        df_merged['base_fee'] = df_merged['base_fee'].ffill().fillna(20000000000)

        # 清洗无效行 (没对齐到 Binance 数据的行)
        before_len = len(df_merged)
        df_merged.dropna(subset=['bin_vwap'], inplace=True)
        after_len = len(df_merged)
        
        print(f"   -> 对齐统计: 总 {before_len} 行 -> 有效 {after_len} 行 (丢弃 {before_len - after_len})")

        if df_merged.empty:
            print("错误: 合并后没有数据。请检查时间范围是否重叠。")
        else:
            self.df_final = df_merged
            # 保存缓存
            self.df_final.to_pickle(config.PROCESSED_DATA_PKL)
            print(" 数据构建完成并已缓存。")

    def _decode_uni_log(self, record):
        """解码 Uniswap Log，包含 0x11b8 池价格修正逻辑"""
        try:
            # 处理时间戳字符串
            ts_str = record['block_timestamp']
            if 'UTC' in ts_str:
                ts_str = ts_str.replace(' UTC', '')
            
            raw_data = record['data'].replace('0x', '')
            if len(raw_data) < 256: return None

            # 提取核心字段
            sqrt_price_x96 = int(raw_data[128:192], 16)
            liquidity = int(raw_data[192:256], 16)
            
            # Q64.96 定点数转 float
            price_raw_ratio = (sqrt_price_x96 / (2**96)) ** 2
            
            # 针对 USDT(6)/WETH(18) 池子的单位换算
            # 目标: 获得 USDT per ETH (数值约 2000-5000)
            
            # 假设 1: Token1/Token0 (WETH/USDT) * 10^12
            p1 = price_raw_ratio * (10**12)
            # 假设 2: Token0/Token1 (USDT/WETH) / 10^12
            p2 = price_raw_ratio / (10**12)
            
            final_price = 0.0
            
            # 智能判定区间 (2025年 ETH 价格预估在 1000-10000)
            if 1000 < p1 < 10000:
                final_price = p1
            elif 1000 < (1/p1) < 10000:
                final_price = 1/p1
            elif 1000 < p2 < 10000:
                final_price = p2
            elif 1000 < (1/p2) < 10000:
                final_price = 1/p2
            else:
                # 默认回退逻辑: 0x11b8 通常是 Token0=USDT, Token1=WETH
                # SqrtPrice 对应 Token1/Token0
                # Price = 1 / (Raw / 10^12)
                final_price = (10**12) / price_raw_ratio
            
            # 最终安全过滤
            if final_price < 100 or final_price > 20000:
                return None

            return {
                'timestamp': ts_str,
                'block_number': int(record['block_number']),
                'uni_price': final_price,
                'uni_liquidity': liquidity,
                'uni_volatility': 0 # 占位
            }
        except Exception as e:
            return None

    def get_chart_data(self, timeframe='1H'):
        """生成前端图表数据"""
        if self.df_final is None or self.df_final.empty: return []
        
        df = self.df_final.set_index('timestamp')
        resampled = df[['uni_price', 'bin_vwap']].resample(timeframe).mean().reset_index()
        
        # 计算价差百分比
        resampled['spread_pct'] = (resampled['bin_vwap'] - resampled['uni_price']) / resampled['uni_price'] * 100
        
        resampled = resampled.replace([np.inf, -np.inf], 0).fillna(0)
        resampled['timestamp'] = resampled['timestamp'].apply(lambda x: x.isoformat())
        
        return resampled.to_dict(orient='records')

    def identify_opportunities_algo_b(self, min_profit_usd=0.0):
        """
        核心算法 B: 基于统计冲击模型的非原子套利识别
        """
        if self.df_final is None or self.df_final.empty: return []
        
        results = []
        
        # 使用 itertuples 遍历每一行数据
        for row in self.df_final.itertuples():
            
            p_uni = row.uni_price
            p_bin = row.bin_vwap
            
            # 1. 快速过滤: 价差过小则跳过计算 (节省性能)
            # 0.0015 = 0.15% (涵盖 0.1% + 0.05% 手续费)
            raw_spread = abs(p_uni - p_bin) / p_uni
            if raw_spread < 0.0015: 
                continue

            liquidity = row.uni_liquidity
            volatility = row.bin_volatility
            base_fee = row.base_fee
            
            # 2. 确定套利方向
            if p_bin > p_uni:
                direction = "Buy_Uni_Sell_Bin" # CEX 贵，去 DEX 买
                spread_val = (p_bin - p_uni) / p_uni
            else:
                direction = "Buy_Bin_Sell_Uni" # DEX 贵，去 CEX 买
                spread_val = (p_uni - p_bin) / p_bin
            
            # 3. 循环寻找最佳投入量 (Optimal Amount)
            best_profit = -9999
            best_amount = 0
            best_details = {}
            
            # 模拟投入不同数量的 ETH
            for amount_eth in config.SIMULATION_AMOUNTS:
                
                # --- A. 计算 Uni 滑点 (基于 Liquidity) ---
                # 简化公式: Slippage% ≈ (Amount * 10^18) / Liquidity * C
                if liquidity > 0:
                    uni_slippage_pct = (amount_eth * 1e18) / liquidity * 0.5
                else:
                    uni_slippage_pct = 0.1 # 深度缺失惩罚
                
                # --- B. 计算 Bin 滑点 (基于 Volatility) ---
                # 算法 B 核心: Slippage = ImpactFactor * Vol * sqrt(Amount)
                # 若波动率为0，给一个默认风险值
                eff_vol = volatility if volatility > 0 else 5.0
                bin_slippage_pct = config.ALGO_IMPACT_FACTOR * eff_vol * (amount_eth ** 0.5)
                
                # --- C. 计算 Gas 成本 ---
                # Gas Price = Base + Priority(2Gwei)
                gas_price = base_fee + 2e9
                gas_cost_eth = (config.GAS_LIMIT_SWAP * gas_price) / 1e18
                gas_cost_usd = gas_cost_eth * p_uni
                
                # --- D. 利润计算 ---
                total_fee_rate = config.CEX_TAKER_FEE + config.DEX_FEE_TIER
                total_slippage = uni_slippage_pct + bin_slippage_pct
                
                # 毛利估算
                margin_per_unit = spread_val - total_slippage - total_fee_rate
                gross_profit = amount_eth * p_uni * margin_per_unit
                
                # 净利 = 毛利 - 固定成本 (Gas + 提币)
                net_profit = gross_profit - gas_cost_usd - config.FIXED_TRANSFER_COST
                
                if net_profit > best_profit:
                    best_profit = net_profit
                    best_amount = amount_eth
                    best_details = {
                        "uni_slip": uni_slippage_pct,
                        "bin_slip": bin_slippage_pct,
                        "gas": gas_cost_usd,
                        "roi": net_profit / (amount_eth * p_uni)
                    }
            
            # 4. 记录满足阈值的机会
            if best_profit > min_profit_usd:
                results.append({
                    "timestamp": row.timestamp.isoformat(),
                    "block_number": row.block_number,
                    "direction": direction,
                    "price_uni": p_uni,
                    "price_bin": p_bin,
                    "spread_pct": spread_val * 100,
                    "volatility": volatility,
                    
                    "optimal_amount_eth": best_amount,
                    "net_profit_usd": best_profit,
                    "roi_pct": best_details['roi'] * 100,
                    
                    "details": {
                        "est_uni_slippage_pct": best_details['uni_slip'] * 100,
                        "est_bin_slippage_pct": best_details['bin_slip'] * 100,
                        "gas_cost_usd": best_details['gas']
                    }
                })
        
        # 按净利润倒序排列
        return sorted(results, key=lambda x: x['net_profit_usd'], reverse=True)

# 单例模式
service = DataService()