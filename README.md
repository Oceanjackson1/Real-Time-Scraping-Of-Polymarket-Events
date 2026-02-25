# Polymarket Real-Time Event Scraper

实时抓取 Polymarket 预测市场的全部活跃事件数据，在终端以仪表盘形式展示，并支持导出 CSV / JSON / Excel 文件。

基于 Polymarket 公开的 **Gamma API**，无需 API Key，开箱即用。

---

## 功能特性

- **全量抓取** — 自动分页获取所有活跃事件（每页 100 条，最多 5,000 条）
- **实时仪表盘** — 基于 Rich 的终端 UI，每 30 秒自动刷新
- **分类聚合** — 自动识别 Politics、Sports、Crypto、Finance 等 12+ 分类
- **预言机识别** — 自动区分 UMA 和 Chainlink 预言机，从市场描述中提取 Chainlink 数据源链接
- **数据丰富** — 展示成交额、24h 成交额、市场数量、最热门结果及概率
- **链接生成** — 每个事件附带可直接访问的 Polymarket 链接和预言机 Polygonscan 链接
- **多格式导出** — 支持 CSV、JSON、Excel（.xlsx）三种格式，Excel 含 4 个工作表
- **事件去重** — 基于 `event.id` 自动去重，确保每个事件唯一
- **交易量聚合** — 事件交易量由所有子市场交易量求和计算，保证数据准确性
- **分类筛选** — 命令行指定分类，只看你关心的市场
- **稳定可靠** — 请求失败自动重试（最多 3 次，指数退避），优雅退出

---

## 实测数据（2026-02-25）

| 指标 | 数值 |
|------|------|
| 活跃事件总数 | 4,515 |
| 子市场总数 | 35,388 |
| 总成交额 | $5.10B |
| 24h 成交额 | $177.5M |
| 分类数量 | 48 |
| 预言机类型 | 2（UMA / Chainlink） |
| 单次抓取耗时 | ~10s |

### 主要分类分布

| 分类 | 事件数 | 总成交额 | 24h 成交额 |
|------|--------|---------|-----------|
| Politics | 1,072 | $3,096.9M | $69.9M |
| Sports | 1,792 | $1,326.8M | $71.4M |
| Crypto | 955 | $306.6M | $26.8M |
| Culture | 167 | $134.9M | $3.2M |
| Finance | 226 | $89.4M | $2.4M |
| World | 37 | $53.4M | $721.3K |
| AI | 42 | $31.1M | $619.4K |
| Science | 40 | $20.6M | $436.0K |

### 预言机使用分布

| 预言机 | 事件数 | 事件占比 | 子市场数 | 交易量 | 交易量占比 |
|--------|--------|---------|---------|--------|-----------|
| UMA | 3,929 | 87.0% | 34,802 | $5,101.6M | 99.99% |
| Chainlink | 586 | 13.0% | 586 | $359.6K | 0.01% |

> **注**: Chainlink 事件均为加密资产（BTC/ETH/SOL/XRP）的短时价格预测盘口，时间窗口通常为 5 分钟 ~ 4 小时。因采集快照仅能捕获当前活跃窗口的交易量，其交易量数据存在系统性低估，不代表 Chainlink 预言机在 Polymarket 上的真实交易规模。

---

## 支持的数据字段

### Event（事件级字段）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | `str` | 事件唯一 ID | `"114242"` |
| `title` | `str` | 事件标题 | `"Democratic Presidential Nominee 2028"` |
| `slug` | `str` | URL 路径标识 | `"democratic-presidential-nominee-2028"` |
| `volume` | `float` | 总交易量 (USD)，= Σ 子市场交易量 | `710600000.0` |
| `volume_24hr` | `float` | 24 小时交易量 (USD)，= Σ 子市场 24h 交易量 | `1250000.0` |
| `liquidity` | `float` | 总流动性 (USD)，= Σ 子市场流动性 | `3500000.0` |
| `active` | `bool` | 是否活跃 | `true` |
| `closed` | `bool` | 是否已关闭 | `false` |
| `tags` | `List[Tag]` | 标签列表 | `[{"label": "Politics"}, ...]` |
| `markets` | `List[Market]` | 子市场列表 | *(见 Market 字段)* |
| `polymarket_url` | `str` | Polymarket 事件链接 | `"https://polymarket.com/event/..."` |
| `category` | `str` | 自动判定的分类 | `"Politics"` |
| `start_date` | `str \| None` | 事件开始时间 (ISO 8601) | `"2026-01-15T00:00:00Z"` |
| `end_date` | `str \| None` | 事件结束时间 (ISO 8601) | `"2028-11-05T00:00:00Z"` |
| `description` | `str` | 事件盘口背景描述 | `"This market will resolve..."` |
| `created_at` | `str \| None` | 事件创建时间 (ISO 8601) | `"2025-06-10T12:00:00Z"` |

