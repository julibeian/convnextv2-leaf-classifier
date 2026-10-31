# 参考训练集（负样本 / 健康样本）

这两个压缩包用于 ConvNeXtV2 叶片分类器的**非单一类别参考训练**，目的是让模型见过"健康水稻"以及"完全不是水稻叶片"的画面，避免把任何输入都硬判成某个病害。

## 包 1：`健康水稻_1733张.zip`

| 项 | 值 |
|---|---|
| 图片数 | 1733 |
| 格式 | 全部 `.jpg` |
| 大小 | 133.5 MB |
| 包内结构 | `健康水稻/1.jpg` … `健康水稻/1733.jpg`（平铺） |
| SHA256 | `8352901a448a814a5227b1367237ce686cb0acc1458f66d38b13d65192773edb` |
| 来源 | `E:\srt水稻项目\date\健康水稻`（后端 data 根目录，原始池） |

## 包 2：`其他_非截图非生活照片_1428张.zip`

| 项 | 值 |
|---|---|
| 图片数 | 1428（1402 `.jpg` + 26 `.png`） |
| 大小 | 180.2 MB |
| 包内结构 | `其他/<子类>/<文件>` |
| SHA256 | `73b899848c566c8d6ee6cb520277dc35ad18a48dc13e9ffd9e3cf26e764a1537` |
| 来源 | `E:\srt水稻项目\date\其他` |

### 收录的子类

| 子目录 | 张数 |
|---|---|
| 其他植物叶片1141 | 1141 |
| 壁纸25 | 24 |
| 夜景17 | 17 |
| 游戏截图11 | 11 |
| 纹理235 | 235 |

### 按要求排除的子类

| 子目录 | 张数 | 原因 |
|---|---|---|
| 截图158 | 158 | 屏幕截图，非自然图像 |
| 生活照片139 | 139 | 私人生活照 |

> 关于 `游戏截图11`：按"只排除 截图 与 生活照片 两个文件夹"的字面要求保留了；如按"排除所有截图"的口径，应从包 2 中去掉这 11 张（29.8 MB），需要时重新打包即可。

## 用法建议

- 作为分类器训练时的额外类别或难负样本池，不要与病害样本混为同一标签；
- 训练前建议先做近重复去重（壁纸/夜景多为大图，注意与验证集的泄漏）；
- 两个包合计 3161 张，解压后约 318 MB。

## 下载

发布页（完整链接）：

<https://github.com/julibeian/convnextv2-leaf-classifier/releases/tag/reference-sets-v1>

| 文件 | 大小 | 直接下载 |
|---|---|---|
| `healthy.rice.zip` | 133.5 MB | <https://github.com/julibeian/convnextv2-leaf-classifier/releases/download/reference-sets-v1/healthy.rice.zip> |
| `other.zip` | 180.2 MB | <https://github.com/julibeian/convnextv2-leaf-classifier/releases/download/reference-sets-v1/other.zip> |

Release 资产名为 `healthy.rice.zip` / `other.zip`，包内目录仍是中文（`健康水稻/`、`其他/`）。

> 仓库内 `reference_sets/` 下另有一份 Git LFS 副本；克隆整个仓库需要 `git lfs install`。只想取数据的话，用上面的 Release 直链即可。
