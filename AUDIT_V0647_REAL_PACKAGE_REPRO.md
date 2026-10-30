# v0.6.47 真实交付包回归复现

以用户提供的 `KIYUU_K01_CBCC_测试.zip` 重新执行 v0.6.47 完成标准，当前包不得判定为 FULL READY。

## 复现结果

1. 正式 FULL 文件合同中至少 17 个对象缺失，包括 FULL/HUMAN/语言/平台/真源审计、Strategy machine authorities、Commerce Decision Context、supporting_analysis 核心对象、ASSET_UNIVERSE 与 FULL_DELIVERY_OBJECT_MANIFEST。
2. `01_LISTING_UPLOAD_READY.md` 存在 EN/BM Title、Product Name、Skin Type、Bullets、Description 等外文对象，但不存在同字段中文 companion。
3. `asset_packages/LST-01…09/06_prompt_EN.txt` 9/9 含中文执行语言，违反 Model Prompt EN language-purity contract。
4. 最终包只物化 LST-01…09，未保留正常样本中的 Paid/Test/Video 等非 Live Gallery 资产层。

## Release rule

上述任一 P0 仍存在时，Host-native 或 Runtime 路径都不得输出 `PASS / DELIVERY_READY / FULL COMPLETE`。v0.6.47 必须以内容深度、语言 companion、资产宇宙与正式对象物化作为完成依据，而不是标题、布尔值、目录数量或 9 个 Gallery package。
