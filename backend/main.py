# backend/main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
from pydantic import BaseModel
import pandas as pd

from data_service import service

# --- 数据模型定义 ---

class ChartPoint(BaseModel):
    timestamp: str
    price_usdt_eth: float # DEX 价格
    price: float          # CEX 价格
    spread_pct: float     # 价差

class ArbitrageOpportunity(BaseModel):
    timestamp: str
    tx_hash: str
    block_number: int
    
    # 价格信号
    price_usdt_eth: float
    price: float
    spread_pct: float
    direction: str        # DEX_TO_CEX 或 CEX_TO_DEX
    
    # 财务数据
    gross_profit: float   # 毛利
    cost_gas: float       # Gas 成本 (USDT)
    estimated_profit: float # 净利润 (扣除 Gas、CEX手续费、提币费)

class Summary(BaseModel):
    total_opportunities: int
    total_potential_profit: float
    max_single_profit: float
    avg_roi_pct: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行数据检查与加载
    service.initialize()
    yield

app = FastAPI(
    title="Non-Atomic Arbitrage System", 
    version="1.0",
    lifespan=lifespan
)

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 接口路由 ---

@app.get("/api/chart", response_model=List[ChartPoint])
def get_chart(timeframe: str = Query("1H", description="1H, 4H, 1D")):
    """获取价格对比图表数据"""
    mapping = {"1H": "1H", "4H": "4H", "1D": "1D"}
    rule = mapping.get(timeframe, "1H")
    return service.get_chart_data(rule)

@app.get("/api/analysis", response_model=List[ArbitrageOpportunity])
def get_analysis(
    threshold: float = Query(0.5, description="价差阈值%"),
    capital: float = Query(10000.0, description="投入本金USDT")
):
    """获取详细的套利机会列表"""
    return service.analyze_opportunities(threshold, capital)

@app.get("/api/summary", response_model=Summary)
def get_summary(
    threshold: float = 0.5,
    capital: float = 10000.0
):
    """获取统计摘要"""
    data = service.analyze_opportunities(threshold, capital)
    if not data:
        return Summary(total_opportunities=0, total_potential_profit=0, max_single_profit=0, avg_roi_pct=0)
    
    df = pd.DataFrame(data)
    total_profit = df['estimated_profit'].sum()
    max_profit = df['estimated_profit'].max()
    # ROI = 净利润 / 本金
    avg_roi = (df['estimated_profit'].mean() / capital) * 100
    
    return Summary(
        total_opportunities=len(data),
        total_potential_profit=total_profit,
        max_single_profit=max_profit,
        avg_roi_pct=avg_roi
    )

if __name__ == "__main__":
    import uvicorn
    # 开发模式启动
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)