### Market（子市场级字段）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | `str` | 子市场唯一 ID | `"0x1234..."` |
| `question` | `str` | 子市场问题 | `"Will Trump win?"` |
| `slug` | `str` | URL 路径标识 | `"will-trump-win"` |
| `outcomes` | `List[str]` | 结果选项 | `["Yes", "No"]` |
| `outcome_prices` | `List[str]` | 各结果当前价格/概率 | `["0.65", "0.35"]` |
| `volume` | `float` | 子市场交易量 (USD) | `50000000.0` |
| `volume_24hr` | `float` | 24 小时交易量 (USD) | `120000.0` |
| `liquidity` | `float` | 流动性 (USD) | `800000.0` |
| `active` | `bool` | 是否活跃 | `true` |
| `closed` | `bool` | 是否已关闭 | `false` |
| `end_date` | `str \| None` | 子市场结束时间 | `"2026-03-01T00:00:00Z"` |
| `polymarket_url` | `str` | Polymarket 子市场链接 | `"https://polymarket.com/event/..."` |
| `description` | `str` | 子市场裁决规则描述 | `"This market will resolve to..."` |
| `resolved_by` | `str \| None` | 预言机合约地址 | `"0x6507..."` |
| `oracle_type` | `str` | 预言机类型 | `"UMA"` / `"Chainlink"` |
| `oracle_link` | `str` | 预言机链接 | `"https://polygonscan.com/address/..."` 或 `"https://data.chain.link/..."` |
| `uma_bond` | `float \| None` | UMA 保证金 | `500.0` |
| `uma_reward` | `float \| None` | UMA 奖励 | `5.0` |
| `created_at` | `str \| None` | 子市场创建时间 | `"2025-06-10T12:00:00Z"` |

### Tag（标签字段）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | `str` | 标签 ID | `"123"` |
| `label` | `str` | 标签名称 | `"Politics"` |
| `slug` | `str` | 标签路径标识 | `"politics"` |

### ScraperSnapshot（快照级字段）

| 字段 | 类型 | 说明 |
|------|------|------|
| `timestamp` | `str` | 抓取时间 (UTC) |
| `events` | `List[Event]` | 全部事件列表 |
| `total_events` | `int` | 去重后事件总数 |
| `total_markets` | `int` | 子市场总数 |
| `total_volume` | `float` | 总交易量 (USD) |
| `categories` | `Dict[str, List[Event]]` | 按分类聚合的事件 |
| `fetch_duration_seconds` | `float` | 抓取耗时（秒） |

### 预言机识别规则

| 判定条件 | 预言机类型 | Oracle Link |
|---------|-----------|-------------|
| API 字段 `umaBond` 不为 `null` | **UMA** | `https://polygonscan.com/address/{resolvedBy}` |
| `umaBond` 为 `null`，且市场描述中匹配到 `data.chain.link` URL | **Chainlink** | 从描述中正则提取的 Chainlink 数据源链接 |

---

## 快速开始

### 环境要求

- Python 3.7+
- 无需 API Key（Gamma API 为公开接口）

### 安装

```bash
git clone https://github.com/Oceanjackson1/Real-Time-Scraping-Of-Polymarket-Events.git
cd Real-Time-Scraping-Of-Polymarket-Events
pip install -r requirements.txt
```

依赖包：

