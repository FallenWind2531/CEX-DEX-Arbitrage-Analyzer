import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// 获取图表数据
export const fetchChartData = async (timeframe = '1H') => {
  try {
    const response = await axios.get(`${API_BASE_URL}/chart`, {
      params: { timeframe }
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching chart data:", error);
    return [];
  }
};

// 获取套利机会列表 (算法B)
export const fetchOpportunities = async (minProfit = 10.0) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/opportunities`, {
      params: { min_profit: minProfit }
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching opportunities data:", error);
    return [];
  }
};

// 获取统计摘要
export const fetchSummaryData = async (minProfit = 10.0) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/summary`, {
      params: { min_profit: minProfit }
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching summary data:", error);
    return null;
  }
};
