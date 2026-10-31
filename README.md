## ConvNeXt V2 叶片图像分类模型

基于 ConvNeXt V2 Base 的水稻叶片整图分类模型，输出 10 类概率：8 个病害或症状标签、健康水稻及“其他”。

### 权重模型和数据集

点击此处跳转下载链接  [跳转](https://github.com/julibeian/convnextv2-leaf-classifier/releases) 

### 介绍

| 项目 | 规格 |
|---|---|
| 网络 | `convnextv2_base.fcmae_ft_in1k` |
| 参数量 | 87,703,050 |
| 输入 | RGB，224 × 224 |
| 输出 | 10 类 logits，Softmax 概率 |
| 权重格式 | Safetensors，float32，约 351 MB |
| 使用范围 | 非商业研究与实验 |

模型包包含 `model.safetensors`、`config.json`、`labels.json`、离线推理代码、模型卡及许可文件。权重只包含推理张量。

| 评测范围 | 样本量 | 准确率 | Macro F1 |
|---|---:|---:|---:|
| 同分布测试，10 类 | 1,020 | 98.24% | 0.9785 |
| 独立采集来源，4 个支持类 | 3,734 | 8.86% | 0.1687 |


