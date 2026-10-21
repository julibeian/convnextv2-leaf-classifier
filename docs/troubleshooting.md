# TLS 与常见故障

## HTTP 验证请求被重定向

签发证书时，HTTP-01 验证需要访问 `/.well-known/acme-challenge/`。在 Nginx 的同一个 `server` 层放置无条件 `return`，可能使请求在进入预期的 `location` 前被重定向。

HTTP 模板将验证路径和普通路径分别配置：验证路径读取 webroot，普通路径才执行 HTTPS 重定向。变更后先运行 `nginx -t`，再 reload，并检查验证路径响应。

参考：[Nginx 请求处理](https://nginx.org/en/docs/http/request_processing.html)、[rewrite 模块](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html)。

## 续期后仍提供旧证书

续期更新证书文件后，Nginx 需要重新加载配置。可以安装 deploy hook：

```bash
sudo install -m 0755 /srv/model-api/deployment/examples/reload-nginx.sh /etc/letsencrypt/renewal-hooks/deploy/reload-nginx
sudo certbot renew --dry-run
```

检查系统中实际启用的续期机制，例如 `certbot.timer` 或相应的计划任务。不要因为证书签发成功就认定自动续期已验证。

不同 Certbot 版本对 dry-run 中 deploy hook 的执行方式可能不同。按照所安装版本的帮助信息测试钩子，并分别验证证书签发、计划任务和 Nginx reload。

参考：[Certbot 续期与钩子](https://eff-certbot.readthedocs.io/en/stable/using.html#pre-and-post-validation-hooks)。

## 反向代理返回 502

先检查应用服务是否运行、是否只监听预期的回环端口，再检查 Nginx 的上游地址。查看必要的日志片段，不要直接分享完整日志。

```bash
systemctl status model-api.service --no-pager
curl --fail --silent --show-error http://127.0.0.1:8000/health
sudo nginx -t
```

## 启动前校验失败

分别检查文件路径、服务账户读权限、模型与标签各自的预期哈希、标签索引和类别数。只有经过验证的发布变更才应更新预期哈希；不要仅为了让校验通过而把任意现有文件的哈希设为可信值。

## 内存占用超出预期

多个 worker 通常会分别加载模型。先使用单 worker 测量模型加载、预热和并发推理时的峰值内存，再决定服务进程数量。文件体积不等于运行内存占用。

## 健康接口成功但预测失败

确认健康接口是否检查了实际加载状态。然后用已知输入核对输入格式、预处理、标签顺序和输出规则。应单独记录加载失败、输入校验失败和推理失败，避免将它们都显示为模型预测结果。
