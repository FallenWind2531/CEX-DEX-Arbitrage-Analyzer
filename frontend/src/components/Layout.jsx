import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, List, TrendingUp } from 'lucide-react';

const Layout = ({ children }) => {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: '仪表盘', icon: LayoutDashboard },
    { path: '/opportunities', label: '套利机会', icon: List },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* 顶部导航栏 */}
      <nav className="bg-white border-b border-gray-200 px-8 py-3 flex items-center justify-between sticky top-0 z-50 shadow-sm">
        <div className="flex items-center gap-8">
          {/* Logo */}
          <div className="flex items-center gap-2 text-blue-600">
            <TrendingUp size={26} strokeWidth={2.5} />
            <span className="text-xl font-bold tracking-tight">Arbitrage Analyzer</span>
          </div>
          
          {/* 导航菜单 */}
          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-blue-50 text-blue-600 shadow-sm'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <Icon size={18} />
                  {item.label}
                </NavLink>
              );
            })}
          </div>
        </div>
        
        <div className="text-sm text-gray-500">
          数据源: <span className="font-medium text-gray-700">Historical Data (2025/09)</span>
        </div>
      </nav>

      {/* 主要内容区域 */}
      <main className="flex-1 p-8 max-w-[1600px] mx-auto w-full">
        {children}
      </main>

      {/* 页脚 */}
      <footer className="p-6 text-center text-gray-400 text-sm border-t border-gray-100 bg-white">
        © 2025 CEX-DEX Arbitrage Project. All rights reserved.
      </footer>
    </div>
  );
};

export default Layout;
