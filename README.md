# Groovectl Skill

让 AI 助手通过自然语言使用 Groovectl 查询与鉴别 Discogs 唱片版本（含厂牌、目录号、条码、片芯刻码、曲目表与备注）、管理收藏（含自定义收藏夹、自定义字段/品相备注与评分）和心愿单、查看用户资料与歌单列表，以及读取或管理 Discogs Marketplace 数据（统计价、品相参考价、在售挂单、卖家店铺库存、个人挂单 CRUD、订单与消息、手续费）。

本项目是独立的 Skill 仓库，只调用已发布的 `groovectl` 命令。不包含 CLI 源码、Discogs API 客户端或用户凭据。当前命令基线为 **groovectl 0.2.0**，项目许可证为 Apache-2.0。

## 从零安装

Skill 文件和 CLI 是两个独立组件，**两者都需要安装**。运行环境需要支持本地命令执行与网络访问；只有聊天能力的环境无法执行此 Skill。

### 1. 安装并检查 Node.js

在实际运行助手的机器上打开终端，执行：

```sh
node --version
npm --version
```

需要 Node.js **24 或更新版本**。如果命令不存在或版本过低，先从 [Node.js 官网](https://nodejs.org/en/download) 按系统说明安装满足要求的 LTS 版本和 npm，重新打开终端，再检查上述版本。Windows 可用 PowerShell；如果 `npm.ps1` 被策略阻止，用 `npm.cmd`。

### 2. 安装 Groovectl CLI

macOS / Linux：

```sh
npm install --global groovectl@0.2.0
groovectl version --json
groovectl schema --compact
```

Windows PowerShell：

```powershell
npm.cmd install --global groovectl@0.2.0
groovectl.cmd version --json
groovectl.cmd schema --compact
```

这是安装 npm 上的公开软件包，不需要登录 npm、不需要克隆 CLI 仓库，也不需要 pnpm、TypeScript 或手工执行 `node dist/...`。固定版本用于复现本项目验证过的命令。

如果安装成功后找不到命令，运行 `npm prefix --global`，确认 macOS/Linux 的 `<prefix>/bin` 或 Windows 的 `<prefix>` 已加入用户 PATH。修改后重开终端及助手应用。权限、PATH、无需全局安装的替代方式见 [CLI 安装与认证](skills/groovectl/references/setup.md)。

### 3. 获取并安装 Skill

先取得本仓库的完整项目目录（本地交付目录，或仓库 ZIP 解压目录），在该目录打开终端。确认能看到 `README.md`、`scripts/` 和 `skills/`，然后执行；macOS/Linux 与 Windows 相同：

```sh
node scripts/install-skill.mjs
```

脚本默认复制到 `~/.agents/skills/groovectl`；Windows 是当前用户主目录下的 `.agents\skills\groovectl`。它只安装 Skill，不安装 CLI、不修改 PATH、不访问凭据，也不覆盖已有技能。

这使用 [OpenAI 官方文档](https://learn.chatgpt.com/docs/build-skills) 中 Codex 的用户技能目录。安装后尝试调用 `$groovectl`；如果当前会话没有发现它，重启 Codex 或新开会话再试。

如需仅在某个项目中使用，或安装到其他宿主目录（如 `~/.codex/skills`、`~/.gemini/config/skills`），在本仓库根目录执行：

```sh
node scripts/install-skill.mjs --skills-dir "/path/to/your-project/.agents/skills"
```

Windows 路径示例：

```powershell
node scripts/install-skill.mjs --skills-dir "C:\Projects\my-project\.agents\skills"
```

自定义路径必须是**技能父目录**，脚本会在下面创建 `groovectl`。其他支持 `SKILL.md` 的宿主可以使用自己的技能目录，但需要自行确认发现机制及命令执行能力。

### 4. 按需配置 Discogs 认证

已知 ID 的公开数据库查询、公开用户资料/列表、公开卖家库存，以及网页在售读取可以匿名使用；搜索、个人评分、收藏与心愿单、品相参考价（需卖家设置）、卖家挂单写入与订单管理需要 Discogs User Token；部分市场 API 请求也可由服务器要求认证。

1. 登录 Discogs，进入 [Settings → Developers](https://www.discogs.com/settings/developers)，生成个人 User Token。
2. 在你自己的交互式终端运行，按隐藏提示输入 Token：

   ```sh
   groovectl --token auth login
   groovectl auth status --json
   ```

3. 确认结果包含 `authenticated: true` 且用户名正确。Windows 必要时把命令换成 `groovectl.cmd`。
4. 助手执行账户操作时还会检查自身环境中的认证状态。容器、不同系统用户或无 keyring 服务的环境需要单独配置；详见 [认证说明](skills/groovectl/references/setup.md#3-authenticate-only-when-needed)。

认证保存在 CLI 使用的系统凭据库中。不要将 Token 发到聊天、写进本仓库、作为 `--token` 的参数或写入 Skill。`--token` 是隐藏输入开关。自动化环境可由宿主安全注入 `DISCOGS_TOKEN`；环境变量优先于已保存的凭据。如需稳定机器可读错误输出，可同时设置 `GROOVECTL_ERROR_FORMAT=json`（或传入 `--error-format json`）。

### 5. 验证与开始使用

先执行一次离线与只读验证：

```sh
groovectl schema --compact
groovectl release get 249504 --json
```

Windows 必要时使用 `groovectl.cmd`。如果返回 API 拒绝、限流或网络错误，先按错误处理，不要将其当作验证通过。

然后在助手中输入，例如：

```text
用 $groovectl 找 Miles Davis 的 Kind of Blue 1978 年日本黑胶版，核对目录号和片芯刻码，不修改账户。
用 $groovectl 查 release 249504 的当前最低价、各品相参考价和英国 VG+ 以上在售挂单。
用 $groovectl 检查 release 249504 是否已收藏，没有就加入 "Japanese Pressings" 收藏夹并记录品相备注。
用 $groovectl 在我的收藏里筛选带 "OBI" 备注的唱片。
用 $groovectl 先 dry-run 预览为 release 249504 创建一条 VG+ 草稿挂单（定价 45 USD）。
```

删除、上架 `For Sale` 挂单、更新订单状态或发送买家消息前请明确目标。Skill 会区分同一版本的多个收藏实例；不明确的版本或实例会先澄清。只读需求不会触发账户写入。

## 能力与边界

| 范围 | 能力 |
| --- | --- |
| AI / 自动化 | `schema [command...] [--compact]` 离线自省、`--error-format json` 结构化错误、`--quiet`、`--limit` 早停分页 |
| Database | 搜索（含 `masterId` / `barcodes`）、`release get` 完整压版详情（厂牌、目录号、条码、片芯刻码、曲目表、备注、社区统计）、`release rating`、`master versions` 服务端筛选与排序、`artist` / `label` |
| Collection | 收藏夹列表与自定义文件夹 CRUD、自定义字段查看与备注写入（`collection fields` / `note set`）、本地 `--query` 筛选、拥有检查、增改删与估值 |
| Wantlist / User / Lists | 心愿单列表（含 `--query`）、增改删；用户资料 `user profile`；公开/个人列表 `list ls` / `list get` |
| Marketplace | 官方 API：`stats`、`price-suggestions`、`listing get|create|update|delete`、`inventory`、`orders list|get|update|messages|message`、`fee`；网页 best-effort：`listings`（支持多条件筛选、排序及本地 `--html`） |

市场数据是本次请求的即时快照，最低商品价与挂单价均不包含运费和税费。`marketplace listings` 为网页 best-effort 读取（非官方 API），绝不携带 Token/Cookie、不重试、不绕过 403/验证挑战，遇阻时可改用浏览器保存的 `--html` 或官方 API 命令。不提供下单/支付、watch、定时任务、通知、历史价格库或本地缓存。不会将空价格当作 0；不支持的币种（如当前 CLI 的 CNY）不会被自动换算。

## 更新与卸载

更新 Skill：先备份已安装目录中的个人修改，移除旧的 `groovectl` 技能目录，再从新项目目录重新运行安装脚本。脚本拒绝覆盖目录或符号链接。

卸载默认位置的 Skill：

```sh
# macOS / Linux：只删除这个技能目录
rm -r "$HOME/.agents/skills/groovectl"
```

```powershell
# Windows PowerShell
Remove-Item -LiteralPath "$HOME\.agents\skills\groovectl" -Recurse
```

自定义安装位置请删除对应位置的 `groovectl` 目录。不要删除整个 `.agents/skills`。Skill 是独立副本，安装后可移走原项目；项目更新也不会自动更新已安装副本。

CLI 升级：`npm install --global groovectl@latest`，升级后检查 `groovectl version --json` 与 `groovectl schema --compact`。CLI 卸载：`npm uninstall --global groovectl`。Windows 可用 `npm.cmd`。这些操作与 Skill 卸载相互独立；卸载也不会撤销 Discogs Token，撤销需在 Discogs 设置中完成。

## 维护与验证

```sh
node --test tests/install-skill.test.mjs
```

该测试不联网、不依赖 CLI 源码，检查完整复制、带空格路径、参数校验和拒绝覆盖。

维护者还可以在安装 CLI 后使用 Python 3 标准库运行命令契约检查（Python 不是安装或使用 Skill 的前置条件）：

```sh
python3 tests/verify-cli.py
```

它读取命令参考中的示例，通过已安装 CLI 连接本地临时模拟 API 及临时 HTML 夹具，以合成 Token 验证参数、JSON 输出、结构化错误和 dry-run，不访问真实 Discogs 账户或外网页面。可用 `--cli /absolute/path/to/groovectl` 指定隔离安装的可执行文件。该检查当前已在 macOS 验证；Windows 的安装指南与安装脚本不需要 Python。

技能行为验收场景见 [tests/scenarios.md](tests/scenarios.md)；验证记录见 [VALIDATION.md](VALIDATION.md)。修改命令参考时应使用公开 npm 包验证，不从 CLI 项目导入实现。

项目结构：

```text
skills/groovectl/SKILL.md             技能入口
skills/groovectl/agents/openai.yaml   展示信息
skills/groovectl/references/         安装认证和命令参考
scripts/install-skill.mjs            跨平台安装脚本
tests/                              安装测试、命令契约检查和行为验收场景
```

上游：[Groovectl CLI](https://github.com/ShiTuoCheng/groovectl) · [npm](https://www.npmjs.com/package/groovectl/v/0.2.0)。本项目使用 Discogs 数据，但不隶属 Discogs，也未获其赞助或背书。
