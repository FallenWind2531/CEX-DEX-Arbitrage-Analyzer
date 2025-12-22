# **1.介绍**

##### 1.1 目的

本文档旨在详细定义“区块链非原子套利交易识别系统”的功能性及非功能性需求。

##### 1.2 文档约定

+ 所有需求将按功能模块进行组织。
+ “系统”一词特指“区块链非原子套利交易识别系统”的Web应用。
+ "CEX" 指中心化交易所 (Centralized Exchange)，特指 Binance。
+ "DEX" 指去中心化交易所 (Decentralized Exchange)，特指 Uniswap V3。

##### 1.3 预期读者

本文档的预期读者包括：

+ **项目开发人员**：作为实现系统功能的技术蓝图和依据。
+ **项目经理**：用于理解项目范围、跟踪进度和进行决策。
+ **测试人员**：用于设计测试用例和验收标准。
+ **项目小组（用户）**：用于确认需求是否准确、完整地反映了项目目标。

##### 1.4 项目范围

本项目旨在分析和识别历史数据中的非原子套利机会，而非执行实际交易。

**系统功能范围 (In-Scope):**

1. **数据可视化**：系统应能获取并以可视化图表（例如价格曲线）展示 2025年9月1日 至 9月30日 期间，Uniswap V3 (USDT/ETH池) 与 Binance (USDT/ETH交易对) 的历史成交数据。
2. **价格对比**：系统应提供功能，对两者的价格变化进行可视化对比。
3. **套利识别**：系统需要分析上述数据，探索并实现一种或多种方法（例如启发式规则、统计分析等）来识别潜在的非原子套利行为。
4. **盈利计算**：系统应能根据识别到的套利行为，计算其潜在的获利金额，并以 USDT 为单位显示。

**系统功能范围外 (Out-of-Scope):**

+ 系统**不**执行任何真实的、自动化的套利交易。
+ 系统**不**提供实时数据分析，主要集中在指定的历史数据回测。
+ 系统**不**涉及除 Uniswap V3 和 Binance 之外的其他交易所。
+ 系统**不**涉及除 USDT/ETH 之外的其他交易对。

##### 1.5 参考文献

1. Heimbach L, Pahari V, Schertenleib E. Non-atomic arbitrage in decentralized finance[C]//2024 IEEE Symposium on Security and Privacy (SP). IEEE, 2024: 3866-3884.
2. Wu F, Sui D, Thiery T, et al. Measuring CEX-DEX Extracted Value and Searcher Profitability: The Darkest of the MEV Dark Forest[J]. arXiv preprint arXiv:2507.13023, 2025.



# **2. 总体描述**

##### 2.1 <font style="color:rgb(0, 0, 0);">产品视角</font>

<font style="color:rgba(0, 0, 0, 0.85);">本产品是一款</font><font style="color:rgb(0, 0, 0) !important;">聚焦 Uniswap V3（DEX 代表）与 Binance（CEX 代表）USDT/ETH 交易对的非原子套利识别专用 Web 应用</font><font style="color:rgba(0, 0, 0, 0.85);">。其核心能力涵盖历史交易数据可视化与套利行为分析，旨在填补 DEX-CEX 跨平台非原子套利分析工具的空白，为用户提供专业、高效的数据分析支持。</font>

##### 2.2 <font style="color:rgb(0, 0, 0);">产品功能</font>

###### <font style="color:rgb(0, 0, 0);">2.2.1 历史数据展示与可视化模块</font>

<font style="color:rgb(0, 0, 0);">该模块专注于 Uniswap V3 与 Binance USDT/ETH 交易数据的呈现与对比，包含以下子功能：</font>

1. **<font style="color:rgb(0, 0, 0) !important;">历史交易数据查询</font>**
   - <font style="color:rgb(0, 0, 0);">Uniswap V3 数据：展示 2025 年 9 月 1 日 - 30 日指定池的交易明细，包括交易时间、成交价格等字段</font>
   - <font style="color:rgb(0, 0, 0);">Binance 数据：展示同期 USDT/ETH 现货交易的明细，包括交易时间、成交价格等字段</font>
   - <font style="color:rgb(0, 0, 0);">数据筛选：支持按时间段筛选数据，提升查询效率。</font>
