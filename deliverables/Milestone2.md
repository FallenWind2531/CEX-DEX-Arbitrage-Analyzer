# **愿景与范围**

### 一、愿景（Vision）

本项目的愿景是打造一个 **面向区块链交易分析的智能识别与可视化平台**，通过整合去中心化交易所（DEX）与中心化交易所（CEX）的异构数据，实现**非原子套利行为的自动识别与潜在利润量化**，从而为区块链数据研究者、量化交易者及风控分析员提供**透明、高效、可验证的数据分析支持工具**。

### 二、范围（Scope）

本项目的研究与开发范围将严格限定在以下几个方向内：

1. **数据范围**：
   - 聚焦于 **Uniswap V3（DEX）** 与 **Binance（CEX）** 两个平台；
   - 仅分析 **USDT/ETH** 交易对的历史数据与实时价格数据；
   - 数据时间范围限定在特定周期（例如 2025 年 9 月及其动态扩展区间）。
2. **功能范围**：
   - **数据获取与整合**：从 Uniswap 与 Binance 的 API 获取交易数据，完成时间戳对齐、字段清洗与格式标准化；
   - **价格趋势可视化**：通过 Web 前端实现双折线对比图，支持时间区间选择与交互展示；
   - **套利行为识别**：实现启发式与统计分析相结合的算法，识别潜在的非原子套利行为；
   - **利润量化与报告生成**：计算潜在套利利润，展示总利润、机会次数、平均收益等核心指标。
3. **系统范围**：
   - **前端模块**：基于 React 框架开发用户界面，重点实现数据展示与交互操作；
   - **后端模块**：基于 Python 的fastapi实现数据处理、算法计算与 API 服务；
   - **数据库模块**：采用 MySQL 存储清洗后的交易数据与分析结果。
4. **非目标范围（Out of Scope）**：
   - 不涉及真实资金交易或套利执行，仅限于数据分析与模拟计算；
   - 不支持除 USDT/ETH 之外的交易对或除 Binance、Uniswap 之外的交易平台；
   - 不提供金融建议或投资决策支持功能。



# **功能路线图**

### **<font style="color:rgb(0, 0, 0) !important;">阶段一：MVP - 核心数据可视化 （冬二周完成）</font>**

#### <font style="color:rgb(0, 0, 0);">「数据采集层」</font>

1. **<font style="color:rgb(0, 0, 0) !important;">Uniswap V3 数据接入</font>**
   - <font style="color:rgb(0, 0, 0);">步骤：</font>
     * <font style="color:rgb(0, 0, 0);">调研 The Graph API 文档，编写针对合约</font>`<font style="color:rgb(0, 0, 0);">0x11b815efB8f581194ae79006d24E0d814B7697F6</font>`<font style="color:rgb(0, 0, 0);">的查询脚本，拉取 2025 年 9 月逐笔交易数据（价格、交易量、时间戳）。</font>
     * <font style="color:rgb(0, 0, 0);">验证数据完整性：检查是否覆盖 9 月 1 日 - 9 月 30 日全周期，每小时数据无缺失。</font>
   - <font style="color:rgb(0, 0, 0);">里程碑：Uniswap 数据拉取完成，本地存储为 CSV 格式可查。</font>
2. **<font style="color:rgb(0, 0, 0) !important;">Binance 数据接入</font>**
   - <font style="color:rgb(0, 0, 0);">步骤：</font>
     * <font style="color:rgb(0, 0, 0);">对接 Binance Spot API（参考</font>`<font style="color:rgb(0, 0, 0);">binance-spot-api-docs</font>`<font style="color:rgb(0, 0, 0);">），编写脚本拉取 2025 年 9 月 USDT/ETH 的 K 线（小时级）与成交明细数据。</font>
     * <font style="color:rgb(0, 0, 0);">格式对齐：将 Binance 数据字段与 Uniswap 统一（如时间戳格式、价格精度）。</font>
   - <font style="color:rgb(0, 0, 0);">里程碑：Binance 数据拉取完成，与 Uniswap 数据格式兼容。</font>
