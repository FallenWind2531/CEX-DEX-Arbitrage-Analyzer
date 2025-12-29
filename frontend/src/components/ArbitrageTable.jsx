import React, { useMemo } from 'react';
import { AlertCircle, MousePointerClick, ShieldAlert } from 'lucide-react';

const ArbitrageTable = ({ data, onRowClick, selectedTimestamp }) => {
  
  const uniqueData = useMemo(() => {
    const map = new Map();
    
    data.forEach(item => {
      const existing = map.get(item.timestamp);
      if (!existing || item.net_profit_usd > existing.net_profit_usd) {
        map.set(item.timestamp, item);
      }
    });

    return Array.from(map.values())
      .sort((a, b) => b.net_profit_usd - a.net_profit_usd);
  }, [data]);

  // 风险等级辅助函数
  const getRiskBadge = (score) => {
    let colorClass = '';
    let label = '';
    
    if (score >= 70) {
      colorClass = 'bg-red-100 text-red-700 border-red-200';
      label = '高风险';
    } else if (score >= 30) {
      colorClass = 'bg-yellow-100 text-yellow-700 border-yellow-200';
      label = '中风险';
    } else {
      colorClass = 'bg-green-100 text-green-700 border-green-200';
      label = '低风险';
    }

    return (
      <div className="flex items-center gap-2">
        <span className={`px-2 py-0.5 rounded text-xs font-semibold border ${colorClass}`}>
          {label}
        </span>
        <span className="text-xs text-gray-400">({score})</span>
      </div>
    );
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 className="text-lg font-semibold mb-4 text-gray-800 flex items-center gap-2">
        <AlertCircle size={20} className="text-blue-500"/> 
        高收益套利机会列表 (Top 20)
        <span className="text-xs font-normal text-gray-400 ml-auto flex items-center gap-1">
          <MousePointerClick size={14}/> 点击行可在图表中定位
        </span>
      </h3>
      <div className="overflow-x-auto max-h-[500px]">
        <table className="w-full text-left text-sm text-gray-600 relative">
          <thead className="bg-gray-50 text-gray-900 font-medium sticky top-0 z-10">
            <tr>
              <th className="p-3">时间</th>
              <th className="p-3">方向</th>
              <th className="p-3">风险评估</th> {/* 新增列 */}
              <th className="p-3">Binance</th>
              <th className="p-3">Uniswap</th>
              <th className="p-3">价差%</th>
              <th className="p-3">最优交易量(ETH)</th>
              <th className="p-3">Gas成本</th>
              <th className="p-3">ROI%</th>
              <th className="p-3 text-right">净利润 (USDT)</th>
            </tr>
          </thead>
          <tbody>
            {uniqueData.length === 0 ? ( 
              <tr>
                <td colSpan="10" className="p-8 text-center text-gray-400">暂无符合条件的套利机会</td>
              </tr>
            ) : (
              uniqueData.slice(0, 20).map((row, idx) => {
                const isSelected = String(row.timestamp) === String(selectedTimestamp);
                
                return (
                  <tr 
                    key={row.timestamp + '-' + idx} 
                    onClick={() => onRowClick(row.timestamp)}
                    className={`border-t border-gray-100 transition-colors cursor-pointer ${
                      isSelected ? 'bg-blue-100 border-l-4 border-l-blue-600' : 'hover:bg-gray-50'
                    }`}
                  >
                    <td className="p-3 whitespace-nowrap font-medium">
                      {new Date(row.timestamp).toLocaleString()}
                    </td>
                    <td className="p-3">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        row.direction === 'Buy_Uni_Sell_Bin' ? 'bg-purple-100 text-purple-700' : 'bg-orange-100 text-orange-700'
                      }`}>
                        {row.direction === 'Buy_Uni_Sell_Bin' ? 'Uni → Bin' : 'Bin → Uni'}
                      </span>
                    </td>
                    {/* 风险列 */}
                    <td className="p-3">
                      {getRiskBadge(row.risk_score || 0)}
                    </td>
                    <td className="p-3">${row.price_bin.toFixed(2)}</td>
                    <td className="p-3">${row.price_uni.toFixed(2)}</td>
                    <td className="p-3 text-gray-500">{row.spread_pct.toFixed(2)}%</td>
                    <td className="p-3 text-gray-500">{row.optimal_amount_eth.toFixed(4)}</td>
                    <td className="p-3 text-gray-500">${row.details.gas_cost_usd.toFixed(2)}</td>
                    <td className="p-3 text-gray-500">{row.roi_pct.toFixed(2)}%</td>
                    <td className="p-3 text-right font-bold text-green-600">
                      +${row.net_profit_usd.toFixed(2)}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ArbitrageTable;