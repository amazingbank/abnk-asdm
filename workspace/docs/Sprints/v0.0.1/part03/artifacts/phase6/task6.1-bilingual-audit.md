---
sprint: v0.0.1
part: part03
phase: 6
task: "6.1"
status: done
date: 2026-11-16
evidence: ./
locale: zh-CN
---
# 任务 6.1 触碰文件注释双语核查矩阵 / Task 6.1 bilingual-comment audit matrix

> 范围 = Phase 1–4 改动详情全量触碰文件（含 Phase 5 物理复核口径 + Phase 7 独有新增文件 `resettable.dart`、`data_epoch_reset_test.dart`——Phase 7 其余触碰文件与 Phase 1–4 清单重合，以最终态审计）。清单落盘 [`task6.1-filelist.txt`](./task6.1-filelist.txt)（96 文件，一行一路径，V6.2.3 硬门传参依据）。
> Scope = all files touched per the Phase 1–4 改动详情 lists (plus the Phase 5 physical re-verification note and the two Phase 7-only new files `resettable.dart` and `data_epoch_reset_test.dart` — the rest of Phase 7 touches overlap the Phase 1–4 list and are audited in their final state). The list lives in [`task6.1-filelist.txt`](./task6.1-filelist.txt) (96 files, one path per line; the argument list for the V6.2.3 hard gate).

## 判定口径 / Pairing criteria

- 形态 A：同行 `// 中文说明 | English summary`。
- 形态 B：中文注释段在上、英文语义重写段紧随（可跨多行，段间可空注释行）。
- 块级判定：注释块（连续注释行）内含 CJK 行时，块内须存在收尾于中文段之后的英文行组；`# noqa-bilingual` 行内豁免（本次未使用）。
- 两形态均认（Phase 6 文档已知坑 1）；判定脚本 `.audit-pairing.py`（块级模型，python3，审计期临时工具）。

## 核查矩阵 / Audit matrix

| # | 文件（相对 abnk-system 仓根） | CJK 注释行 | 配对形态 | 配对缺口 | 处置 |
|---|---|---|---|---|---|
| 1 | channels/backoffice/src/i18n/resources.ts | 9 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 2 | channels/backoffice/src/i18n/interpolate.ts | 3 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 3 | channels/backoffice/src/i18n/locale-context.ts | 7 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 4 | channels/backoffice/src/i18n/locale.ts | 8 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 5 | channels/backoffice/src/i18n/locale-provider.tsx | 24 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 6 | channels/backoffice/src/i18n/use-locale.ts | 6 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 7 | channels/backoffice/src/i18n/index.ts | 2 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 8 | channels/backoffice/src/i18n/api-error.ts | 7 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 9 | channels/backoffice/src/i18n/locales/zh-cn/common.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 10 | channels/backoffice/src/i18n/locales/zh-cn/login.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 11 | channels/backoffice/src/i18n/locales/zh-cn/clients.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 12 | channels/backoffice/src/i18n/locales/zh-cn/loanOps.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 13 | channels/backoffice/src/i18n/locales/zh-cn/errors.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 14 | channels/backoffice/src/i18n/locales/en-us/common.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 15 | channels/backoffice/src/i18n/locales/en-us/login.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 16 | channels/backoffice/src/i18n/locales/en-us/clients.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 17 | channels/backoffice/src/i18n/locales/en-us/loanOps.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 18 | channels/backoffice/src/i18n/locales/en-us/errors.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 19 | channels/backoffice/src/components/LanguageToggle.tsx | 4 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 20 | channels/backoffice/src/components/BoLayout.tsx | 1 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 21 | channels/backoffice/src/components/IdentifierEditForm.tsx | 4 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 22 | channels/backoffice/src/components/IdentifierCard.tsx | 1 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 23 | channels/backoffice/src/components/IdentifierStatusTag.tsx | 1 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 24 | channels/backoffice/src/components/LoanCard.tsx | 1 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 25 | channels/backoffice/src/components/SavingsTable.tsx | 1 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 26 | channels/backoffice/src/components/FixedDepositTable.tsx | 1 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 27 | channels/backoffice/src/AppProviders.tsx | 8 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 28 | channels/backoffice/src/main.tsx | 3 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 29 | channels/backoffice/src/pages/LoginPage.tsx | 1 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 30 | channels/backoffice/src/pages/ClientListPage.tsx | 1 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 31 | channels/backoffice/src/pages/ClientDetailPage.tsx | 1 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 32 | channels/backoffice/src/pages/LoanOpsPage.tsx | 3 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 33 | channels/backoffice/src/utils/format.ts | 3 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 34 | channels/backoffice/src/api/errors.ts | 9 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 35 | channels/backoffice/src/api/mock/mockAuth.ts | 5 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 36 | channels/backoffice/src/api/remote/remoteAuth.ts | 4 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 37 | channels/backoffice/src/api/mock/mockClient.ts | 5 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 38 | channels/backoffice/src/api/remote/remoteClient.ts | 26 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 39 | channels/backoffice/src/api/remote/generatedClient.ts | 26 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 40 | channels/backoffice/src/api/mock/mockStore.ts | 35 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 41 | channels/backoffice/src/api/mock/mockData/types.ts | 9 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 42 | channels/backoffice/src/api/mock/mockData/zh-cn/clients.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 43 | channels/backoffice/src/api/mock/mockData/zh-cn/operators.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 44 | channels/backoffice/src/api/mock/mockData/en-us/clients.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 45 | channels/backoffice/src/api/mock/mockData/en-us/operators.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 46 | channels/backoffice/Dockerfile | 18 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 47 | channels/mobile-banking/l10n.yaml | 3 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 48 | channels/mobile-banking/lib/l10n/app_zh.arb | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 49 | channels/mobile-banking/lib/l10n/app_en.arb | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 50 | channels/mobile-banking/pubspec.yaml | 24 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 51 | channels/mobile-banking/lib/main.dart | 12 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 52 | channels/mobile-banking/lib/app_scope.dart | 21 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 53 | channels/mobile-banking/lib/app.dart | 10 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 54 | channels/mobile-banking/lib/main_scaffold.dart | 5 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 55 | channels/mobile-banking/lib/features/login/login_page.dart | 6 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 56 | channels/mobile-banking/lib/features/home/home_page.dart | 4 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 57 | channels/mobile-banking/lib/features/transactions/transactions_page.dart | 5 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 58 | channels/mobile-banking/lib/features/transfer/transfer_page.dart | 6 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 59 | channels/mobile-banking/lib/features/fixed_deposit/fixed_deposit_page.dart | 5 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 60 | channels/mobile-banking/lib/features/loans/loans_page.dart | 4 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 61 | channels/mobile-banking/lib/features/profile/profile_page.dart | 10 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 62 | channels/mobile-banking/lib/data/models/transaction.dart | 5 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 63 | channels/mobile-banking/lib/data/models/identity.dart | 5 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 64 | channels/mobile-banking/lib/data/models/loan.dart | 8 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 65 | channels/mobile-banking/lib/core/errors/app_exception.dart | 21 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 66 | channels/mobile-banking/lib/data/remote/generated_client.dart | 26 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 67 | channels/mobile-banking/lib/data/mock/mock_account_repository.dart | 16 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 68 | channels/mobile-banking/lib/data/mock/mock_identity_repository.dart | 3 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 69 | channels/mobile-banking/lib/data/mock/mock_auth_repository.dart | 3 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 70 | channels/mobile-banking/lib/data/mock/mock_loan_repository.dart | 3 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 71 | channels/mobile-banking/lib/data/mock/data_locale.dart | 18 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 72 | channels/mobile-banking/lib/data/mock/fixture_bundle.dart | 13 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 73 | channels/mobile-banking/lib/data/mock/resettable.dart | 5 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 74 | channels/mobile-banking/test/app_locale_test.dart | 4 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 75 | channels/mobile-banking/test/profile_page_test.dart | 4 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 76 | channels/mobile-banking/test/login_page_test.dart | 2 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 77 | channels/mobile-banking/test/home_page_test.dart | 3 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 78 | channels/mobile-banking/test/transactions_page_test.dart | 2 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 79 | channels/mobile-banking/test/transfer_page_test.dart | 1 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 80 | channels/mobile-banking/test/fixed_deposit_page_test.dart | 2 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 81 | channels/mobile-banking/test/loans_page_test.dart | 1 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 82 | channels/mobile-banking/test/fixture_data_locale_test.dart | 11 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 83 | channels/mobile-banking/test/data_epoch_reset_test.dart | 7 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 84 | channels/mobile-banking/test/helpers/test_app.dart | 10 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 85 | channels/mobile-banking/fixtures/zh-cn/me.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 86 | channels/mobile-banking/fixtures/zh-cn/identity.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 87 | channels/mobile-banking/fixtures/zh-cn/accounts.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 88 | channels/mobile-banking/fixtures/zh-cn/transactions.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 89 | channels/mobile-banking/fixtures/zh-cn/loan_products.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 90 | channels/mobile-banking/fixtures/en-us/me.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 91 | channels/mobile-banking/fixtures/en-us/identity.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 92 | channels/mobile-banking/fixtures/en-us/accounts.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 93 | channels/mobile-banking/fixtures/en-us/transactions.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 94 | channels/mobile-banking/fixtures/en-us/loan_products.json | 0 | —（无注释资产） | 0 | 2026-11-16 复核清零 |
| 95 | channels/mobile-banking/Dockerfile | 34 | B（段式为主） | 0 | 2026-11-16 复核清零 |
| 96 | deploy/prod/env/abnk-fullstack.env.example | 35 | B（段式为主） | 0 | 2026-11-16 复核清零 |

## 处置汇总 / Disposition summary

- 触碰文件总数 96（backoffice 46 + mobile-banking 49 + 部署 env 样例 1）；无注释资产（JSON/ARB 词条与 fixtures，CJK 注释数 0）33 件，含注释资产 63 件。
- 审计发现漏网并就地补齐（2026-11-16）：backoffice 13 文件（IdentifierEditForm / IdentifierCard / IdentifierStatusTag / LoanCard / SavingsTable / FixedDepositTable / main.tsx / ClientListPage / LoanOpsPage / mockClient / remoteClient / generatedClient / Dockerfile）；mobile-banking 29 文件（pubspec / main / app_scope / app / main_scaffold + features 7 + models 3 + generated_client + mock 2 + test 9 + Dockerfile）+ 部署 env 样例 1——合计 43 文件约 200 行中文注释补英文语义重写配对。
- 补齐后全量复扫（.audit-pairing.py，与 V6.1.1 同口径）：594 行 CJK 注释，配对缺口总和 = **0**（V6.1.2 判据）。
- 英文一律语义重写（Plan 决策 D2 口径），非逐字直译。
