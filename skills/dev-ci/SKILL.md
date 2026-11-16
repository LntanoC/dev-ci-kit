---
name: dev-ci
description: Integrate, adapt, or audit reusable GitHub Actions CI from LntanoC/dev-ci-kit for Maven Java projects and npm frontends, including OSV dependency scanning and optional OpenCodeReview with DeepSeek.
---

# Dev CI

Use this skill when asked to set up or update a project's CI using dev-ci-kit. The kit's reusable workflows run on GitHub Actions; this skill helps the agent integrate them and does not itself run CI or access secrets.

1. Inspect the project instructions, existing GitHub workflows, build files, lockfiles, module paths, and test prerequisites. Preserve existing useful checks and avoid duplicate workflows and job names.
2. Use `assets/ci-java-react.yml` as a starting reference, adapting paths, Java and Node versions, and enabled jobs to the project. Remove Java or frontend jobs when not applicable. Java requires Maven and uses `mvnw` if present; frontend uses npm and requires `package-lock.json`. Do not assume Gradle, pnpm, or missing lint/build scripts are supported. Discuss unavoidable gaps instead of silently skipping checks.
3. Reuse the security job for supported dependency manifests. Add `assets/security-schedule.yml` if scheduled scans are desired. Inspect OSV scan results and existing dependency-scanning configuration.
4. Enable OCR only if the user wants AI review and accepts sending selected code changes to the configured model provider. The caller must provide repository or organization secret `DEEPSEEK_API_KEY`; never request its value in chat or write it into files. The reusable job skips forks, drafts, and PR authors outside OWNER/MEMBER/COLLABORATOR. Same-repository contributor access and workflow changes still require trust and review.
5. Respect local rules, validate configuration and relevant project checks, and report what was actually tested. Explain that a GitHub run is needed to verify remote permissions, secrets, model access, review comments, and the actual project environment. Do not claim local validation proves the remote workflow works.

The examples intentionally use `@main`, and OCR uses the latest upstream release. Both can change without a consumer repository change. Tell users about this tradeoff when integrating; do not change this policy without their agreement. Only push, open or merge PRs when authorized.
