# dev-ci-kit

可复用的 GitHub Actions CI 工作流和 Codex Skill，帮助 Maven Java、npm 前端项目接入构建、测试、依赖漏洞扫描与 AI 代码审查。

## 包含什么

| 工作流 | 默认行为 |
| --- | --- |
| `java.yml` | 使用 Java 17 编译并运行 Maven 测试，上传 Surefire 报告；优先使用项目的 Maven Wrapper。 |
| `frontend.yml` | 使用 Node.js 22 执行 `npm ci`、lint 和构建。 |
| `security.yml` | 使用 OSV-Scanner：PR 检查新增漏洞；其他事件全量扫描并报告，但默认不因已有漏洞失败。 |
| `ocr-review.yml` | 同仓库可信作者的非草稿 PR 使用 OpenCodeReview 和 DeepSeek 审查，并尝试在 PR 中发表意见。 |

Java 测试是否需要数据库等服务取决于业务项目；本工具不会自动提供这些服务。报告仅包含 Maven Surefire 生成的文件；若没有生成文件则不会上传。安全扫描覆盖哪些依赖取决于 OSV 支持的清单和锁文件。AI 审查结果需要人工判断，运行成功也不代表没有漏洞或所有文件都被审查。

## 在业务仓库接入

1. 根据项目实际情况，将 [Java + npm 前端示例](skills/dev-ci/assets/ci-java-react.yml)复制为业务仓库的 `.github/workflows/ci.yml`，并修改目录、版本和不需要的任务。示例的推送分支为 `main`。
2. Java 项目需要 Maven `pom.xml`、Java 17（或调整版本）和可运行的测试。前端需要 `package-lock.json` 以及 `lint`、`build` 脚本。可分别通过 `run-compile`、`run-tests`、`run-lint`、`run-build` 输入禁用步骤，但应先确认业务需要。
3. 如启用 OCR，在业务仓库 **Settings → Secrets and variables → Actions → Secrets** 中创建 `DEEPSEEK_API_KEY`，填入 DeepSeek API 密钥，不要提交密钥。组织级 secret 也可使用，但需要给该仓库授权。无需配置 `OCR_LLM_MODEL`，默认模型为 `deepseek-flash`，可通过 `model` 输入调整。
4. 提交到功能分支并创建 PR，在 Actions 和 PR 评论中检查结果。可另行使用[定时扫描示例](skills/dev-ci/assets/security-schedule.yml)，默认每周一 02:23 UTC 执行，也支持手动运行。

调用工作流须允许相应的 `GITHUB_TOKEN` 权限。示例已按任务声明：Java/前端只读仓库；OSV 工作流包含 `actions: read` 和 `security-events: write`；OCR 使用 `pull-requests: write` 发布评论。仓库或组织策略仍可能限制权限和第三方 Actions，需在真实运行中确认。

## 接入 Codex Skill

将本仓库的 `skills/dev-ci` 安装为 Codex Skill，之后可在目标项目中要求 Codex 使用 `$dev-ci` 接入或检查 CI。安装后如果 Codex 没有发现新 Skill，重启 Codex 或开启新会话。Skill 帮助检查项目并生成适配配置，实际 CI 由 GitHub Actions 运行。

Skill 是安装时的本地副本，**不会自动随仓库更新**；要获得最新的 Skill 指令和示例，需要重新安装或更新本地副本。业务仓库使用示例中的 `@main` 调用远程工作流，每次运行使用当时的 `main`；OCR Action 引用上游 `@main`，并安装当时的 npm `latest`。因此即使业务仓库没有改动，运行结果和行为也可能变化，上游更新可能引入故障或供应链风险。需要稳定性时可改为经过验证的提交 SHA 和版本，并建立升级机制。

## AI 审查的边界

- OCR 会将选中的代码变更发送到 DeepSeek，可能产生 API 费用；接入前确认代码及数据允许发送给该服务。
- 示例仅允许同仓库、作者身份为 OWNER/MEMBER/COLLABORATOR 的非草稿 PR 运行 OCR。来自 fork 的 PR 会跳过；普通构建和安全检查仍会运行。
- 此条件不能替代仓库访问控制：能修改同仓库工作流或提交代码的人员仍须可信，合并前应审查工作流变更。不要改用 `pull_request_target` 并执行不可信 PR 代码。
- Java、前端和依赖扫描不需要 DeepSeek 密钥。OCR 不能代替测试、漏洞扫描和人工评审。

## 开发与验证

本仓库自己的工作流会执行配置测试和 actionlint。修改后可本地执行：

```sh
python -m pip install PyYAML==6.0.3
python -m unittest discover -s tests -v
```

这些静态检查不能代替在真实业务仓库触发 GitHub Actions，特别是密钥、权限、评论发布和外部服务连通性。