| 包 | 版本 | 用途 |
|----|------|------|
| requests | >= 2.31.0 | HTTP 请求 |
| rich | >= 13.7.0 | 终端 UI 渲染 |
| openpyxl | >= 3.1.0 | Excel 文件读写 |

### 运行

```bash
# 启动实时仪表盘
python main.py

# 单次抓取并导出 CSV + JSON + Excel
python main.py --export-once

# 仅导出 Excel
python main.py --export-excel
```

终端仪表盘包含三个区域：

- **顶部摘要面板** — 总事件数、总市场数、总成交额、抓取耗时、更新时间
- **分类汇总表** — 各分类的事件数、总成交额、24h 成交额
- **主事件表** — 按 24h 成交额降序，含标题、分类、市场数、成交额、领先概率、预言机类型、链接

按 `Ctrl+C` 优雅退出。

---

## 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--interval N` | 设置刷新间隔（秒），默认 30 | `python main.py --interval 10` |
| `--export` | 每次刷新时自动导出 CSV + JSON | `python main.py --export` |
| `--export-once` | 抓取一次并导出 CSV + JSON + Excel 后退出 | `python main.py --export-once` |
| `--export-excel` | 抓取一次并导出 Excel 后退出 | `python main.py --export-excel` |
| `--category NAME` | 按分类筛选事件 | `python main.py --category Politics` |

参数可组合使用：

```bash
# 每 10 秒刷新，只看体育类，同时导出 CSV/JSON
python main.py --interval 10 --export --category Sports

# 每次刷新同时导出 Excel
python main.py --export --export-excel

# 单次抓取加密货币类事件并导出全部格式
python main.py --export-once --category Crypto
```

---

## 导出格式

导出文件自动保存到 `exports/` 目录，文件名带时间戳（如 `polymarket_events_20260225_081133.csv`），不同时间的导出互不覆盖。

### CSV 字段

| 字段 | 说明 |
|------|------|
| `event_id` | 事件 ID |
| `title` | 事件标题 |
| `category` | 分类 |
| `tags` | 所有标签（分号分隔） |
| `num_markets` | 子市场数量 |
| `total_volume` | 总成交额 (USD) |
| `volume_24hr` | 24 小时成交额 (USD) |
| `liquidity` | 流动性 (USD) |
| `description` | 事件盘口背景 |
| `created_at` | 创建时间 (ISO 8601) |
| `oracle_type` | 预言机类型（UMA / Chainlink） |
| `oracle_link` | 预言机链接 |
| `resolved_by` | 预言机合约地址 |
| `top_market_question` | 最热门子市场问题 |
| `top_outcome` | 领先结果 |
| `top_price` | 领先结果概率 |
| `polymarket_url` | Polymarket 链接 |
| `scraped_at` | 抓取时间 (UTC) |

### JSON 结构

```json
{
  "scraped_at": "2026-02-25 08:11:33 UTC",
  "total_events": 4515,
  "total_markets": 35388,
  "total_volume": 5102008441.65,
  "fetch_duration_seconds": 10.5,
  "categories": {
    "Politics": ["..."],
    "Sports": ["..."]
  },
  "events": [
    {
      "id": "114242",
      "title": "US strikes Iran by...?",
      "category": "Politics",
      "description": "This market will resolve to ...",
      "volume": 411268786.80,
      "volume_24hr": 22982076.74,
      "markets": [
        {
          "question": "US strikes Iran by February 28, 2026?",
          "resolved_by": "0x6507...",
          "oracle_type": "UMA",
          "oracle_link": "https://polygonscan.com/address/0x6507...",
          "uma_bond": 500.0,
          "uma_reward": 5.0
        }
      ],
      "polymarket_url": "https://polymarket.com/event/us-strikes-iran-by"
    }
  ]
}
```

### Excel 工作表结构

Excel 文件（`.xlsx`）包含 **4 个工作表**：

#### Sheet 1: 事件明细（以采集时间戳命名）

按交易量降序排列，每个事件一行：