2. **<font style="color:rgb(0, 0, 0) !important;">价格对比可视化</font>**
   - <font style="color:rgb(0, 0, 0);">双轴折线图：同步展示 Uniswap V3 与 Binance 的 USDT/ETH 价格趋势，直观呈现价格差异。</font>

###### <font style="color:rgb(0, 0, 0);">2.2.2 非原子套利识别与获利计算模块</font>

<font style="color:rgb(0, 0, 0);">该模块通过跨平台交易数据分析识别套利行为，并计算潜在获利，包含以下子功能：</font>

1. **<font style="color:rgb(0, 0, 0) !important;">套利识别方法</font>**
   - <font style="color:rgb(0, 0, 0);">启发式规则分析：设定如 “价差≥0.5%”“10 分钟内跨平台交易” 等规则，筛选潜在套利交易。</font>
   - <font style="color:rgb(0, 0, 0);">统计分析：通过计算价格相关性、交易时间序列匹配度，识别异常交易集群</font>
2. **<font style="color:rgb(0, 0, 0) !important;">获利计算</font>**
   - <font style="color:rgb(0, 0, 0);">计算公式：潜在获利 = 高价格平台卖出金额 - 低价格平台买入金额 - 交易手续费</font>
   - <font style="color:rgb(0, 0, 0);">用户输入：支持用户输入最小套利利润、时间区间，影响套利识别统计结果。</font>
   - <font style="color:rgb(0, 0, 0);">结果展示：按获利金额排序展示识别出的套利交易，包含交易时间、价差、手续费、净获利等关键信息，展示潜在获利金额、套利机会数、平均利润等统计数据。</font>

##### 2.3 <font style="color:rgb(0, 0, 0);">用户类别及特征</font>

| **使用者** | **主要特征**                                                 | **备注**                                                     |
| :--------: | ------------------------------------------------------------ | ------------------------------------------------------------ |
|    用户    | 可以查看 <font style="color:rgb(0, 0, 0) !important;">Uniswap V3 和 Binance 的可视化历史成交数据</font> | 默认展示2025年9月1日至9月31日期间数据，可以选择任意时间段    |
|            | 可以查看任意时间段内可能的非原子套利行为统计结果             | 包括潜在获利金额、套利机会数、平均利润，可以设定部分套利分析参数 |


##### 2.4 运行环境

###### 2.4.1 客户端环境

浏览器：<font style="color:rgba(0, 0, 0, 0.85);">支持主流现代浏览器如 Chrome、Firefox、Edge。</font>

<font style="color:rgba(0, 0, 0, 0.85);">网络：稳定联网，需具备访问国际网络的能力。</font>

###### <font style="color:rgb(0, 0, 0);">2.4.2 服务器端环境</font>

<font style="color:rgba(0, 0, 0, 0.85) !important;">操作系统：Linux Ubuntu 22.04</font>

<font style="color:rgba(0, 0, 0, 0.85);">数据库：使用MySQL 存储结构化交易数据。</font>

<font style="color:rgba(0, 0, 0, 0.85);">网络：稳定联网，需具备访问国际网络的能力。</font>

##### 2.5 <font style="color:rgb(0, 0, 0);">设计与实现约束</font>

###### <font style="color:rgb(0, 0, 0);">2.5.1 数据约束</font>

1. **<font style="color:rgb(0, 0, 0) !important;">数据源限制</font>**<font style="color:rgb(0, 0, 0);">：Uniswap V3 数据仅从指定合约地址获取，不支持其他 USDT/ETH 池数据；Binance 数据依赖官方 Spot API</font>
2. **<font style="color:rgb(0, 0, 0) !important;">数据完整性依赖</font>**<font style="color:rgb(0, 0, 0);">：需从数据源 API 获取完整交易数据。</font>
3. **<font style="color:rgb(0, 0, 0) !important;">数据存储周期</font>**<font style="color:rgb(0, 0, 0);">：必须保留 2025 年 9 月 1 日 - 30 日的完整数据，历史数据仅允许管理员手动清理，用户无删除权限。</font>

