import React, { useMemo } from 'react';
import { AlertCircle, MousePointerClick } from 'lucide-react';

const ArbitrageTable = ({ data, onRowClick, selectedTimestamp }) => {
  
  // 使用 useMemo 缓存计算结果，避免每次渲染都重新计算
  const uniqueData = useMemo(() => {
    const map = new Map();
    
    data.forEach(item => {
      const existing = map.get(item.timestamp);
      // 如果该时间戳还没有记录，或者当前记录的利润更高，则更新 Map
      if (!existing || item.estimated_profit > existing.estimated_profit) {
        map.set(item.timestamp, item);
      }
    });

    // 将 Map 转回数组，并按利润降序排列（保持原有的 Top 排序逻辑）
    return Array.from(map.values())
      .sort((a, b) => b.estimated_profit - a.estimated_profit);
  }, [data]);

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
              <th className="p-3">Binance</th>
              <th className="p-3">Uniswap</th>
              <th className="p-3">价差%</th>
              <th className="p-3">Gas成本</th>
              <th className="p-3 text-right">净利润 (USDT)</th>
            </tr>
          </thead>
          <tbody>
            {uniqueData.length === 0 ? ( 
              <tr>
                <td colSpan="7" className="p-8 text-center text-gray-400">暂无符合条件的套利机会</td>
              </tr>
            ) : (
              uniqueData.slice(0, 20).map((row, idx) => {
                const isSelected = String(row.timestamp) === String(selectedTimestamp);
                
                return (
                  <tr 
                    key={row.timestamp} 
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
                        row.direction === 'DEX_TO_CEX' ? 'bg-purple-100 text-purple-700' : 'bg-orange-100 text-orange-700'
                      }`}>
                        {row.direction === 'DEX_TO_CEX' ? 'Uni -> Bin' : 'Bin -> Uni'}
                      </span>
                    </td>
                    <td className="p-3">${row.price.toFixed(2)}</td>
                    <td className="p-3">${row.price_usdt_eth.toFixed(2)}</td>
                    <td className="p-3 text-gray-500">{row.spread_pct.toFixed(2)}%</td>
                    <td className="p-3 text-gray-500">${row.cost_gas.toFixed(2)}</td>
                    <td className="p-3 text-right font-bold text-green-600">
                      +${row.estimated_profit.toFixed(2)}
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