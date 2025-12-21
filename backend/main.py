# backend/main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
from pydantic import BaseModel
import pandas as pd
from data_service import service

# --- Pydantic 模型定义 ---

class ChartPoint(BaseModel):
    timestamp: str
    uni_price: float
    bin_vwap: float
    spread_pct: float

class ArbitrageDetails(BaseModel):
    est_uni_slippage_pct: float
    est_bin_slippage_pct: float
    gas_cost_usd: float

class AlgoBOpportunity(BaseModel):
    timestamp: str
    block_number: int
    direction: str
    price_uni: float
    price_bin: float
    spread_pct: float
    volatility: float
    
    optimal_amount_eth: float # 算法 B 算出的最佳交易量 (ETH)
    net_profit_usd: float     # 真实净利 (USDT)
    roi_pct: float            # 投资回报率 (%)
    
    details: ArbitrageDetails

class Summary(BaseModel):
    total_opportunities: int
    total_potential_profit: float
    max_single_profit: float
    avg_roi: float

# --- 生命周期管理 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据服务
    service.initialize()
    yield

app = FastAPI(title="Arbitrage Algo B System", lifespan=lifespan)

# 允许跨域请求 (方便前端调用)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API 接口 ---

@app.get("/api/chart", response_model=List[ChartPoint])
def get_chart(timeframe: str = "1H"):
    """获取价格对比图表数据"""
    return service.get_chart_data(timeframe)

@app.get("/api/opportunities", response_model=List[AlgoBOpportunity])
def get_opportunities(
    min_profit: float = Query(10.0, description="最小净利润阈值(USDT)")
):
    """
    运行算法：识别基于统计学冲击模型的非原子套利机会
    """
    return service.identify_opportunities_algo_b(min_profit_usd=min_profit)

@app.get("/api/summary", response_model=Summary)
def get_summary(min_profit: float = 10.0):
    """获取统计摘要"""
    data = service.identify_opportunities_algo_b(min_profit_usd=min_profit)
    if not data:
        return Summary(total_opportunities=0, total_potential_profit=0, max_single_profit=0, avg_roi=0)
    
    df = pd.DataFrame(data)
    
    return Summary(
        total_opportunities=len(data),
        total_potential_profit=df['net_profit_usd'].sum(),
        max_single_profit=df['net_profit_usd'].max(),
        avg_roi=df['roi_pct'].mean()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)