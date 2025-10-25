# CEX-DEX-Arbitrage-Analyzer
A web application to analyze and identify non-atomic arbitrage opportunities between Uniswap V3 and Binance for the USDT/ETH pair.

本项目的文档管理主要在[语雀知识库](https://www.yuque.com/fallen-8rfie/hfw0rg)上进行管理。

## 仓库索引结构
本仓库索引结构如下：
```
/ (仓库根目录: CEX-DEX-Arbitrage-Analyzer/)
│
├── backend/                   # 后端应用
│   
│
├── frontend/                  # 前端应用
│   ├── public/                # 静态资源
│   └── src/                   # 前端源码
│
├── docs/                      # 存放技术文档和设计文档（Markdown）
│
├── process/                   # 进度管理
│   ├── meeting-minutes/       # 会议纪要 (按日期命名)
│   │   └── 2025-10-25-Kickoff.md（例）
│   └── snapshots/             # 线上会议截图 
│
├── deliverables/              # 存放每个里程碑的最终交付物 (PDF/ZIP)
│   ├── M1-Project-Proposal/   # Milestone 1 交付物
│   ├── M2-Vision-Scope/       # Milestone 2 交付物
│   └── ...                    # M3, M4, M5
│
├── .gitignore            
└── README.md                
```

## Git提交格式
为了统一提交信息，提高可读性，commit信息需符合以下格式：
```
<type>: <subject>
```
其中，`type`用于说明本次提交的“性质”，可用type如下：

- **feat**: 增加新功能 (feature)。
- **fix**: 修复了Bug。
- **docs**: 只修改了文档(指 docs/ 目录下的技术文档)。
- **style**: 修改代码格式。
- **test**: 增加或修改测试用例。
- **chore**: 日常事务，构建过程或辅助工具的变动（如修改 .gitignore，更新交付文件，添加会议纪要）。

`subject`用一句话简短描述本次提交的目的。

使用例：
```
feat: implement basic price visualization component

fix: ensure chart scales correctly on window resize

docs: update feature roadmap for M3

chore: upload M1 project proposal slides
```