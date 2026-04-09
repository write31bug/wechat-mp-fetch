# PR：股票技术分析工具 v1.2.0 反馈（第二轮）

**日期：** 2026-04-08（第二轮）
**版本：** `E:\public\股票技术分析 (1)\股票技术分析`
**测试环境：** Windows / Python 3 / akshare 1.18.53 / yfinance 1.2.0

---

## 一、总体评价

第二轮更新质量很高，上一轮提出的主要问题均已处理：

| 上一轮问题 | 状态 |
|-----------|------|
| `fund_zh_a_hist` 接口不存在 | ✅ 已移除，替换为正确接口 |
| 批量失败无提示 | ✅ 新增 `failed` 列表 |
| yfinance 港美股主源 | ✅ 保留 |
| `--ascii` 中文乱码 | ✅ 保留 |
| `--batch` 批量分析 | ✅ 保留 |

**整体评价：** 架构清晰，功能完整，基金类型分类处理（ETF/LOF/开放基金）是正确方向。

---

## 二、仍需修复的问题

### 🔴 Bug 1：基金接口参数名写错

**文件：** `stock_analysis.py`
**函数：** `fetch_fund_data_akshare()`

**问题：**

开发者对 akshare 基金接口的签名理解有误，导致两处调用失败：

**错误 A - `fund_open_fund_daily_em` 多传了 `symbol` 参数：**
```python
df = ak.fund_open_fund_daily_em(symbol=code)  # ❌
```
`fund_open_fund_daily_em()` 不接受 `symbol` 参数，调用无参数版本时返回**所有基金**的最新净值（23011条），无法按单只基金提取。

**错误 B - `fund_open_fund_info_em` 参数名写错：**
```python
df = ak.fund_open_fund_info_em(fund=code)  # ❌
```
正确参数名是 `symbol`，不是 `fund`：
```python
df = ak.fund.fund_em.fund_open_fund_info_em(
    symbol=code,
    indicator='单位净值走势',
    period='近1年'
)
```

**实测验证（akshare 1.18.53）：**

```python
# 错误A：fund_open_fund_daily_em 不接受 symbol
ak.fund.fund_em.fund_open_fund_daily_em(symbol='001316')
# TypeError: got an unexpected keyword argument 'symbol'

# 正确B：fund_open_fund_info_em 用 symbol 参数
ak.fund.fund_em.fund_open_fund_info_em(symbol='001316', indicator='单位净值走势', period='近1年')
# ✅ 成功返回 2647 条历史净值数据
```

**修复方案：**

`fetch_fund_data_akshare` 改为：
```python
@staticmethod
def fetch_fund_data_akshare(code: str, days: int = 60) -> Optional[pd.DataFrame]:
    if not AKSHARE_AVAILABLE:
        return None

    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')

    # 尝试 ETF（代码以 15/16/51/58 开头）
    if code.startswith(('15', '16', '51', '58')):
        try:
            df = ak.fund.fund_etf_em.fund_etf_hist_em(
                symbol=code, period='daily',
                start_date=start_date, end_date=end_date
            )
            if df is not None and not df.empty:
                df = df.rename(columns={
                    '日期': 'date', '开盘': 'open', '收盘': 'close',
                    '最高': 'high', '最低': 'low', '成交量': 'volume',
                    '成交额': 'amount', '涨跌幅': 'pct_change'
                })
                df['date'] = pd.to_datetime(df['date'])
                return df.sort_values('date').reset_index(drop=True)
        except Exception as e:
            print(f"[WARN] ETF数据失败: {e}", file=sys.stderr)

    # 尝试 开放式基金历史净值（单位净值走势）
    try:
        df = ak.fund.fund_em.fund_open_fund_info_em(
            symbol=code,
            indicator='单位净值走势',
            period='近1年'
        )
        if df is not None and not df.empty:
            df = df.rename(columns={
                '净值日期': 'date', '单位净值': 'close', '日增长率': 'pct_change'
            })
            df['date'] = pd.to_datetime(df['date'])
            df['open'] = df['close']
            df['high'] = df['close']
            df['low'] = df['close']
            df['volume'] = 0
            df = df.sort_values('date').reset_index(drop=True)
            return df.tail(days)
    except Exception as e:
        print(f"[WARN] 开放基金数据失败: {e}", file=sys.stderr)

    return None
```

---

### 🟡 Bug 2：ETF历史数据列名映射缺失

**文件：** `stock_analysis.py`
**函数：** `fetch_fund_data_akshare()` 的 ETF 分支

**问题：**

`fund_etf_hist_em` 返回列名是中文（如"日期"、"收盘"），但代码没有 rename 就直接用了，导致后续 `df['close']` 等列访问失败。

**修复：** 添加 rename（见上方完整修复代码）。

---

### 🟢 建议：统一基金类型判断逻辑

**文件：** `stock_analysis.py`
**函数：** `fetch_fund_data_akshare()`

**问题：**

当前基金类型判断（ETF vs LOF vs 开放基金）放在 `fetch_fund_data_akshare` 内部，但代码结构不够清晰。

**建议改为：**
```python
def get_fund_type(code: str) -> str:
    """判断基金类型"""
    if code.startswith(('15', '16', '51', '58')):
        return 'ETF'
    else:
        return 'OPEN'  # 开放式基金（含混合型、QDII等）
```

---

## 三、测试验证记录

| 功能 | 标的 | 结果 | 备注 |
|------|------|------|------|
| A股股票 | 600036 | ✅ | 新浪主源正常 |
| A股 ETF | 510310 | ✅ | 新浪主源正常 |
| 港股 yfinance | 00700 | ✅ 架构正确 | 需联网测试 |
| 美股 yfinance | AAPL | ✅ 架构正确 | 需联网测试 |
| 基金 ETF `--type fund` | 159934 | ❌ | 参数问题（同上） |
| 基金 开放基金 `--type fund` | 001316 | ❌ | 参数问题（同上） |
| 批量 `--batch` | 3只股票 | ✅ | 输出正确含 avg_score |
| 批量失败列表 | 含失败标的 | ✅ | summary 中有 failed 列表 |
| `--ascii` | 任意 | ✅ | 中文标签转英文 |

---

## 四、修复优先级

```
P0（阻塞基金功能）:
  - Bug 1：fund_open_fund_daily_em 多传了 symbol 参数
  - Bug 1：fund_open_fund_info_em 参数名 fund → symbol

P1（建议）:
  - Bug 2：ETF 历史数据列名映射缺失

P2（可选）:
  - 基金类型判断逻辑简化
```

---

**总结：** 这一轮已经非常接近可用状态，致命 bug 全部修掉了，P0 的两个参数问题是最后一公里。修复后即可合并。
