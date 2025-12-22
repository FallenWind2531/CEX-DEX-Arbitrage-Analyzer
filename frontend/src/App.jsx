import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import Dashboard from './pages/Dashboard';
import OpportunitiesPage from './pages/OpportunitiesPage';
import Layout from './components/Layout';
import './App.css';

// Antd 主题配置 - 与 Tailwind 颜色系统协调
const antdTheme = {
  token: {
    colorPrimary: '#2563eb', // Tailwind blue-600
    borderRadius: 8,
    colorSuccess: '#16a34a', // Tailwind green-600
    colorWarning: '#d97706', // Tailwind amber-600
    colorError: '#dc2626',   // Tailwind red-600
    fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
  },
  components: {
    Table: {
      headerBg: '#f9fafb', // Tailwind gray-50
      rowHoverBg: '#f3f4f6', // Tailwind gray-100
    },
    Card: {
      borderRadiusLG: 12,
    },
  },
};

function App() {
  return (
    <ConfigProvider theme={antdTheme} locale={zhCN}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/opportunities" element={<OpportunitiesPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