3. **<font style="color:rgb(0, 0, 0) !important;">数据清洗与存储</font>**
   - <font style="color:rgb(0, 0, 0);">步骤：</font>
     * <font style="color:rgb(0, 0, 0);">设计 MySQL 数据库表结构（字段包含</font>`<font style="color:rgb(0, 0, 0);">交易对、价格、时间、交易所、交易量</font>`<font style="color:rgb(0, 0, 0);">等）。</font>
     * <font style="color:rgb(0, 0, 0);">编写脚本，清洗重复、空值数据，将数据批量入库。</font>
   - <font style="color:rgb(0, 0, 0);">里程碑：数据入库完成，验证数据总量与原始数据一致。</font>

#### <font style="color:rgb(0, 0, 0);">「前端交互层」</font>

1. **<font style="color:rgb(0, 0, 0) !important;">前端框架搭建</font>**
   - <font style="color:rgb(0, 0, 0);">步骤：</font>
     * <font style="color:rgb(0, 0, 0);">选用 React 框架初始化项目，配置路由（首页为</font>`<font style="color:rgb(0, 0, 0);">价格对比页</font>`<font style="color:rgb(0, 0, 0);">）。</font>
     * <font style="color:rgb(0, 0, 0);">集成组件库，搭建页面基础布局（头部、侧边栏、内容区）。</font>
   - <font style="color:rgb(0, 0, 0);">里程碑：前端项目可本地启动，页面骨架加载正常。</font>
2. **<font style="color:rgb(0, 0, 0) !important;">可视化组件开发</font>**
   - <font style="color:rgb(0, 0, 0);">步骤：</font>
     * <font style="color:rgb(0, 0, 0);">开发双折线图组件（分别渲染 Uniswap 和 Binance 的价格走势）。</font>
     * <font style="color:rgb(0, 0, 0);">联调后端接口：从数据库查询 9 月小时级价格数据，驱动图表渲染。</font>
   - <font style="color:rgb(0, 0, 0);">里程碑：折线图成功展示两大平台价格对比，时间轴与数据粒度对齐。</font>
3. **<font style="color:rgb(0, 0, 0) !important;">交互功能优化</font>**
   - <font style="color:rgb(0, 0, 0);">步骤：</font>
     * <font style="color:rgb(0, 0, 0);">开发时间区间选择器（默认选中 9 月 1 日 - 9 月 30 日），支持用户手动调整。</font>
     * <font style="color:rgb(0, 0, 0);">添加图例交互（点击隐藏 / 显示某平台价格曲线）。</font>
   - <font style="color:rgb(0, 0, 0);">里程碑：MVP 版本发布，用户可在 Web 端查看交互式价格对比图表。</font>

### **<font style="color:rgb(0, 0, 0) !important;">阶段二：v1.0 - 核心套利分析 （冬四周完成）</font>**

#### <font style="color:rgb(0, 0, 0);">「算法开发层」</font>

1. **<font style="color:rgb(0, 0, 0) !important;">套利算法分析</font>**
   - <font style="color:rgb(0, 0, 0);">步骤：</font>
     * <font style="color:rgba(0, 0, 0, 0.85);">研究非原子套利相关文献与市场实践，梳理现有识别方法的核心逻辑，结合项目数据特征提炼关键影响因素。</font>
     * <font style="color:rgb(0, 0, 0);">结合启发式规则与统计分析等方法，实现完整的套利算法</font>
   - <font style="color:rgb(0, 0, 0);">里程碑：得到合理的套利算法</font>
2. **<font style="color:rgb(0, 0, 0) !important;">后端分析程序开发</font>**
   - <font style="color:rgb(0, 0, 0);">步骤：</font>
     * <font style="color:rgb(0, 0, 0);">编写程序，从数据库提取历史数据，识别套利机会。</font>
     * <font style="color:rgb(0, 0, 0);">计算每笔套利净利润：</font>`<font style="color:rgb(0, 0, 0);">(卖出价-买入价)×交易量 - 手续费 - Gas费</font>`<font style="color:rgb(0, 0, 0);">（以 USDT 计）。</font>
   - <font style="color:rgb(0, 0, 0);">里程碑：程序运行成功，输出多笔模拟套利结果，利润计算逻辑自洽。</font>