###### <font style="color:rgb(0, 0, 0);">2.5.2 技术约束</font>

1. **<font style="color:rgb(0, 0, 0) !important;">性能限制</font>**<font style="color:rgb(0, 0, 0);">：</font>
   - <font style="color:rgb(0, 0, 0);">数据加载：默认展示2025 年 9 月历史数据首次加载需在 3 秒内完成；</font>
   - <font style="color:rgb(0, 0, 0);">可视化响应：图表交互（如选择时间段）响应时间≤1 秒；</font>
   - <font style="color:rgba(0, 0, 0, 0.85);">套利分析：一个月内的套利识别计算需在 3 秒内完成。</font>
2. **<font style="color:rgb(0, 0, 0) !important;">并发支持</font>**<font style="color:rgb(0, 0, 0);">：可以支持至少 10 名用户同时在线操作。</font>

##### 2.6 <font style="color:rgb(0, 0, 0);">用户文档</font>

<font style="color:rgb(0, 0, 0);">产品交付时将提供两类用户文档，助力用户快速上手并解决使用过程中的问题，具体如下表所示：</font>

| **<font style="color:rgb(0, 0, 0) !important;">文档类型</font>** | **<font style="color:rgb(0, 0, 0) !important;">文档名称</font>** | **<font style="color:rgb(0, 0, 0) !important;">目标用户</font>** | **<font style="color:rgb(0, 0, 0) !important;">核心内容</font>** |
| :----------------------------------------------------------: | :----------------------------------------------------------: | :----------------------------------------------------------: | ------------------------------------------------------------ |
| <font style="color:rgba(0, 0, 0, 0.85) !important;">指导类文档</font> | <font style="color:rgba(0, 0, 0, 0.85) !important;">《用户操作指南》</font> | <font style="color:rgba(0, 0, 0, 0.85) !important;">所有用户类别</font> | <font style="color:rgba(0, 0, 0, 0.85) !important;">步骤化讲解核心操作</font> |
| <font style="color:rgba(0, 0, 0, 0.85) !important;">描述类文档</font> | <font style="color:rgba(0, 0, 0, 0.85) !important;">《数据源说明文档》</font> | <font style="color:rgba(0, 0, 0, 0.85) !important;">所有用户类别</font> | <font style="color:rgba(0, 0, 0, 0.85) !important;">说明 Uniswap V3 合约地址、各 API 数据源范围、数据字段含义</font> |



# **3. 系统功能**

##### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.1 数据可视化与对比功能</font>

###### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.1.1 功能描述与优先级</font>

<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">该功能为跨平台价格展示与对比的核心模块，支持用户直观观察 Uniswap V3 与 Binance 两大交易所间 USDT/ETH 的价格差异，是后续套利分析的基础支撑。</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">优先级：高</font>**

###### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.1.2 刺激 / 响应序列</font>

1. **<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">刺激</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：用户访问系统首页或选中 “价格对比” 模块</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">响应</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：系统自动加载并展示默认时间范围（2025 年 9 月 1 日 - 9 月 30 日）的价格对比图表</font>
2. **<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">刺激</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：用户通过时间选择器调整查询时间段</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">响应</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：系统在 1 秒内刷新图表，展示选中时间段的价格数据</font>
3. **<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">刺激</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：用户点击图例隐藏 / 显示某一平台的价格曲线</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">响应</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：系统无需页面刷新，即时更新图表显示状态</font>

###### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.1.3 功能性需求</font>

1. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">支持以双轴折线图形式，同步展示 Uniswap V3 与 Binance 的 USDT/ETH 小时级成交价格</font>
2. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">提供时间范围选择器（起止日期），支持用户自定义查询时间段</font>
3. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">实现图例交互功能：点击可切换不同交易所价格曲线的显示 / 隐藏状态</font>
4. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">保证数据一致性：双轴图表时间轴需精确到毫秒级对齐</font>
5. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">在图表下方展示选中时间段内的关键数据指标（最高价格、最低价格、平均价格）</font>

##### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.2 非原子套利识别功能</font>

###### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.2.1 功能描述与优先级</font>

<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">该功能为核心业务模块，通过启发式规则与统计分析相结合的方式，分析历史交易数据，识别潜在的非原子套利行为。</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">优先级：高</font>**

###### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.2.2 刺激 / 响应序列</font>

1. **<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">刺激</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：用户进入 “套利分析” 模块并点击 “开始分析” 按钮</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">响应</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：系统显示分析进度指示器，启动数据计算流程</font>
2. **<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">刺激</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：用户在分析前设置自定义参数（最小利润阈值、价差比例）</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">响应</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：系统应用参数筛选套利机会，在 15 秒内完成分析</font>
3. **<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">刺激</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：分析流程完成</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">响应</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：系统展示套利机会列表与统计汇总卡片</font>

##### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.2.3 功能性需求</font>

1. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">实现双重识别机制：</font>
   - <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">启发式规则：当跨平台价差≥0.5% 且交易时间间隔≤10 分钟时，识别为潜在套利机会</font>
   - <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">统计分析：通过价格相关性计算、交易时间序列匹配度分析，识别异常交易集群</font>
2. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">支持用户自定义分析参数：</font>
   - <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">最小利润阈值（默认值：50 USDT）</font>
   - <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">价差比例阈值（默认值：0.5%）</font>
   - <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">自定义时间范围（与可视化模块时间范围保持一致）</font>
3. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">输出套利机会详情，包含交易时间、交易所组合（买入 / 卖出平台）、价差金额、交易量、净利润等字段</font>
4. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">提供结果排序功能：支持按净利润（降序 / 升序）、交易时间（最新 / 最早）排序</font>

##### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.3 套利利润计算功能</font>

###### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.3.1 功能描述与优先级</font>

<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">该功能为套利识别的辅助模块，针对已识别的套利机会，综合成本因素量化潜在利润，确保计算结果贴近实际场景。</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">优先级：中</font>**

###### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.3.2 刺激 / 响应序列</font>

1. **<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">刺激</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：系统完成套利识别分析</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">响应</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：自动为每一条识别出的套利机会计算净利润</font>
2. **<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">刺激</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：用户点击某条套利机会的 “查看详情” 按钮</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">响应</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：展示利润计算明细（买入金额、卖出金额、手续费、Gas 费、净利润）</font>

###### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.3.3 功能性需求</font>

1. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">采用公式计算净利润：</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">净利润 =（卖出价格 × 交易量）-（买入价格 × 交易量）- 手续费 - Gas 费（仅 Uniswap 适用）</font>**
2. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">支持手续费动态配置：</font>
   - <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">Binance 手续费：固定为交易金额的 0.1%</font>
   - <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">Uniswap 手续费：固定为交易金额的 0.3%（与 USDT/ETH 交易池设置一致）</font>
3. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">Gas 费计算规则：根据交易时间段的历史平均 Gas 价格换算（单位：USDT）</font>
4. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">展示利润统计指标：总潜在利润、套利机会数量、单机会平均利润、单次最大利润</font>
5. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">保证计算准确性：模拟利润与实际理论值误差不超过 10%</font>

##### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.4 数据管理功能</font>

###### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.4.1 功能描述与优先级</font>

<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">该功能为底层支撑模块，负责交易数据的获取、清洗与存储，保障上层功能所需数据的可用性与完整性。</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">优先级：中</font>**

###### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.4.2 刺激 / 响应序列</font>

1. **<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">刺激</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：系统启动或触发定时任务</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">响应</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：自动从 Uniswap V3（The Graph API）、Binance（Spot API）拉取最新交易数据</font>
2. **<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">刺激</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：数据拉取完成</font>**<font style="color:rgb(0, 0, 0) !important;background-color:rgba(0, 0, 0, 0);">响应</font>**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">：系统执行数据清洗流程，将数据增量存储至 MySQL 数据库</font>

###### <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">3.4.3 功能性需求</font>

1. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">实现定时数据同步：每小时拉取最新小时级交易数据，执行增量存储（仅新增数据入库）</font>
2. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">保障数据完整性：两大平台有效数据获取率不低于 95%</font>
3. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">实现数据清洗规则：</font>
   - <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">剔除重复交易记录（通过交易 ID + 时间戳判断）</font>
   - <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">过滤异常数据（价格≤0 或交易量≤0 的记录）</font>
   - <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">统一数据格式（时间戳转为 UTC+0 时区，价格精度保留 6 位小数）</font>
4. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">保留 2025 年 9 月完整历史数据，支持管理员手动备份，禁止用户删除操作</font>
5. <font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">提供数据异常提示：数据拉取失败时显示错误信息，并自动重试 3 次（重试间隔：5 分钟）</font>

<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);"></font>



# **4. 外部接口**

##### 4.1 用户接口

| 项目     | 信息                                                         |
| -------- | ------------------------------------------------------------ |
| 界面类型 | Web浏览器界面                                                |
| 主要界面 | 1. 数据可视化界面   2. 套利机会展示界面   3. 利润统计界面   4. 系统配置界面   5. 模拟参数设置界面 |
| 交互方式 | 鼠标点击、键盘输入、下拉选择、时间范围滑块                   |
| 显示要求 | 支持常见屏幕分辨率(1024×768及以上)                           |
| 响应时间 | 页面切换 ≤3秒，数据查询 ≤5秒                                 |
| 用户角色 | 普通用户                                                     |


##### 4.2 硬件接口

###### 服务器硬件接口需求

| 项目       | 信息                                  |
| ---------- | ------------------------------------- |
| 服务器设备 | 本地服务器或云服务器（阿里云/腾讯云） |
| 处理器     | Intel i5 及以上或同等性能CPU          |
| 内存       | 4G 及以上                             |
| 存储       | 500G 及以上                           |
| 网卡       | 速率 100Mbps 及以上                   |
| 备份       | 本地备份或云备份                      |


###### 客户端硬件接口需求

| 项目     | 信息                               |
| -------- | ---------------------------------- |
| 处理器   | Intel i3 或 AMD A4 及以上          |
| 内存     | 2G 及以上                          |
| 存储     | 任意主流存储介质                   |
| 网卡     | 速率 10Mbps 及以上                 |
| 显示设备 | 支持分辨率 1024×768 及以上的显示器 |


##### 4.3 软件接口

| 项目         | 信息                                                         |
| ------------ | ------------------------------------------------------------ |
| 服务器端软件 | 1. 操作系统：Ubuntu 20.04 LTS   2. Web服务器：Nginx   3. 后端框架：Python FastAPI   4. 数据库：MySQL 8.0   5. 数据处理库：Pandas, NumPy |
| 客户端软件   | 1. 操作系统：Windows 10/Linux/macOS   2. 浏览器：Chrome/Firefox/Safari/Edge最新版本   3. 前端框架：React 17+   4. 图表库：Recharts或类似可视化库 |


##### 4,4 通信接口

| 项目         | 信息                                                         |
| ------------ | ------------------------------------------------------------ |
| 网络协议     | HTTP/1.1、HTTPS、TCP/IP                                      |
| 数据传输格式 | JSON、XML                                                    |
| 通信安全     | SSL/TLS加密传输                                              |
| 接口标准     | RESTful API                                                  |
| 数据传输速率 | 100Mbps及以上                                                |
| 外部系统接口 | 1. Uniswap V3 API接口 - 获取去中心化交易所数据   2. Binance API接口 - 获取中心化交易所数据   3. 前端与后端API通信接口 |



# **5. 其他非功能性需求**

###### 5.1 性能需求  Performance Requirements  

1. 系统应保证运行稳定，避免崩溃；
2. 系统应支持至少100人的并发访问；
3. 系统首次启动时，需要分别从两平台完成数据获取与预处理，这个过程应在1分钟以内完成；
4. 数据已被缓存时，Web应用主界面的仪表盘应在3s以内完成渲染；
5. 用户进行任何操作时，系统应及时作出反应，反应时间在1s以内；
6. 用户触发非原子套利识别时，系统应在15s以内给出结果。

###### 5.2 安全性需求 Safety Requirements

