# dev-ci-kit

可复用的 GitHub Actions 工作流和 Codex Skill，帮助 Maven Java、npm 前端项目接入构建、测试、依赖漏洞扫描与 AI 审查。

## 项目架构

![业务仓库调用可复用工作流进行构建、扫描和审查](docs/assets/ci-architecture.png)

[架构图 Excalidraw 源文件](docs/assets/ci-architecture.excalidraw) · [Mermaid 源文件](docs/assets/ci-architecture.mmd)

| 工作流 | 用途 |
| --- | --- |
| `java.yml` | Maven 编译、测试及 Surefire 报告。 |
| `frontend.yml` | npm 安装依赖、lint 和构建。 |
| `security.yml` | OSV-Scanner 依赖漏洞扫描。 |
| `ocr-review.yml` | 对符合条件的 PR 进行 AI 代码审查。 |
| `security-audit.yml` | 实验性、手动触发的源码安全审查。 |

业务项目按需调用这些工作流；`validate.yml` 用于检查本工具包自身。

## 使用方法

推荐在业务项目中让编程 Agent 检查项目结构并接入，例如：

> 请根据 `LntanoC/dev-ci-kit` 为当前项目配置合适的 GitHub Actions CI，保留已有检查；按需接入 AI 审查和源码安全审查。

如果使用 Codex，可要求它用 `$skill-installer` 安装 `LntanoC/dev-ci-kit` 的 `skills/dev-ci`，然后使用 `$dev-ci` 接入或检查 CI。Skill 是安装时的本地副本，不会随仓库自动更新。也可参考 [日常 CI 示例](skills/dev-ci/assets/ci-java-react.yml)、[定时扫描示例](skills/dev-ci/assets/security-schedule.yml)和[手动源码审查示例](skills/dev-ci/assets/security-audit-manual.yml)自行配置。

启用 AI 功能时，在业务仓库的 **Settings → Secrets and variables → Actions → Secrets** 中配置所选工作流要求的 API 密钥；不要将密钥提交到仓库或发给 Agent。当前提供的 OCR 和源码安全审查模板使用通用的 Secret 名称 `LLM_API_KEY`。模型服务商并不局限于 DeepSeek，但当前 OCR 工作流的 API 地址和源码审查工作流的提供商配置面向 DeepSeek；使用其他服务需要由 Agent 适配并验证，不能只更换密钥。已有业务仓库的工作流不会自动更新，可继续使用原来的 Secret 映射；复制新模板时应配置 `LLM_API_KEY`。

Agent 可根据项目调整工作流，但还需在真实 GitHub Actions 中确认依赖、权限、密钥、服务连通性和结果。Java 工作流面向 Maven；前端工作流面向 npm，需要锁文件及对应脚本。

## 安全审查的边界

- OCR 仅审查同仓库可信作者的非草稿 PR；选中的变更会发送给配置的模型服务，并可能产生费用。
- 源码安全审查是实验性功能，仅在私有仓库默认分支手动触发。它使用 DeepSeek Harness 参考 Cloudflare 审计指引，输出保留 5 天的 Actions 报告；不会自动执行完整六阶段审计或保证独立复核。运行成功不代表项目没有漏洞。
- 接入前确认代码、会话日志及报告的访问权限和数据处理方式。Harness 只读模式不限制网络或读取范围，只审查可信代码；需要执行目标代码验证的线索应另行在符合要求的隔离环境验证。
- 源码审查每次获取 Cloudflare 指引默认分支最新提交并安装 npm `latest` 标签的 Harness，实际版本记录在日志中。示例使用 `@main`，OCR 也引用上游浮动版本；上游更新可能改变行为或引入不兼容。需要稳定性时可固定经过验证的版本。

## 开发与验证

```sh
python -m pip install PyYAML==6.0.3
python -m unittest discover -s tests -v
```

本仓库的工作流还会执行 actionlint；本地静态检查不能代替真实业务仓库的远端运行。