3. **<font style="color:rgb(0, 0, 0) !important;">算法验证</font>**
   - <font style="color:rgb(0, 0, 0);">步骤：</font>
     * <font style="color:rgb(0, 0, 0);">选取多笔已知套利案例，验证算法识别准确率。</font>
     * <font style="color:rgb(0, 0, 0);">调整参数，对比识别效果，确定最优阈值。</font>
   - <font style="color:rgb(0, 0, 0);">里程碑：核心算法验证通过，识别准确率≥80%。</font>

#### <font style="color:rgb(0, 0, 0);">「前端交互层」</font>

1. **<font style="color:rgb(0, 0, 0) !important;">分析参数配置界面</font>**
   - <font style="color:rgb(0, 0, 0);">步骤：</font>
     * <font style="color:rgb(0, 0, 0);">开发表单组件，支持用户输入</font>`<font style="color:rgb(0, 0, 0);">利润阈值（默认50 USDT）</font>`<font style="color:rgb(0, 0, 0);">、</font>`<font style="color:rgb(0, 0, 0);">时间区间</font>`<font style="color:rgb(0, 0, 0);">。</font>
     * <font style="color:rgb(0, 0, 0);">联调后端接口，将用户参数传入分析脚本。</font>
   - <font style="color:rgb(0, 0, 0);">里程碑：参数界面与后端联调成功，可触发分析请求。</font>
2. **<font style="color:rgb(0, 0, 0) !important;">分析结果展示</font>**
   - <font style="color:rgb(0, 0, 0);">步骤：</font>
     * <font style="color:rgb(0, 0, 0);">开发表格组件：展示套利机会列表（包含</font>`<font style="color:rgb(0, 0, 0);">时间、价格差、净利润、交易对</font>`<font style="color:rgb(0, 0, 0);">）。</font>
     * <font style="color:rgb(0, 0, 0);">开发统计卡片：展示</font>`<font style="color:rgb(0, 0, 0);">总潜在利润、套利机会数、平均利润</font>`<font style="color:rgb(0, 0, 0);">等摘要数据。</font>
   - <font style="color:rgb(0, 0, 0);">里程碑：v1.0 版本发布，用户可自定义参数并查看完整分析报告。</font>

### **<font style="color:rgb(0, 0, 0) !important;">阶段三：v1.1 - 动态分析实现 （冬六周完成）</font>**

#### <font style="color:rgb(0, 0, 0);">「前端交互层」</font>

1. **<font style="color:rgb(0, 0, 0) !important;">时间范围扩展</font>**
   - <font style="color:rgb(0, 0, 0);">步骤：</font>
     * <font style="color:rgb(0, 0, 0);">前端：修改时间选择器为 “起止时间选择器”，支持任意时间区间（如 2025 年 10 月）。</font>
     * <font style="color:rgb(0, 0, 0);">后端：调整数据查询 SQL，适配动态时间范围的筛选逻辑。</font>
   - <font style="color:rgb(0, 0, 0);">里程碑：用户可选择任意时间范围进行价格对比与套利分析，数据查询无报错。</font>
2. **<font style="color:rgb(0, 0, 0) !important;">数据自动更新</font>**
   - <font style="color:rgb(0, 0, 0);">步骤：</font>
     * <font style="color:rgb(0, 0, 0);">编写定时任务脚本，每小时自动拉取 Uniswap 和 Binance 的最新交易数据。</font>
     * <font style="color:rgb(0, 0, 0);">实现增量入库：仅更新新增数据，避免重复存储。</font>
   - <font style="color:rgb(0, 0, 0);">里程碑：数据库每小时自动增量更新，最新数据延迟≤1 小时。</font>



