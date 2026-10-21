# 部署步骤

以下示例面向使用 systemd 的 Linux 系统。应用代码、模型文件、标签映射和依赖清单需要事先准备。包管理器命令以 Debian 系发行版为例，其他发行版应使用对应命令。

## 准备账户和目录

```bash
sudo apt update
sudo apt install python3-venv nginx certbot
sudo useradd --system --user-group --home /srv/model-api --shell /usr/sbin/nologin model-api
sudo install -d -o root -g model-api -m 0750 /srv/model-api
sudo install -d -o root -g model-api -m 0750 /srv/model-api/private
sudo install -d -o root -g model-api -m 0750 /etc/model-api
```

创建账户前先检查是否已存在同名账户；已存在时核对其用途和组，不重复创建。应用应以专用账户运行。

将应用放到 `/srv/model-api`，将本仓库内容放到 `/srv/model-api/deployment`。模板默认应用入口为 `app:app`。如应用使用其他模块名，修改 `MODEL_APP_MODULE`。

## 准备运行环境

```bash
sudo python3 -m venv /srv/model-api/venv
sudo /srv/model-api/venv/bin/python -m pip install --upgrade pip
```

随后按应用自己的依赖清单安装软件。涉及 PyTorch 时，先按[官方安装说明](https://pytorch.org/get-started/locally/)选择匹配 CPU 或加速设备的版本，再安装其余依赖。不要把开发机器的完整环境直接当作部署依赖。

确认应用目录、虚拟环境和模板可由服务账户读取。应用如果需要写文件，应配置单独的写入目录。

## 准备模型和标签

将可信模型文件和标签映射分别保存为：

```text
/srv/model-api/private/model.pth
/srv/model-api/private/labels.json
```

标签映射的结构示例：

```json
{"0": "class_a", "1": "class_b"}
```

按真实输出维度和类别顺序设置标签。示例中的两个名称不是可直接用于任意模型的标签。

文件应由受控的部署账户管理，并允许服务账户读取：

```bash
sudo chown root:model-api /srv/model-api/private/model.pth /srv/model-api/private/labels.json
sudo chmod 0640 /srv/model-api/private/model.pth /srv/model-api/private/labels.json
```

## 配置启动前校验

把 `examples/runtime.env.example` 复制到 `/etc/model-api/runtime.env`。填写模型和标签映射各自的可信 SHA-256、类别数以及应用入口，替换全部 `REPLACE_` 占位符。

哈希应通过可信发布渠道取得。下面的命令可用于检查本地文件与预期值是否一致，不能独立证明来源可信：

```bash
sha256sum /srv/model-api/private/model.pth
sha256sum /srv/model-api/private/labels.json
```

校验脚本读取 `MODEL_ARTIFACT_PATH`、`MODEL_ARTIFACT_SHA256`、`MODEL_LABELS_PATH`、`MODEL_LABELS_SHA256` 和 `MODEL_CLASS_COUNT`。应用也必须读取相同的文件，或者显式配置与这些值一致的加载路径。脚本不会自动改变应用的加载逻辑。

```bash
sudo chown root:model-api /etc/model-api/runtime.env
sudo chmod 0640 /etc/model-api/runtime.env
sudo install -m 0644 /srv/model-api/deployment/examples/model-api.service /etc/systemd/system/model-api.service
sudo systemctl daemon-reload
sudo systemctl enable --now model-api.service
```

`ExecStartPre` 校验失败时，systemd 不会启动应用。检查结果及启动日志：

```bash
sudo systemctl status model-api.service --no-pager
sudo journalctl -u model-api.service --no-pager -n 50
curl --fail --silent --show-error http://127.0.0.1:8000/health
```

`/health` 必须由应用实现，并且只有在模型完成加载后才返回就绪状态。单纯 HTTP 200 或模块能够导入，不能证明模型已加载。

## 配置 HTTPS

将示例域名替换为自己控制的域名，检查 DNS 和目标网络的访问规则。应用端口只绑定回环地址；对外入口由 Nginx 提供。

先安装 HTTP 配置，再申请证书：

```bash
sudo install -d -m 0755 /var/www/acme
sudo install -m 0644 /srv/model-api/deployment/examples/nginx-http.conf.example /etc/nginx/conf.d/model-api-http.conf
sudo nginx -t
sudo systemctl reload nginx
sudo certbot certonly --webroot -w /var/www/acme -d api.example.com
```

证书签发成功后再安装 HTTPS 配置。两个配置中的域名和证书目录须一致。

```bash
sudo install -m 0644 /srv/model-api/deployment/examples/nginx-https.conf.example /etc/nginx/conf.d/model-api-https.conf
sudo nginx -t
sudo systemctl reload nginx
curl --fail --silent --show-error https://api.example.com/health
```

随后按 [TLS 与常见故障](troubleshooting.md) 配置续期钩子并演练。不要在尚未取得证书时启用引用该证书的 HTTPS 配置。

## 验收

检查配置语法、服务启动、模型加载、回环健康接口和 HTTPS 健康接口。再用已知输入验证预测输出，并分别测试上传上限、并发、超时和重启后的恢复。模板使用单个 worker，避免在未测量内存占用前重复加载模型。

本仓库没有实现用户认证、业务接口或限流逻辑。对外提供推理服务时，应在应用或入口层补齐适用的访问控制和资源限制。
