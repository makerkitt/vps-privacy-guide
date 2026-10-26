# 维护、备份与排障

以下命令假设面板部署目录是 `/opt/sui-vps`。替换路径前先核对现有服务。

## 查看状态

```sh
cd /opt/sui-vps
sudo docker compose -f deploy/compose.yaml ps
sudo docker compose -f deploy/compose.yaml exec -T s-ui ./sui healthcheck
sudo docker compose -f deploy/compose.yaml logs --tail 100 s-ui
```

日志可能包含连接信息，只在可信终端查看。健康检查仅验证面板监听；代理核心启动错误、TLS 错误和客户端错误要分别查看。

## 备份

数据库和证书含用户凭据。下面使用短暂停机获得一致的整目录快照，现有连接会中断。每次升级前执行，并另存一份加密的异机备份。

```sh
cd /opt/sui-vps
sudo install -d -m 700 /var/backups/sui-vps
sudo docker compose -f deploy/compose.yaml stop s-ui
sudo sh -c 'umask 077; tar -czf "/var/backups/sui-vps/state-$(date -u +%Y%m%dT%H%M%SZ).tar.gz" deploy/state deploy/compose.yaml versions.json'
sudo docker compose -f deploy/compose.yaml start s-ui
sudo docker compose -f deploy/compose.yaml ps
```

逐条确认命令结果；备份失败也要启动服务，并查明失败原因。不要把备份提交到 Git。上游还提供数据库备份命令，但整机恢复还需要证书和部署版本。

## 升级与回滚

1. 阅读 S-UI 和 sing-box 的发行说明，备份当前状态、镜像摘要及证书。
2. 在测试环境更新镜像 tag 与摘要，同步 versions.json，执行仓库检查和三协议实测。
3. 正式环境执行 `docker compose -f deploy/compose.yaml up -d` 切换，重新验收。
4. 失败时停服务，保留失败状态作诊断；把旧备份解压到一个新的临时目录检查，再恢复旧版 Compose、数据库、证书和匹配镜像。
5. 数据库升级可能不可逆，不能只降级镜像而继续使用迁移后的数据库。恢复前先确认备份完整且路径正确。

不启用 Watchtower 或自动追踪 latest。Docker 的 `restart: unless-stopped` 负责进程退出后的重启，不会因为健康状态变为 unhealthy 自动修复节点。

## 证书续期

Certbot 的定时续期必须启用，短期 IP 证书尤其需要监控。续期后的 deploy hook 应完成以下动作：

1. 确认此次续期对应 `sui-vps` 证书；其他站点的证书不处理。
2. 检查新证书有效期，检查公钥与私钥配对，保留当前文件备份。
3. 将新 fullchain.pem 与 privkey.pem 同步到 `/opt/sui-vps/deploy/state/cert/`，权限分别 644 和 600。
4. 重启 S-UI，执行健康检查，并从客户端验证 AnyTLS/Hysteria2。重启会断开连接。
5. 如果失败，恢复之前匹配的证书/私钥并检查服务；不要关闭客户端证书校验。

本仓库首版**没有自动安装续期定时器或 deploy hook**。部署者须在实际 VPS 上配置并通过 `certbot renew --dry-run` 验证签发流程，另外验证证书同步和服务加载流程。不要把 staging 测试证书复制到生产服务。

使用 standalone 校验时，续期仍需要公网 TCP 80 可达且空闲；若后来添加了 Web 服务，应调整校验方式。

## 常见问题

| 现象 | 优先检查 |
| --- | --- |
| 面板打不开 | SSH 隧道是否运行、是否使用本地 12095、面板路径是否修改 |
| S-UI 显示健康但节点不通 | 是否已添加入站/用户、核心日志、云安全组、Docker 端口 |
| AnyTLS/Hysteria2 证书错误 | SAN 与 server_name、有效期、完整证书链、客户端时间、容器内证书路径 |
| 只有 Hysteria2 不通 | UDP 443 的云安全组/防火墙/运营商限制，不要只测 TCP |
| Reality 不通 | UUID、flow、公私钥配对、short ID、SNI/握手目标、双方时间 |
| 订阅缺少节点 | 用户关联、发布地址、出站模板、客户端格式支持 |
| 更换证书后仍显示旧证书 | 容器挂载文件是否更新，核心是否加载新文件 |

如果共享错误日志，先移除 IP、用户标识、订阅路径、认证头和密钥。
