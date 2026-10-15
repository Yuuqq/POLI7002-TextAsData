# PR #2 third-pass review

Review of https://github.com/Yuuqq/POLI7002-TextAsData/pull/2 (`54c5533` on `jules-13003729469819640183-2cff2f98`).

`gh pr review --request-changes` returned 403 (`addPullRequestReview`: this token only has `metadata=read`). The same text is also a top-level comment: https://github.com/Yuuqq/POLI7002-TextAsData/pull/2#issuecomment-6196459534

This branch only records the review. It does not change course code and does not open another pull request.

---

## Third-pass review（Cursor/Grok 二审之后的 Jules 修复 PR）

**Verdict: request changes — not merge-ready.**

本 PR 相对二审是一次**方向正确、执行半成品**的修复：工作区里的明文 NYT key 和 `http://` 调用被拿掉了，`week2.py` / `week3.py` 的错归属也改对了。但交付物仍不可靠——同一份 `REVIEW.md` 现在描述的是**已经不存在**的代码状态；路径“可移植性”修成了空操作；运行时仍会把密钥打到 stdout。合进去会在 PR #1 的审查文档上再叠一层过期清单。

对照对象：Cursor/Grok 对 PR #1 的二次审查。

---

### 1. 二审必改项是否落地

| 二审要求 | 判定 | 说明 |
|---|---|---|
| `REVIEW.md` 打码明文 key，禁止再贴凭证 | **做到** | `api-key=<redacted>`。不要再引入任何一把明文 key |
| 纠正 `week3.py` HTTP / `week2.py` 路径与句柄的错归属 | **做到** | Avalon → `stemming.py`；未关闭文件 → `dictionaries.py`。核对过：`week2.py` 仍是 4 行 for 循环，`week3.py` 无 HTTP |
| 补上 HW2 第二把 key + 其余 `/Users/...`（含 `svm.R`） | **文档做到，代码也改了** | 三份 `Hu_*.py` 改为 `os.environ.get("NYT_API_KEY", "")`；名单里补了 `lexis.py` / `dictionaries.py` / `hw3/*` / `svm.R` |
| 按课程仓库重标定级（缺测试/DRY/lockfile 降为 LOW 或删除） | **未做** | 「Lack of Test Coverage」仍是 MEDIUM，套话未改 |
| 审查放 PR 正文，不要把有缺陷的 `REVIEW.md` 合进 `master` | **未做** | 仍在维护并准备合并这份文档 |
| 活密钥保持 CRITICAL；轮换已泄露 key | **半做** | 工作区已移除；git 历史仍有两把 key（`nyt_demo.py` 与 HW2）。`REVIEW.md` 写了 revoke，但本 PR 无法从历史上擦掉 |

Jules 比二审要求多走了一步：直接改源码，而不只改文档。这一点值得肯定。问题是**文档没有跟着代码更新**，而文档正是这条 PR 链的核心产物。

---

### 2. 正确性：源码改动

**密钥替换（部分正确）**  
`os.environ.get("NYT_API_KEY", "")` 比硬编码好，但空字符串默认值是错的。未设置环境变量时脚本仍会发请求，然后在 `response.json()` / `data["response"]["docs"]` 上炸，错误信息含糊。应 `key = os.environ.get("NYT_API_KEY")`，缺失则立刻 `raise` / `stop`。`.gitignore` 和 `README.md` 都没有提到 `NYT_API_KEY`。

**HTTPS（正确）**  
`api.nytimes.com` 与 `avalon.law.yale.edu` 改为 `https://` 没问题。不要把公开历史文本抓取和「query string 里传 key」写成同一档 HIGH——二审已经说过，本 PR 的 `REVIEW.md` 仍把它们捆在一起。

**路径（名义修复，实际空操作）**  
`wd = "./"` 只是把绝对路径换成了 CWD 依赖；`setwd("./")` 在 R 里是 no-op。二审建议的是 `pathlib` / `here`，相对**项目根或脚本位置**解析。现在从仓库根跑 `code/r/lda.R` 会去根目录找 `lexis.json`（真实文件在 `code/r/lexis.json`）；从 `homework/hw4/` 跑 `dictionary.R` 才碰巧能找到 `LIWC2007.txt`。这不是可移植性，是换了一种会失败的方式。

**循环内 I/O（目标达成，实现仍脆）**  
`lexis_dtm.py` / `trump_dtm.py` / `dictionaries.py` 把 `open(..., 'a')` 挪到循环外，这一点对。但表头和数据仍是两次 `'a'` 打开：重跑会重复表头+行。应一次 `'w'` 写完。`dictionaries.py` 读演讲稿已改成 `with open`，这条 LOW 算修掉了。

**未改、但二审点过、现在仍会炸的运行时问题（本 PR 不必全修，但不要假装审查已闭环）**

- `stemming.py`：`word_tokenize` / `FreqDist` / `PorterStemmer` 等 import 仍被注释，入库即 `NameError`
- `lexis.py` / `homework/hw3/lexis.py`：`codecs.open(...)` 仍无 `with`/`close`
- `svm.R:24`：`trace("create_matrix", edit=T)` 非交互环境挂死
- `lda.R` / `svm.R`：每次运行 `install.packages(...)`
- HW2：`if len(pub_date) == 0: pub_date == "NA"` 仍是比较不是赋值
- 分页 `while keep_going` 仍无页数上限