1. 系统应能检测出各种非正常情况，如无法连接数据库等，并给出对应提示；
2. 在无法获取某一平台数据时，系统应给出对应提示，并在一段时间后重试；
3. 系统管理员应每两个月备份一次数据；
4. 出现事故导致数据丢失后，系统应能在24小时内完成数据恢复；
5. 系统出现崩溃后，应在24小时内恢复正常运行。

###### 5.3 安全需求 Security Requirements

1. 用于访问外部数据源的API密钥，必须仅储存在服务端的环境变量中；
2. 客户端与服务器之间，以及服务器与外部API之间的通信都必须被加密；
3. 只有系统管理员有权查看及修改底层数据库数据；
4. 当流量过大时，限制流量防止恶意访问；
5. 系统应该能检测到恶意操作；
6. 当检测到恶意重复操作时，系统应提出警告并在一段时间内不允许操作。

###### 5.4 软件质量属性 Software Quality Attributes

1. 可用性：系统保证在早上6点到晚上12点之间可用；
2. 可维护性：系统运行时需要保存运行日志，便于维护人员分析；
3. 兼容性：系统需要在主流浏览器上可以正常浏览和使用；
4. 易用性：系统的仪表盘应有良好的可视化交互功能，用户可以查看任意时间点的价格与价差，并且识别出的非原子套利结果应该具有高度的可读性；
5. 可靠性：如果外部API的返回结果异常，系统应能有效进行处理，避免后续处理崩溃；
6. 可拓展性： 系统在后端设计和前端设计上尽可能地在满足所有需求的同时，应考虑系统的后续发展，便于扩充需求。



# **6. 附录**

###### a. 术语表

| <font style="color:rgb(27, 28, 29);">术语 / 缩写</font> | <font style="color:rgb(27, 28, 29);">定义</font>             |
| ------------------------------------------------------- | ------------------------------------------------------------ |
| <font style="color:rgb(27, 28, 29);">非原子套利</font>  | <font style="color:rgb(27, 28, 29);">指套利交易的“买入”和“卖出”操作不在同一个区块或同一笔事务中完成。套利者需先在一个市场成交，再到另一个市场成交，期间存在价格波动和交易失败的风险。这是本项目的核心研究对象。</font> |
| <font style="color:rgb(27, 28, 29);">CEX</font>         | <font style="color:rgb(27, 28, 29);">中心化交易所。指由一个中心化实体运营的传统交易所。在本项目中，特指 Binance (币安)。</font> |
| <font style="color:rgb(27, 28, 29);">DEX</font>         | <font style="color:rgb(27, 28, 29);">去中心化交易所。指基于区块链智能合约运行的交易所。在本项目中，特指 Uniswap V3。</font> |
| <font style="color:rgb(27, 28, 29);">USDT/ETH 池</font> | <font style="color:rgb(27, 28, 29);">在 Uniswap V3 中，用户为 USDT 和 ETH 这两种资产提供流动性的智能合约。</font> |
| <font style="color:rgb(27, 28, 29);">API</font>         | <font style="color:rgb(27, 28, 29);">应用程序编程接口。本项目用于从 Binance、The Graph、Etherscan 等服务获取交易数据的技术手段。</font> |
| <font style="color:rgb(27, 28, 29);">启发式规则</font>  | <font style="color:rgb(27, 28, 29);">指用于“探索和识别”非原子套利行为的、基于经验或直觉建立的简化算法或规则。例如：“当CEX和DEX价差在T时间内超过X%时，标记为一次潜在套利机会”。</font> |
| <font style="color:rgb(27, 28, 29);">MEV</font>         | <font style="color:rgb(27, 28, 29);">最大可提取价值。指区块生产者（矿工/验证者）通过在其生产的区块中任意包含、排除或重排交易顺序所能获取的利润。非原子套利是MEV的一种形式。</font> |


###### b. 模型

用例图和数据流图

![](https://cdn.nlark.com/yuque/0/2025/png/38855972/1763366002695-1f290a86-0e8a-4e1f-b61e-9d06af1397fc.png)![](https://cdn.nlark.com/yuque/0/2025/png/38855972/1763367736328-18dfb875-af15-4f58-b523-67d027d5f549.png)
