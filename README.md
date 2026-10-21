# ConvNeXt V2 叶片图像分类模型

基于 ConvNeXt V2 Base 的水稻叶片整图分类模型，输出 10 类概率：8 个病害或症状标签、健康水稻及“其他”。

[下载模型包](https://github.com/julibeian/convnextv2-leaf-classifier/releases/latest) · [模型卡](MODEL_CARD.md) · [输入契约](config.json) · [类别映射](labels.json)

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

第二行 Macro F1 只在该来源的四个支持类上计算。两项评测的分布和类别范围不同。独立来源结果显示明显的分布迁移问题，同分布分数不能用于承诺田间识别效果。每类指标、拒识规则及局限见模型卡。

离线调用：

```bash
python inference.py path/to/image.jpg --model-dir path/to/model-bundle
```

环境依赖见 [requirements.txt](requirements.txt)。模型权重采用 [CC BY-NC 4.0](WEIGHTS_LICENSE.md)；代码和文档采用 [MIT License](LICENSE)。