---

### 3. 安全

**已改善**

- 工作树中两把硬编码 NYT key 已不在当前 blob 里
- NYT 调用改为 HTTPS，不再把 key 放在明文 HTTP 上

**仍是问题**

1. **运行时泄密（应修）** — `homework/hw2/Hu_replication.py:20` 仍 `print("The URL is ", url)`。key 进了环境变量之后，这行会把**用户自己的** key 打到 stdout/日志。这是本 PR 引入的新风险形态（旧代码打印的是已泄露的作业 key；新代码打印的是操作者的活凭证）。
2. **历史未净化** — `nyt_demo.py` 那把 key 仍在 `4252d95`（`REVIEW.md`）和更早提交；HW2 那把 key 仍在 `15a2a42` / `3cc872d`。从 HEAD 删掉不等于泄露结束。两把 key 都应在 NYT Developer 门户轮换。后续提交**不要再写出完整 key**。
3. **Query string 传 key** — 环境变量解决的是仓库泄露，不是 access log / Referer / 代理日志。可选改进：`api-key` header，而不是拼进 URL。
4. **二审提过、本 PR 完全未碰**
   - `homework/hw4/LIWC2007.txt`：疑似专有 LIWC 2007 词典，是许可问题
   - `homework/hw3/trump.html.baiduyun.uploading.cfg`：百度云上传残留

空默认值不是“更安全”，是把认证失败推迟到 JSON 解析。

---

### 4. 回归

没有测试，也没有 CI（`checks` 为空）。抽查改动本身：

- 缩进：`lexis_dtm.py` / `trump_dtm.py` / `dictionaries.py` 的 `writerow` 仍在 `if` 内，没有把行写到错误层级
- `Hu_trump.py` 原本就有 `import os`；`Hu_hillary.py` / `Hu_replication.py` 有补 import，不会 `NameError`
- **行为回归（可接受，但未说明）**：没设 `NYT_API_KEY` 时作业脚本从“带着泄露 key 能跑”变成“请求失败”。应在 `README` 写一句
- **路径回归**：`setwd("./")` 切断了原先指向 Dropbox/Desktop 数据目录的约定。在课程仓库里数据本就不完整，这未必更糟，但把它写成“fix portability”是夸大
- 本 PR 叠在 PR #1 分支 `jules-2659870686789863091-5adb56c7` 上，不直接进 `master`。先合 #2 再合 #1，会把过期的 `REVIEW.md` 带进默认分支

---

### 5. `REVIEW.md` 质量 — 这次的核心失败

二审卡住 #1，是因为文档**不可靠**。本 PR 修了错文件名和明文 key，然后立刻制造了下一类不可靠：

当前 HEAD 已是 `wd = "./"`、`https://`、`os.environ.get(...)`，`REVIEW.md` 却仍写：

- CRITICAL：这些文件里**还有**硬编码 key（没有）
- HIGH：这些文件**正在**走 `http://`（没有）
- MEDIUM：这些行**仍是** `/Users/brycedietrich/...`（没有；行号也是旧的）
- LOW：循环内 `'a'` 打开（已经挪到循环外）

这不再是审查，是一份与 diff 矛盾的清单。读文档的人会去“修”已经不存在的绝对路径。

还没改的二审文档问题：

- 缺测试仍标 MEDIUM（课程作业仓库）
- Avalon HTTP 与 NYT key-in-URL 仍同档 HIGH
- 未记录 LIWC / baiduyun / `stemming.py` 烂 import / `trace(edit=T)`
- 没有 Fixed / Remaining 分区，尽管同一 commit 已经改了代码

`api-key=<redacted>` 写两次也没有信息量。写路径即可，不要假装还有两把不同的活 key 印在文档里。

---

### 6. 合并前必须改

1. **重写 `REVIEW.md` 反映 HEAD**：已修项标 Fixed（路径、HTTPS、工作区密钥、循环外 I/O、`with open`）；未修项留在 Remaining。不要再引用已删除的 `/Users/...` 行号。或者按二审建议：把审查放进 PR 正文，不要把这份文件合进 `master`。
2. **删掉 `Hu_replication.py` 的 `print(..., url)`**（以及任何会打印带 `api-key=` URL 的调试输出）。
3. **环境变量缺失时 fail-fast**，去掉 `get(..., "")`；`README` 加一行 `NYT_API_KEY`。
4. **路径不要再用 `setwd("./")` / `wd = "./"` 冒充修复。** 要么按脚本位置解析（`pathlib.Path(__file__).parent` / `here::here()`），要么在文档里承认 CWD 约定。
5. **重标定级**：测试/DRY/lockfile 降为 LOW 或删除；公开 HTTP 抓取与密钥传输分开。
6. **轮换两把已进 git 历史的 NYT key。** 这不能靠再提交完成，但必须在合并说明里写明，且不要把 key 再写进任何文件。