| 列 | 说明 |
|----|------|
| Event Name | 事件标题 |
| Event Link | Polymarket 事件链接 |
| Volume (USD) | 总交易量（= Σ 子市场交易量） |
| End Date | 事件结束时间 |
| Created At | 事件创建时间 |
| Rules | 裁决规则（取自交易量最大的子市场描述） |
| Background | 事件盘口背景描述 |
| Oracle Link | 预言机链接（Polygonscan 或 Chainlink 数据源） |
| Oracle Type | 预言机类型（UMA / Chainlink） |

#### Sheet 2: Category_Summary

| 列 | 说明 |
|----|------|
| Category | 分类名称 |
| Events | 事件数 |
| Markets | 子市场数 |
| Total Volume (USD) | 总交易量 |
| 24h Volume (USD) | 24 小时交易量 |
| Liquidity (USD) | 总流动性 |

#### Sheet 3: Oracle_Summary

| 列 | 说明 |
|----|------|
| Oracle Type | 预言机类型 |
| Events | 事件数 |
| Markets | 子市场数 |
| Total Volume (USD) | 总交易量 |
| 24h Volume (USD) | 24 小时交易量 |

含合计行（Total）汇总全部预言机数据。

#### Sheet 4: Scrape_Info

| 字段 | 说明 |
|------|------|
| Scraped At | 采集时间 (UTC) |
| Total Events | 事件总数 |
| Total Markets | 子市场总数 |
| Total Volume (USD) | 总交易量 |
| Total Categories | 分类数 |
| Oracle Types | 预言机类型数 |
| Fetch Duration (seconds) | 抓取耗时 |

---

## 项目结构

```
Real-Time-Scraping-Of-Polymarket-Events/
├── main.py              # 程序入口：CLI 参数解析、刷新循环、信号处理
├── config.py            # 配置常量：API 地址、刷新间隔、分页参数
├── models.py            # 数据模型：Tag / Market / Event / ScraperSnapshot
├── api_client.py        # API 客户端：分页请求、重试机制、限流控制
├── data_processor.py    # 数据处理：JSON 解析、分类判定、预言机识别、事件去重、交易量聚合
├── display.py           # 终端展示：Rich 仪表盘、彩色表格、实时刷新
├── exporter.py          # 数据导出：CSV / JSON / Excel 文件写入
├── requirements.txt     # Python 依赖
├── .gitignore           # Git 忽略规则
├── exports/             # 导出文件目录（运行时自动创建）
└── scraper.log          # 运行日志（运行时自动生成）
```

---

## 架构设计

### 数据流

```
  Polymarket Gamma API
  GET /events?active=true&closed=false&order=volume24hr
         │
         │  分页请求（每页 100 条，最多 50 页）
         │  请求间隔 50ms，失败自动重试（3 次，指数退避）
         ▼
  ┌─ api_client.py ──────────────────────────┐
  │  GammaAPIClient.fetch_all_active_events() │
  │  → 返回 List[Dict]（原始 JSON）            │
  └──────────────┬───────────────────────────┘
                 │
                 ▼
  ┌─ data_processor.py ─────────────────────────────────┐
  │  DataProcessor.build_snapshot()                      │
  │  ├── parse_event() → Event 对象                      │
  │  │   ├── parse_market() → Market 对象                │
  │  │   │   └── 预言机识别：UMA (umaBond) / Chainlink   │
  │  │   │       (正则匹配 data.chain.link URL)          │
  │  │   ├── determine_category() → 分类判定             │
  │  │   └── 交易量聚合：volume = Σ(子市场 volume)        │
  │  ├── 事件去重：基于 event.id 去重                     │
  │  ├── categorize_events() → 按分类聚合                │
  │  └── 统计总量 → ScraperSnapshot                      │
  └────────────┬────────────────────────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
  ┌─ display.py ┐  ┌─ exporter.py ───────────────────────┐
  │  Dashboard  │  │  Exporter                            │
  │  .render()  │  │  .export_csv()   → CSV 文件           │
  │  Rich Live  │  │  .export_json()  → JSON 文件          │
  │  终端仪表盘  │  │  .export_excel() → Excel 文件（4 表） │
  └─────────────┘  │  存入 exports/ 目录                   │
                   └──────────────────────────────────────┘
```

### 数据模型

