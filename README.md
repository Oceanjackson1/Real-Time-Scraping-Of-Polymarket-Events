# Polymarket 实时市场数据爬取工具

实时抓取 [Polymarket](https://polymarket.com) 预测市场的活跃事件数据，在终端以仪表盘形式展示，并支持导出 CSV / JSON 文件。

## 功能

- 自动分页抓取所有活跃市场事件（通过 Polymarket Gamma API）
- 终端实时仪表盘，每 30 秒自动刷新
- 按分类聚合展示（Politics、Sports、Crypto、Finance 等）
- 显示每个事件的成交额、24h 成交额、市场数量、最热门结果及概率
- 生成可直接访问的 Polymarket 链接
- 支持导出 CSV 和 JSON 文件
- 支持按分类筛选
- 失败自动重试 + 指数退避

## 样本数据（2026-02-25 实测）

| 指标 | 数值 |
|------|------|
| 活跃事件总数 | 5,000 |
| 子市场总数 | 36,796 |
| 总成交额 | $5.11B |
| 分类数量 | 48 |
| 单次抓取耗时 | ~10s |

### 主要分类分布

| 分类 | 事件数 | 总成交额 | 24h 成交额 |
|------|--------|---------|-----------|
| Politics | 1,145 | $3,084.7M | $64.4M |
| Sports | 2,041 | $1,351.1M | $67.8M |
| Crypto | 1,108 | $299.9M | $20.9M |
| Culture | 167 | $134.5M | $3.4M |
| Finance | 223 | $89.1M | $2.2M |
| World | 36 | $53.3M | $1.2M |
| AI | 45 | $32.0M | $588.1K |
| Science | 42 | $22.1M | $298.0K |

### 成交额 TOP 5 事件

| 事件 | 分类 | 成交额 | 链接 |
|------|------|--------|------|
| Democratic Presidential Nominee 2028 | Politics | $710.6M | [链接](https://polymarket.com/event/democratic-presidential-nominee-2028) |
| Who will Trump nominate as Fed Chair? | Politics | $514.1M | [链接](https://polymarket.com/event/who-will-trump-nominate-as-fed-chair) |
| US strikes Iran by...? | Politics | $411.5M | [链接](https://polymarket.com/event/us-strikes-iran-by) |
| Republican Presidential Nominee 2028 | Politics | $326.6M | [链接](https://polymarket.com/event/republican-presidential-nominee-2028) |
| 2026 NBA Champion | Sports | $278.3M | [链接](https://polymarket.com/event/2026-nba-champion) |

## 安装

```bash
# 克隆项目
git clone <repo-url>
cd Real-Time-Scraping-Of-Polymarket-Events

# 安装依赖（仅需 requests 和 rich）
pip install -r requirements.txt
```

### 环境要求

- Python 3.7+
- 无需 API Key，Polymarket Gamma API 为公开接口

## 使用方式

### 实时仪表盘（默认每 30 秒刷新）

```bash
python main.py
```

终端将显示：
- 顶部摘要面板：总事件数、总市场数、总成交额、抓取耗时
- 分类汇总表：各分类的事件数和成交额
- 主事件表：按 24h 成交额排序，含标题、分类、成交额、概率、链接

按 `Ctrl+C` 优雅退出。

### 自定义刷新间隔

```bash
python main.py --interval 10    # 每 10 秒刷新
python main.py --interval 60    # 每 60 秒刷新
```

### 仪表盘 + 持续导出文件

```bash
python main.py --export
```

每次刷新时自动在 `exports/` 目录下生成带时间戳的 CSV 和 JSON 文件。

### 单次抓取并导出（无仪表盘）

```bash
python main.py --export-once
```

抓取一次数据后导出文件并退出，适合定时任务 (cron) 场景。

### 按分类筛选

```bash
python main.py --category Politics    # 只看政治类
python main.py --category Crypto      # 只看加密货币类
python main.py --category Sports      # 只看体育类
```

### 组合使用

```bash
python main.py --interval 10 --export --category Sports
```

## 项目结构

```
.
├── main.py              # 入口文件：CLI 参数解析、刷新循环、信号处理
├── config.py            # 配置常量：API 地址、刷新间隔、分页参数
├── models.py            # 数据模型：Tag, Market, Event, ScraperSnapshot
├── api_client.py        # API 客户端：分页请求、重试机制、限流控制
├── data_processor.py    # 数据处理：JSON 解析、分类判定、聚合统计
├── display.py           # 终端展示：Rich 仪表盘、彩色表格、实时刷新
├── exporter.py          # 数据导出：CSV / JSON 文件写入
├── requirements.txt     # Python 依赖
├── exports/             # 导出文件目录（运行时自动创建）
└── scraper.log          # 运行日志
```

## 数据流

```
Polymarket Gamma API
        │
        ▼
  api_client.py          GET /events?active=true&closed=false
  (分页请求, 重试)        按 24h 成交额降序, 每页 100 条
        │
        ▼
  data_processor.py      解析 JSON → 数据模型
  (解析, 分类, 聚合)      分类判定 → 聚合统计 → ScraperSnapshot
        │
        ├──────────────────────┐
        ▼                      ▼
   display.py             exporter.py
   (Rich 终端仪表盘)       (CSV / JSON 文件)
```

## API 说明

本工具使用 Polymarket 的 **Gamma API**（公开接口，无需认证）：

- **Base URL**: `https://gamma-api.polymarket.com`
- **主要端点**: `GET /events` — 获取事件列表，支持以下参数：
  - `active` — 是否活跃
  - `closed` — 是否已关闭
  - `order` — 排序字段（如 `volume24hr`）
  - `ascending` — 升序/降序
  - `limit` / `offset` — 分页参数
- **速率限制**: 500 次/10 秒（本工具请求间隔 50ms，远低于限制）

## 导出文件格式

### CSV 字段

| 字段 | 说明 |
|------|------|
| event_id | 事件 ID |
| title | 事件标题 |
| category | 分类 |
| tags | 所有标签（分号分隔） |
| num_markets | 子市场数量 |
| total_volume | 总成交额 (USD) |
| volume_24hr | 24 小时成交额 (USD) |
| liquidity | 流动性 (USD) |
| top_market_question | 最热门子市场问题 |
| top_outcome | 领先结果 |
| top_price | 领先结果概率 |
| polymarket_url | Polymarket 链接 |
| scraped_at | 抓取时间 (UTC) |

### JSON 结构

```json
{
  "scraped_at": "2026-02-25 04:25:51 UTC",
  "total_events": 5000,
  "total_markets": 36796,
  "total_volume": 5112070444.67,
  "categories": {
    "Politics": [ ... ],
    "Sports": [ ... ]
  },
  "events": [
    {
      "id": "114242",
      "title": "US strikes Iran by...?",
      "category": "Politics",
      "volume": 411268786.80,
      "volume_24hr": 22982076.74,
      "markets": [ ... ],
      "polymarket_url": "https://polymarket.com/event/us-strikes-iran-by"
    }
  ]
}
```

## 配置

编辑 `config.py` 可调整以下参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `REFRESH_INTERVAL_SECONDS` | 30 | 刷新间隔（秒） |
| `API_PAGE_LIMIT` | 100 | 每页请求条数 |
| `MAX_PAGES` | 50 | 最大分页数（安全上限） |
| `REQUEST_DELAY_SECONDS` | 0.05 | 分页请求间隔（秒） |
| `EXPORT_DIR` | exports | 导出文件目录 |

## 许可证

MIT
