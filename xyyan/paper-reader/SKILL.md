---
name: paper-reader
description: 医学文献精读技能。当用户说"精读文献"、"阅读这篇论文"、"帮我整理这篇文献"、"读这篇PDF"、"文献笔记"时触发。使用 pdfplumber 提取 PDF 文本，分析论文结构（背景、方法、结果、结论），提取关键机制通路和发现，生成结构化 markdown 笔记保存到 E:\xiaoyan\papers\ 目录。
---

# paper-reader 医学文献精读技能

## 工作流程

### Step 1: 提取 PDF 文本

使用 bundled script `scripts/extract_pdf.py` 提取全文：

```bash
python scripts/extract_pdf.py "<pdf_path>" "<output_txt_path>"
```

默认读取全部页面，可选加 `max_pages` 参数限制（如只读前10页做快速预览）。

**注意**: PDF 路径中若有中文，Python 直接调用可能有问题。先用以下 Python 单行命令获取文件列表中的正确路径：
```python
python -c "import os; files=os.listdir(r'E:\document'); [print(f'[{i}] {f}') for i,f in enumerate(sorted([f for f in files if f.endswith('.pdf')]))]"
```

### Step 2: 读取文本并分析

读取提取的 .txt 文件，判断论文类型：
- **综述 (Review)**: 通常无 methods 节，侧重综合论述
- **原始研究 (Original Article)**: 有明确 Methods/Results 结构
- **Meta分析**: 有检索策略、系统评价
- **Letter/Commentary**: 短文，简短评论

### Step 3: 生成结构化笔记

使用 `references/note_template.md` 作为模板，填充以下内容：

| 字段 | 说明 |
|------|------|
| `number` | 笔记编号，按读取顺序递增 |
| `title` | 中文标题（译） |
| `original_title` | 英文原标题 |
| `background` | 2-4句背景，说明研究领域的已知与未知 |
| `objective` | 1-2句，明确研究目的或科学问题 |
| `methods` | 研究设计、样本、模型、关键技术 |
| `results` | 核心发现（量化描述，非仅"显著"） |
| `mechanism_diagram` | 用文字/ASCII描述机制图 |
| `clinical_significance` | 临床意义和局限性 |
| `relevance` | 与脓毒症内皮损伤/凝血病课题的关联 |
| `open_questions` | 1-3个值得深究的问题 |

### Step 4: 保存笔记

笔记保存路径格式：
```
E:\xiaoyan\papers\笔记_{number:03d}_{简短中文标题}.md
```

同步保存原始文本：
```
E:\xiaoyan\papers\paper_{index}.txt
```

---

## 关键原则

1. **不转述结论**：忠实提取原文数据和表述，不添加未提及的内容
2. **机制优先**：与内皮损伤、凝血病相关的机制详细记录，临床描述可简略
3. **保留原文关键术语**：首次出现时附英文
4. **评估客观**：文献质量评估基于期刊、方法学、样本量综合判断，不因结论重要就打高分
5. **提出问题**：每篇至少留下1个值得在课题中探索的问题

---

## 快速预览模式

若只需快速了解一篇文献的核心结论，可用 `max_pages=3` 只读前3页（标题+摘要），节省 token。