```
ScraperSnapshot
├── timestamp: str                 # 抓取时间 (UTC)
├── total_events: int              # 去重后事件总数
├── total_markets: int             # 子市场总数
├── total_volume: float            # 总成交额 (USD)
├── fetch_duration_seconds: float  # 抓取耗时
├── categories: Dict[str, List]    # 按分类聚合的事件
└── events: List[Event]
     ├── id, title, slug
     ├── volume                    # = Σ(子市场 volume)
     ├── volume_24hr               # = Σ(子市场 volume_24hr)
     ├── liquidity                 # = Σ(子市场 liquidity)
     ├── category: str             # 自动判定的分类
     ├── description: str          # 事件盘口背景
     ├── created_at: str           # 事件创建时间
     ├── start_date / end_date     # 起止时间
     ├── tags: List[Tag]
     │    └── id, label, slug
     ├── markets: List[Market]
     │    ├── question, outcomes, outcome_prices
     │    ├── volume, volume_24hr, liquidity
     │    ├── description          # 裁决规则
     │    ├── resolved_by          # 预言机合约地址
     │    ├── oracle_type          # "UMA" / "Chainlink"
     │    ├── oracle_link          # Polygonscan 或 Chainlink 链接
     │    └── uma_bond, uma_reward # UMA 参数
     └── polymarket_url: str
```

---

## API 说明

本工具使用 Polymarket 的 **Gamma API**（公开接口，无需认证）：

| 项目 | 说明 |
|------|------|
| Base URL | `https://gamma-api.polymarket.com` |
| 主要端点 | `GET /events` |
| 认证方式 | 无需认证 |
| 速率限制 | 500 次 / 10 秒 |

### 请求参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `active` | `true` | 仅获取活跃事件 |
| `closed` | `false` | 排除已关闭事件 |
| `order` | `volume24hr` | 按 24h 成交额排序 |
| `ascending` | `false` | 降序排列 |
| `limit` | `100` | 每页条数 |
| `offset` | `0, 100, 200...` | 分页偏移 |

---

## 配置

编辑 `config.py` 可调整以下参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `REFRESH_INTERVAL_SECONDS` | `30` | 仪表盘刷新间隔（秒），可通过 `--interval` 覆盖 |
| `API_PAGE_LIMIT` | `100` | 每页请求条数 |
| `MAX_PAGES` | `50` | 最大分页数（安全上限，即最多 5,000 条） |
| `REQUEST_DELAY_SECONDS` | `0.05` | 分页请求间隔（秒），防止触发速率限制 |
| `EXPORT_DIR` | `exports` | 导出文件保存目录 |

---

## 常见问题

**Q: 抓取的事件数量是否有上限？**

默认最多抓取 `MAX_PAGES × API_PAGE_LIMIT = 50 × 100 = 5,000` 条事件。如需更多，可在 `config.py` 中调大 `MAX_PAGES`。

**Q: 请求过于频繁会被限流吗？**

Gamma API 的速率限制为 500 次/10 秒。本工具每次分页请求间隔 50ms（即每秒最多 20 次），远低于限制。如遇 429 响应，工具会自动等待并重试。

**Q: 预言机类型是如何判断的？**

通过两条规则判定：(1) 如果 API 返回的 `umaBond` 字段不为空，则判定为 UMA 预言机；(2) 如果 `umaBond` 为空，系统会用正则表达式从市场描述中查找 `data.chain.link` 链接，如匹配则判定为 Chainlink 预言机。

**Q: 为什么 Chainlink 的交易量远低于 UMA？**

Chainlink 事件均为加密资产的短时价格预测盘口（时间窗口 5 分钟 ~ 4 小时），系统滚动创建。API 快照只能捕获当前活跃窗口的交易量，而 UMA 事件的交易量是整个生命周期（可能数月）的累积值。两者在统计口径上不具可比性。

**Q: 事件交易量是怎么计算的？**

事件交易量 = 该事件下所有子市场的 `volumeNum` 字段求和，而非直接使用 API 返回的事件级 `volume` 字段，后者可能不准确或为 `null`。

**Q: 导出文件会覆盖吗？**

不会。每次导出的文件名都包含时间戳（精确到秒），不同时间的导出互不覆盖。

---

## 许可证

MIT
