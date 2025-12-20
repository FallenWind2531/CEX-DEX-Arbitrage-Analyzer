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

// 获取套利分析列表
export const fetchAnalysisData = async (threshold = 0.5, capital = 10000) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/analysis`, {
      params: { threshold, capital }
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching analysis data:", error);
    return [];
  }
};

// 获取统计摘要
export const fetchSummaryData = async (threshold = 0.5, capital = 10000) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/summary`, {
      params: { threshold, capital }
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching summary data:", error);
    return null;
  }
};