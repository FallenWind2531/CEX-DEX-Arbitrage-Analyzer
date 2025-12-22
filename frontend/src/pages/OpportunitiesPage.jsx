import React, { useEffect, useState, useMemo } from 'react';
import { Table, Card, Tag, Space, InputNumber, Button, Tooltip, Statistic, Row, Col, Select, DatePicker, message } from 'antd';
import { DownloadOutlined, ReloadOutlined, FilterOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { fetchOpportunities } from '../api/marketService';
import dayjs from 'dayjs';

const OpportunitiesPage = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [minProfit, setMinProfit] = useState(10.0);
  
  // 前端筛选状态
  const [directionFilter, setDirectionFilter] = useState(null);
  const [dateRange, setDateRange] = useState(null);

  // 加载数据
  const loadData = async () => {
    setLoading(true);
    try {
      const result = await fetchOpportunities(minProfit);
      // 添加唯一key
      const dataWithKey = result.map((item, index) => ({
        ...item,
        key: `${item.timestamp}-${item.block_number}-${index}`,
      }));
      setData(dataWithKey);
      message.success(`成功加载 ${dataWithKey.length} 条套利机会`);
    } catch (error) {
      message.error('数据加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // 前端筛选后的数据
  const filteredData = useMemo(() => {
    let result = [...data];
    
    // 方向筛选
    if (directionFilter) {
      result = result.filter(item => item.direction === directionFilter);
    }
    
    // 时间范围筛选
    if (dateRange && dateRange[0] && dateRange[1]) {
      const startTime = dateRange[0].startOf('day').valueOf();
      const endTime = dateRange[1].endOf('day').valueOf();
      result = result.filter(item => {
        const itemTime = new Date(item.timestamp).getTime();
        return itemTime >= startTime && itemTime <= endTime;
      });
    }
    
    return result;
  }, [data, directionFilter, dateRange]);

  // 统计数据
  const stats = useMemo(() => {
    if (filteredData.length === 0) {
      return { total: 0, totalProfit: 0, avgRoi: 0, maxProfit: 0 };
    }
    const totalProfit = filteredData.reduce((sum, item) => sum + item.net_profit_usd, 0);
    const avgRoi = filteredData.reduce((sum, item) => sum + item.roi_pct, 0) / filteredData.length;
    const maxProfit = Math.max(...filteredData.map(item => item.net_profit_usd));
    return {
      total: filteredData.length,
      totalProfit,
      avgRoi,
      maxProfit,
    };
  }, [filteredData]);

  // 导出CSV
  const exportCSV = () => {
    if (filteredData.length === 0) {
      message.warning('没有数据可导出');
      return;
    }

    const headers = [
      '时间', '区块号', '方向', 'Binance价格', 'Uniswap价格', 
      '价差%', '波动率', '最优交易量(ETH)', 'Gas成本', 'Uni滑点%', 'Bin滑点%', 
      '净利润(USDT)', 'ROI%'
    ];
    
    const rows = filteredData.map(item => [
      item.timestamp,
      item.block_number,
      item.direction,
      item.price_bin.toFixed(2),
      item.price_uni.toFixed(2),
      item.spread_pct.toFixed(4),
      item.volatility.toFixed(6),
      item.optimal_amount_eth.toFixed(4),
      item.details.gas_cost_usd.toFixed(2),
      item.details.est_uni_slippage_pct.toFixed(4),
      item.details.est_bin_slippage_pct.toFixed(4),
      item.net_profit_usd.toFixed(2),
      item.roi_pct.toFixed(4),
    ]);

    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `arbitrage_opportunities_${dayjs().format('YYYY-MM-DD_HH-mm')}.csv`;
    link.click();
    message.success('导出成功');
  };

  // 表格列定义
  const columns = [
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      sorter: (a, b) => new Date(a.timestamp) - new Date(b.timestamp),
      render: (text) => dayjs(text).format('YYYY-MM-DD HH:mm:ss'),
      fixed: 'left',
    },
    {
      title: '区块号',
      dataIndex: 'block_number',
      key: 'block_number',
      width: 110,
      sorter: (a, b) => a.block_number - b.block_number,
    },
    {
      title: '方向',
      dataIndex: 'direction',
      key: 'direction',
      width: 120,
      render: (direction) => {
        const isDexToCex = direction === 'Buy_Uni_Sell_Bin';
        return (
          <Tag color={isDexToCex ? 'purple' : 'orange'}>
            {isDexToCex ? 'Uni → Bin' : 'Bin → Uni'}
          </Tag>
        );
      },
    },
    {
      title: 'Binance',
      dataIndex: 'price_bin',
      key: 'price_bin',
      width: 110,
      sorter: (a, b) => a.price_bin - b.price_bin,
      render: (val) => `$${val.toFixed(2)}`,
    },
    {
      title: 'Uniswap',
      dataIndex: 'price_uni',
      key: 'price_uni',
      width: 110,
      sorter: (a, b) => a.price_uni - b.price_uni,
      render: (val) => `$${val.toFixed(2)}`,
    },
    {
      title: '价差%',
      dataIndex: 'spread_pct',
      key: 'spread_pct',
      width: 90,
      sorter: (a, b) => a.spread_pct - b.spread_pct,
      render: (val) => `${val.toFixed(2)}%`,
    },
    {
      title: (
        <Tooltip title="市场波动率指标">
          波动率 <InfoCircleOutlined />
        </Tooltip>
      ),
      dataIndex: 'volatility',
      key: 'volatility',
      width: 100,
      sorter: (a, b) => a.volatility - b.volatility,
      render: (val) => val.toFixed(4),
    },
    {
      title: '最优量(ETH)',
      dataIndex: 'optimal_amount_eth',
      key: 'optimal_amount_eth',
      width: 120,
      sorter: (a, b) => a.optimal_amount_eth - b.optimal_amount_eth,
      render: (val) => val.toFixed(4),
    },
    {
      title: 'Gas成本',
      key: 'gas_cost',
      width: 100,
      sorter: (a, b) => a.details.gas_cost_usd - b.details.gas_cost_usd,
      render: (_, record) => `$${record.details.gas_cost_usd.toFixed(2)}`,
    },
    {
      title: (
        <Tooltip title="Uniswap 预估滑点">
          Uni滑点% <InfoCircleOutlined />
        </Tooltip>
      ),
      key: 'uni_slippage',
      width: 100,
      render: (_, record) => `${record.details.est_uni_slippage_pct.toFixed(3)}%`,
    },
    {
      title: (
        <Tooltip title="Binance 预估滑点">
          Bin滑点% <InfoCircleOutlined />
        </Tooltip>
      ),
      key: 'bin_slippage',
      width: 100,
      render: (_, record) => `${record.details.est_bin_slippage_pct.toFixed(3)}%`,
    },
    {
      title: 'ROI%',
      dataIndex: 'roi_pct',
      key: 'roi_pct',
      width: 90,
      sorter: (a, b) => a.roi_pct - b.roi_pct,
      render: (val) => (
        <span className={val > 0 ? 'text-green-600' : 'text-red-500'}>
          {val.toFixed(2)}%
        </span>
      ),
    },
    {
      title: '净利润(USDT)',
      dataIndex: 'net_profit_usd',
      key: 'net_profit_usd',
      width: 130,
      sorter: (a, b) => a.net_profit_usd - b.net_profit_usd,
      defaultSortOrder: 'descend',
      fixed: 'right',
      render: (val) => (
        <span className="font-bold text-green-600">
          +${val.toFixed(2)}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">完整套利机会列表</h1>
        <p className="text-gray-500 mt-1">查看、筛选和导出所有识别到的套利机会</p>
      </div>

      {/* 统计概览 */}
      <Card size="small">
        <Row gutter={24}>
          <Col span={6}>
            <Statistic 
              title="筛选后机会数" 
              value={stats.total} 
              suffix="次" 
              valueStyle={{ color: '#1890ff' }}
            />
          </Col>
          <Col span={6}>
            <Statistic 
              title="潜在总利润" 
              value={stats.totalProfit} 
              precision={2}
              prefix="$"
              valueStyle={{ color: '#52c41a' }}
            />
          </Col>
          <Col span={6}>
            <Statistic 
              title="单笔最大利润" 
              value={stats.maxProfit} 
              precision={2}
              prefix="$"
              valueStyle={{ color: '#fa8c16' }}
            />
          </Col>
          <Col span={6}>
            <Statistic 
              title="平均ROI" 
              value={stats.avgRoi} 
              precision={4}
              suffix="%"
              valueStyle={{ color: '#722ed1' }}
            />
          </Col>
        </Row>
      </Card>

      {/* 筛选控制栏 */}
      <Card size="small">
        <Space wrap size="middle">
          <Space>
            <span className="text-gray-600">最小净利润:</span>
            <InputNumber
              value={minProfit}
              onChange={(val) => setMinProfit(val || 0)}
              min={0}
              step={5}
              addonAfter="USDT"
              style={{ width: 140 }}
            />
            <Button 
              type="primary" 
              onClick={loadData} 
              loading={loading}
              icon={<ReloadOutlined />}
            >
              查询
            </Button>
          </Space>

          <Space>
            <FilterOutlined className="text-gray-400" />
            <Select
              placeholder="按方向筛选"
              allowClear
              value={directionFilter}
              onChange={setDirectionFilter}
              style={{ width: 150 }}
              options={[
                { value: 'Buy_Uni_Sell_Bin', label: 'Uni → Bin' },
                { value: 'Buy_Bin_Sell_Uni', label: 'Bin → Uni' },
              ]}
            />
            <DatePicker.RangePicker
              value={dateRange}
              onChange={setDateRange}
              placeholder={['开始日期', '结束日期']}
            />
          </Space>

          <Button 
            icon={<DownloadOutlined />} 
            onClick={exportCSV}
          >
            导出 CSV
          </Button>
        </Space>
      </Card>

      {/* 数据表格 */}
      <Card 
        size="small" 
        bodyStyle={{ padding: 0 }}
      >
        <Table
          columns={columns}
          dataSource={filteredData}
          loading={loading}
          pagination={{
            defaultPageSize: 50,
            showSizeChanger: true,
            pageSizeOptions: ['20', '50', '100', '200'],
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
            showQuickJumper: true,
          }}
          scroll={{ x: 1600 }}
          size="small"
          bordered
          sticky
        />
      </Card>
    </div>
  );
};

export default OpportunitiesPage;

