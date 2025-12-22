**1. 进入backend目录**
`cd ./backend`

**2. 创建并激活虚拟环境**
建议使用独立的运行环境：
`python3 -m venv .venv`
`source .venv/bin/activate`


**3. 安装依赖**
下载项目所需的 Python 库：
`pip install -r requirements.txt`

**4. 准备数据**
如果想从头开始构建，需要参照ddoc/数据源说明文档.md内容获取原始数据并正确放置；如果想快速启动，只需要确保backend/data目录下包含正确的pkl缓存文件即可

**5. 启动程序**
执行启动命令：
`python main.py`

*   第一次运行时会自动下载数据，需要等待几分钟。
*   当屏幕显示 Uvicorn running on http://0.0.0.0:8000 时，表示启动成功。
*   在浏览器中访问 http://localhost:8000/docs 查看接口。
