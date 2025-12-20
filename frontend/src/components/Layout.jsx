import React from 'react';
import { LayoutDashboard } from 'lucide-react';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* 顶部导航栏 */}
      <nav className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-2 text-blue-600">
          <LayoutDashboard size={24} />
          <span className="text-xl font-bold tracking-tight">Arbitrage Analyzer</span>
        </div>
        <div className="text-sm text-gray-500">
          数据源: <span className="font-medium text-gray-700">Historical Data (2025/09)</span>
        </div>
      </nav>

      {/* 主要内容区域 */}
      <main className="flex-1 p-8 max-w-7xl mx-auto w-full">
        {children}
      </main>

      {/* 页脚 */}
      <footer className="p-6 text-center text-gray-400 text-sm">
        © 2025 CEX-DEX Arbitrage Project. All rights reserved.
      </footer>
    </div>
  );
};

export default Layout;