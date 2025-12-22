import React, { useEffect, useState } from 'react';
import { fetchChartData, fetchOpportunities, fetchSummaryData } from '../api/marketService';
import PriceChart from '../components/PriceChart';
import StatCard from '../components/StatCard';
import ArbitrageTable from '../components/ArbitrageTable';
import { Activity, DollarSign, TrendingUp, Filter, RefreshCw } from 'lucide-react';

const Dashboard = () => {
  // 状态管理
  const [chartData, setChartData] = useState([]);
  const [opportunities, setOpportunities] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  // 交互参数
  const [timeframe, setTimeframe] = useState('1H');
  const [minProfit, setMinProfit] = useState(10.0);
  const [selectedTimestamp, setSelectedTimestamp] = useState(null);

  // 加载数据函数
  const loadData = async () => {
    setLoading(true);
    try {
      // 并行请求所有数据
      const [chartRes, opportunitiesRes, summaryRes] = await Promise.all([
        fetchChartData(timeframe),
        fetchOpportunities(minProfit),
        fetchSummaryData(minProfit)
      ]);

      setChartData(chartRes);
      setOpportunities(opportunitiesRes);
      setSummary(summaryRes);
    } catch (error) {
      console.error("Failed to fetch data", error);
    } finally {
      setLoading(false);
    }
  };

  // 监听参数变化自动刷新
  useEffect(() => {
    loadData();
  }, [timeframe, minProfit]);

  return (
    <>
      <header className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">仪表盘概览</h1>
          <p className="text-gray-500 mt-2">监控 Uniswap V3 与 Binance 之间的非原子套利机会</p>
        </div>
        
        {/* 控制面板 */}
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">时间粒度</label>
            <select 
              value={timeframe} 
              onChange={(e) => setTimeframe(e.target.value)}
              className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-24 p-2"
            >
              <option value="1H">1 小时</option>
              <option value="4H">4 小时</option>
              <option value="1D">1 天</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">最小净利润 (USDT)</label>
            <input 
              type="number" 
              step="1"
              value={minProfit}
              onChange={(e) => setMinProfit(Number(e.target.value))}
              className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-28 p-2"
            />
          </div>

          <button 
            onClick={loadData}
            className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg transition-colors"
            title="刷新数据"
          >
            <RefreshCw size={20} className={loading ? "animate-spin" : ""} />
          </button>
        </div>
      </header>

      {/* 统计概览 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard 
          title="发现机会总数" 
          value={summary ? `${summary.total_opportunities} 次` : '-'} 
          icon={Activity} 
          trend="基于当前筛选" 
        />
        <StatCard 
          title="潜在总利润" 
          value={summary ? `$${summary.total_potential_profit.toFixed(2)}` : '-'} 
          icon={DollarSign} 
          trend="扣除Gas后"
        />
        <StatCard 
          title="单笔最大利润" 
          value={summary ? `$${summary.max_single_profit.toFixed(2)}` : '-'} 
          icon={TrendingUp} 
        />
        <StatCard 
          title="平均 ROI" 
          value={summary ? `${summary.avg_roi.toFixed(4)}%` : '-'} 
          icon={Filter} 
        />
      </div>

      {/* 图表与表格区域 */}
      <div className="grid grid-cols-1 gap-8">
        {/* 传递图表数据 */}
        <PriceChart 
          data={chartData} 
          highlightTimestamp={selectedTimestamp} 
        />
        
        {/* 传递分析列表数据 */}
        <ArbitrageTable 
          data={opportunities} 
          onRowClick={(timestamp) => {
            setSelectedTimestamp(timestamp);
          }}
          selectedTimestamp={selectedTimestamp}
        />
      </div>
    </>
  );
};

export default Dashboard;
