---
name: dev-ci
description: 为 Maven Java 项目和 npm 前端接入、适配或检查 LntanoC/dev-ci-kit 的可复用 GitHub Actions CI，包括 OSV 依赖扫描和可选的 OpenCodeReview + DeepSeek 审查。
---

# Dev CI

当用户要求使用 dev-ci-kit 为项目配置或更新 CI 时，使用此 Skill。工具包的可复用工作流在 GitHub Actions 上运行；本 Skill 负责指导 Agent 完成接入，本身不会运行 CI 或读取密钥。

1. 检查项目指令、现有 GitHub 工作流、构建文件、锁文件、模块路径和测试前提。保留已有的有效检查，避免重复的工作流和任务名称。
2. 以 `assets/ci-java-react.yml` 为参考起点，根据项目调整路径、Java 和 Node 版本以及启用的任务。项目不适用时删除 Java 或前端任务。Java 任务要求使用 Maven，并在存在 `mvnw` 时优先使用它；前端任务使用 npm，要求存在 `package-lock.json`。不要假定支持 Gradle、pnpm，或项目中不存在的 lint/build 脚本。对于无法避免的检查缺口，应与用户说明，不要静默跳过。
3. 对支持的依赖清单复用安全扫描任务；如果需要定时扫描，添加 `assets/security-schedule.yml`。检查 OSV 扫描结果和项目现有的依赖扫描配置。
4. 仅当用户需要 AI 审查并接受将选中的代码变更发送给所配置的模型服务商时，才启用 OCR。示例要求调用方提供仓库级或组织级 Secret `LLM_API_KEY`；不要在聊天中索要密钥值，也不要将其写入文件。当前工作流默认连接 DeepSeek，改用其他服务需要适配并验证。可复用任务会跳过 fork、草稿 PR，以及作者身份不属于 OWNER/MEMBER/COLLABORATOR 的 PR。同仓库贡献者的访问权限和工作流变更仍需经过信任与审查。
5. 遵守本地规则，验证配置和相关项目检查，如实报告实际测试内容。说明需要真实的 GitHub 运行才能验证远端权限、密钥、模型访问、审查评论和实际项目环境；不要声称本地验证能够证明远端工作流正常运行。
6. 用户明确要求时，可向私有仓库提供实验性的 `assets/security-audit-manual.yml`。模板从 Secret `LLM_API_KEY` 获取密钥，当前工作流将源码发送给 DeepSeek。说明这是参考 Cloudflare 指引的聚焦源码审查，不是其完整审计或独立验证；日志和产物可能包含敏感信息。每次运行会获取 Cloudflare 指引默认分支的最新提交，并安装 npm `latest` 标签指向的 DeepSeek Harness 版本，同时记录两者版本；上游更新可能导致不兼容或行为变化。Harness 的只读模式不限制网络或读取范围，因此只应审查可信的默认分支。核实仓库私有状态、触发方式、数据共享、权限、费用以及真实远端运行情况。

示例有意使用 `@main`，OCR 使用上游最新版本。即使业务仓库没有变更，两者的行为也可能发生变化。接入时应向用户说明这一权衡；未经用户同意，不要更改此策略。只有在获得授权后才推送、创建或合并 PR。
