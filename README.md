# 模型服务部署指南

面向 Linux 的通用部署资料：使用 Nginx 提供 HTTPS，通过 systemd 托管 FastAPI / ASGI 应用，并在启动前校验模型文件与标签映射。

```text
HTTPS 客户端
    │
    ▼
Nginx :443
    │  回环网络
    ▼
ASGI 服务 127.0.0.1:8000
    │
    ▼
模型文件 + 标签映射
```

| 资料 | 内容 |
|---|---|
| [部署步骤](docs/deployment.md) | 服务账户、目录、运行环境与启动顺序 |
| [模型文件核验](docs/artifact-verification.md) | 哈希、标签顺序、运行进程与加载证据 |
| [TLS 与常见故障](docs/troubleshooting.md) | 证书续期、反向代理、健康检查与排错 |
| [配置模板](examples/) | systemd、Nginx、环境变量及续期钩子 |
| [启动前校验脚本](scripts/verify_artifact.py) | 只使用 Python 标准库，不加载或反序列化模型 |
| [发布范围](PUBLIC_SCOPE.md) | 文档范围、占位符约定与许可边界 |

仓库不包含业务应用、模型文件或数据集。使用模板前，需要准备可导入的 ASGI 应用、可信的模型及标签文件，并替换所有占位符。模板中的 `app:app` 指向应用目录内的 `app.py`，该文件由部署者自行提供。

配置模板用于参考，尚不能代替目标环境中的语法检查、资源测试和端到端验收。应用的模型加载方式、预处理、并发能力和健康接口必须与部署配置相符。

校验脚本的本地检查：

```bash
python -m unittest discover -s tests -v
```

文档与模板采用 [MIT License](LICENSE)。第三方软件、模型与数据的许可分别适用，见 [第三方说明](THIRD_PARTY_NOTICES.md)。
