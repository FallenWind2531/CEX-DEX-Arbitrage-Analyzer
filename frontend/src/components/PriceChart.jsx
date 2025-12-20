import React, { useState, useMemo, useEffect } from 'react';
import { 
  ComposedChart, Line, Bar, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Brush, ReferenceLine
} from 'recharts';
import { format } from 'date-fns';
import { ZoomIn, ZoomOut, BarChart2, Maximize2, Minimize2 } from 'lucide-react';

const PriceChart = ({ data, highlightTimestamp }) => {
  const [autoScale, setAutoScale] = useState(true);
  const [showSpread, setShowSpread] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);
  const [brushRange, setBrushRange] = useState({ startIndex: 0, endIndex: 0 });

  const processedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      // 创建一个数值型的时间字段用于 X 轴
      timestampNum: new Date(item.timestamp).getTime(),
      priceDiff: item.price - item.price_usdt_eth
    }));
  }, [data]);

  // 初始化 Brush
  useEffect(() => {
    if (processedData.length > 0 && brushRange.endIndex === 0) {
      setBrushRange({ startIndex: 0, endIndex: processedData.length - 1 });
    }
  }, [processedData]);

  // 2. 缩放逻辑
  useEffect(() => {
    if (highlightTimestamp && processedData.length > 0) {
      const targetTime = new Date(highlightTimestamp).getTime();
      let closestIdx = -1;
      let minDiff = Infinity;

      processedData.forEach((item, index) => {
        const diff = Math.abs(item.timestampNum - targetTime);
        if (diff < minDiff) {
          minDiff = diff;
          closestIdx = index;
        }
      });

      if (closestIdx !== -1) {
        // 缩放窗口大小
        const windowSize = 20; 
        const newStartIndex = Math.max(0, closestIdx - windowSize);
        const newEndIndex = Math.min(processedData.length - 1, closestIdx + windowSize);

        setBrushRange({ startIndex: newStartIndex, endIndex: newEndIndex });
        setShowSpread(true);
      }
    }
  }, [highlightTimestamp, processedData]);

  // ESC 退出全屏
  useEffect(() => {
    const handleEsc = (event) => {
      if (event.key === 'Escape') setIsExpanded(false);
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, []);

  const containerStyle = isExpanded 
    ? "fixed inset-0 z-50 bg-white p-8 w-screen h-screen flex flex-col" 
    : "bg-white p-6 rounded-xl shadow-sm border border-gray-100 h-[550px] flex flex-col relative transition-all duration-300";

  return (
    <div className={containerStyle} onDoubleClick={() => setIsExpanded(!isExpanded)}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          USDT/ETH 价格与价差分析
          {isExpanded && <span className="text-xs font-normal text-gray-500 bg-gray-100 px-2 py-1 rounded">全屏模式 (按 ESC 退出)</span>}
        </h3>
        
        <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
          <button onClick={() => setShowSpread(!showSpread)} className={`flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg border transition-colors ${showSpread ? 'bg-purple-50 border-purple-200 text-purple-700' : 'bg-gray-50 border-gray-200 text-gray-600'}`}>
            <BarChart2 size={16} /> {showSpread ? "隐藏价差" : "显示价差"}
          </button>
          <button onClick={() => setAutoScale(!autoScale)} className={`flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg border transition-colors ${autoScale ? 'bg-blue-50 border-blue-200 text-blue-700' : 'bg-gray-50 border-gray-200 text-gray-600'}`}>
            {autoScale ? <ZoomIn size={16} /> : <ZoomOut size={16} />} {autoScale ? "聚焦" : "全景"}
          </button>
          <button onClick={() => setIsExpanded(!isExpanded)} className={`flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg border transition-colors ${isExpanded ? 'bg-gray-800 text-white border-gray-800' : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'}`} title={isExpanded ? "退出全屏" : "全屏查看"}>
            {isExpanded ? <Minimize2 size={16} /> : <Maximize2 size={16} />} {isExpanded ? "退出" : "放大"}
          </button>
        </div>
      </div>

      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={processedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            
            <XAxis 
              dataKey="timestampNum" 
              type="number" 
              domain={['dataMin', 'dataMax']}
              tickFormatter={(unixTime) => { 
                try { return format(new Date(unixTime), 'MM/dd HH:mm'); } catch (e) { return ''; } 
              }}
              stroke="#9ca3af" 
              fontSize={12} 
              minTickGap={30}
              scale="time" 
            />

            <YAxis yAxisId="left" domain={autoScale ? ['dataMin - 5', 'dataMax + 5'] : [0, 'auto']} stroke="#9ca3af" fontSize={12} tickFormatter={(val) => `$${val.toFixed(0)}`} label={{ value: 'ETH 价格 (USDT)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#9ca3af' } }} />
            <YAxis yAxisId="right" orientation="right" domain={['auto', 'auto']} stroke="#8884d8" fontSize={12} tickFormatter={(val) => `${val > 0 ? '+' : ''}${val.toFixed(1)}`} hide={!showSpread} label={showSpread ? { value: '价差 (Diff)', angle: 90, position: 'insideRight', style: { textAnchor: 'middle', fill: '#8884d8' } } : null} />
            
            <Tooltip 
              labelFormatter={(label) => format(new Date(label), 'yyyy-MM-dd HH:mm')} 
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} 
              formatter={(value, name) => [`$${Number(value).toFixed(2)}`, name]} 
            />
            <Legend verticalAlign="top" height={36}/>
            
            {showSpread && <ReferenceLine y={0} yAxisId="right" stroke="#e5e7eb" />}

            {highlightTimestamp && (
              <ReferenceLine 
                x={new Date(highlightTimestamp).getTime()} 
                yAxisId="left"
                stroke="#ff4d00" 
                strokeDasharray="3 3"
                strokeWidth={2}
                label={{ 
                  value: 'Selected', 
                  position: 'insideTopRight', 
                  fill: '#ff4d00',
                  fontSize: 12
                }}
              />
            )}

            {showSpread && (
              <Bar 
                yAxisId="right"
                dataKey="priceDiff" 
                name="价差 (Binance - Uni)" 
                barSize={isExpanded ? 8 : 4}
                fill="#8884d8"
                opacity={0.6}
              />
            )}

            <Line yAxisId="left" type="monotone" dataKey="price" stroke="#F3BA2F" name="Binance (CEX)" strokeWidth={2} dot={false} connectNulls={true} isAnimationActive={false} />
            <Line yAxisId="left" type="monotone" dataKey="price_usdt_eth" stroke="#FF007A" name="Uniswap V3 (DEX)" strokeWidth={2} dot={false} connectNulls={true} isAnimationActive={false} />

            <Brush 
              dataKey="timestampNum" 
              height={30} 
              stroke="#8884d8"
              tickFormatter={(unixTime) => format(new Date(unixTime), 'MM/dd')}
              alwaysShowText={false}
              startIndex={brushRange.startIndex}
              endIndex={brushRange.endIndex}
              onChange={(newIndex) => {
                if (newIndex.startIndex !== undefined && newIndex.endIndex !== undefined) {
                  setBrushRange({ startIndex: newIndex.startIndex, endIndex: newIndex.endIndex });
                }
              }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default PriceChart;