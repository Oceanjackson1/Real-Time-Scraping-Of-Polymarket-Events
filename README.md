# Polymarket Real-Time Event Scraper

实时抓取 [Polymarket](https://polymarket.com) 预测市场的全部活跃事件数据，在终端以仪表盘形式展示，并支持导出 CSV / JSON 文件。

基于 Polymarket 公开的 **Gamma API**，无需 API Key，开箱即用。

---

## 功能特性

- **全量抓取** — 自动分页获取所有活跃事件（每页 100 条，最多 5,000 条）
- **实时仪表盘** — 基于 Rich 的终端 UI，每 30 秒自动刷新
- **分类聚合** — 自动识别 Politics、Sports、Crypto、Finance 等 12+ 分类
- **数据丰富** — 展示成交额、24h 成交额、市场数量、最热门结果及概率
- **链接生成** — 每个事件附带可直接访问的 Polymarket 链接
- **数据导出** — 支持 CSV 和 JSON 两种格式，带时间戳文件名
- **分类筛选** — 命令行指定分类，只看你关心的市场
- **稳定可靠** — 请求失败自动重试（最多 3 次，指数退避），优雅退出

## 实测数据（2026-02-25）

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

---

## 快速开始

### 环境要求

- Python 3.7+
- 无需 API Key（Gamma API 为公开接口）

### 安装

```bash
git clone https://github.com/your-username/Real-Time-Scraping-Of-Polymarket-Events.git
cd Real-Time-Scraping-Of-Polymarket-Events
pip install -r requirements.txt
```

依赖仅两个包：

| 包 | 版本 | 用途 |
|----|------|------|
| `requests` | >= 2.31.0 | HTTP 请求 |
| `rich` | >= 13.7.0 | 终端 UI 渲染 |

### 运行

```bash
python main.py
```

终端将显示实时仪表盘：
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
| `--export-once` | 抓取一次并导出后退出（无仪表盘） | `python main.py --export-once` |
| `--category NAME` | 按分类筛选事件 | `python main.py --category Politics` |

参数可组合使用：

```bash
# 每 10 秒刷新，只看体育类，同时导出
python main.py --interval 10 --export --category Sports

# 单次抓取加密货币类事件并导出
python main.py --export-once --category Crypto
```

---

## 项目结构

```
Real-Time-Scraping-Of-Polymarket-Events/
├── main.py              # 程序入口：CLI 参数解析、刷新循环、信号处理
├── config.py            # 配置常量：API 地址、刷新间隔、分页参数
├── models.py            # 数据模型：Tag / Market / Event / ScraperSnapshot
├── api_client.py        # API 客户端：分页请求、重试机制、限流控制
├── data_processor.py    # 数据处理：JSON 解析、分类判定、聚合统计
├── display.py           # 终端展示：Rich 仪表盘、彩色表格、实时刷新
├── exporter.py          # 数据导出：CSV / JSON 文件写入
├── requirements.txt     # Python 依赖
├── .gitignore           # Git 忽略规则
├── exports/             # 导出文件目录（运行时自动创建）
└── scraper.log          # 运行日志（运行时自动生成）
```

## 架构设计

### 模块职责

```
┌─────────────────────────────────────────────────────────────┐
│  main.py                                                    │
│  程序入口 / CLI 解析 / 刷新循环 / 信号处理                      │
└──────┬───────────────────┬──────────────────┬───────────────┘
       │                   │                  │
       ▼                   ▼                  ▼
┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│ api_client   │  │ data_processor │  │   display     │
│              │  │                │  │               │
│ GammaAPI     │  │ DataProcessor  │  │  Dashboard    │
│ Client       │→ │ .build_        │→ │  .render()    │
│ .fetch_all_  │  │  snapshot()    │  │               │
│  active_     │  │ .parse_event() │  │ build_header  │
│  events()    │  │ .parse_market()│  │ build_tables  │
│              │  │ .categorize_   │  │               │
│ 分页/重试/限流 │  │  events()      │  │ Rich 终端 UI  │
└──────────────┘  └───────┬────────┘  └───────────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │  exporter    │
                  │              │
                  │  Exporter    │
                  │ .export_csv()│
                  │ .export_json │
                  │              │
                  │ 带时间戳文件名 │
                  └──────────────┘
```

### 数据模型

```
ScraperSnapshot                    # 一次完整抓取的快照
├── timestamp: str                 # 抓取时间 (UTC)
├── total_events: int              # 事件总数
├── total_markets: int             # 子市场总数
├── total_volume: float            # 总成交额
├── fetch_duration_seconds: float  # 抓取耗时
├── categories: Dict[str, List]    # 按分类聚合的事件
└── events: List[Event]            # 全部事件列表
     ├── id, title, slug
     ├── volume, volume_24hr, liquidity
     ├── category: str             # 自动判定的分类
     ├── tags: List[Tag]           # 标签列表
     │    └── id, label, slug
     ├── markets: List[Market]     # 子市场列表
     │    ├── question, outcomes, outcome_prices
     │    ├── volume, volume_24hr, liquidity
     │    ├── resolved_by, oracle_type, oracle_link
     │    └── uma_bond, uma_reward
     └── polymarket_url: str       # Polymarket 事件链接
```

### 数据流

```
  Polymarket Gamma API
  GET /events?active=true&closed=false&order=volume24hr
         │
         │  分页请求（每页 100 条，最多 50 页）
         │  请求间隔 50ms，失败自动重试（3 次，指数退避）
         ▼
  ┌─ api_client.py ─────────────────────────┐
  │  GammaAPIClient.fetch_all_active_events()│
  │  → 返回 List[Dict]（原始 JSON）           │
  └──────────────┬──────────────────────────┘
                 │
                 ▼
  ┌─ data_processor.py ────────────────────┐
  │  DataProcessor.build_snapshot()         │
  │  ├── parse_event() → Event 对象         │
  │  │   ├── parse_market() → Market 对象   │
  │  │   └── determine_category() → 分类    │
  │  ├── categorize_events() → 按分类聚合   │
  │  └── 统计总量 → ScraperSnapshot         │
  └────────────┬───────────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
  ┌─ display.py ┐  ┌─ exporter.py ──────────────┐
  │  Dashboard  │  │  Exporter                   │
  │  .render()  │  │  .export_csv() → CSV 文件    │
  │  Rich Live  │  │  .export_json() → JSON 文件  │
  │  终端仪表盘  │  │  存入 exports/ 目录           │
  └─────────────┘  └─────────────────────────────┘
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
|------|------|------|
| `active` | `true` | 仅获取活跃事件 |
| `closed` | `false` | 排除已关闭事件 |
| `order` | `volume24hr` | 按 24h 成交额排序 |
| `ascending` | `false` | 降序排列 |
| `limit` | `100` | 每页条数 |
| `offset` | `0, 100, 200...` | 分页偏移 |

---

## 导出格式

导出文件自动保存到 `exports/` 目录，文件名带时间戳（如 `polymarket_events_20260225_042551.csv`）。

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
| `description` | 规则/盘口背景 |
| `created_at` | 创建时间（ISO 8601） |
| `oracle_type` | 预言机类型（UMA / Unknown） |
| `oracle_link` | 预言机 Polygonscan 链接 |
| `resolved_by` | 预言机合约地址 |
| `top_market_question` | 最热门子市场问题 |
| `top_outcome` | 领先结果 |
| `top_price` | 领先结果概率 |
| `polymarket_url` | Polymarket 链接 |
| `scraped_at` | 抓取时间 (UTC) |

### JSON 结构

```json
{
  "scraped_at": "2026-02-25 04:25:51 UTC",
  "total_events": 5000,
  "total_markets": 36796,
  "total_volume": 5112070444.67,
  "fetch_duration_seconds": 10.5,
  "categories": {
    "Politics": [ "..." ],
    "Sports": [ "..." ]
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
          "resolved_by": "0x65070BE91477460D8A7AeEb94ef92fe056C2f2A7",
          "oracle_type": "UMA",
          "oracle_link": "https://polygonscan.com/address/0x65070...",
          "uma_bond": 500.0,
          "uma_reward": 5.0
        }
      ],
      "polymarket_url": "https://polymarket.com/event/us-strikes-iran-by"
    }
  ]
}
```

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

默认最多抓取 `MAX_PAGES * API_PAGE_LIMIT = 50 * 100 = 5,000` 条事件。如需更多，可在 `config.py` 中调大 `MAX_PAGES`。

**Q: 请求过于频繁会被限流吗？**

Gamma API 的速率限制为 500 次/10 秒。本工具每次分页请求间隔 50ms（即每秒最多 20 次），远低于限制。如遇 429 响应，工具会自动等待并重试。

**Q: 支持哪些分类筛选？**

自动识别的分类包括：Politics, Crypto, Sports, Finance, Science, Entertainment, Business, Economy, AI, Technology, Culture, World 等。实际分类取决于 Polymarket 为事件设置的标签。

**Q: 导出文件会覆盖吗？**

不会。每次导出的文件名都包含时间戳（精确到秒），不同时间的导出互不覆盖。

---

## 许可证

MIT
