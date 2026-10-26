# S-UI 部署

本流程在目标 Linux VPS 上执行。它启动 S-UI，再通过面板添加节点；不会自动创建三种节点或申请证书。

## 1. 检查环境

使用已确认的 SSH 别名登录，确认 Docker Engine 和 Compose v2 已安装。不要把本机开发用 Docker 当作 VPS。

```sh
uname -m
cat /etc/os-release
docker version
docker compose version
sudo ss -lntup
```

本方案需要 TCP 443、TCP 8443 和 UDP 443 空闲。80/TCP 只在使用 HTTP-01 证书校验时需要。服务商安全组也必须放行节点端口与实际 SSH 端口。不要覆盖既有防火墙规则；Docker 发布端口涉及转发规则，不能只依赖 UFW 的普通入站规则判断隔离。

## 2. 拉取仓库并启动

以下示例假设目标目录 `/opt/sui-vps` 尚不存在。已有目录时先检查，不覆盖。

```sh
sudo git clone https://github.com/makerkitt/vps-privacy-guide.git /opt/sui-vps
cd /opt/sui-vps
sudo install -d -m 700 deploy/state/db deploy/state/cert
sudo docker compose -f deploy/compose.yaml config --quiet
sudo docker compose -f deploy/compose.yaml pull
sudo docker compose -f deploy/compose.yaml up -d
sudo docker compose -f deploy/compose.yaml ps
sudo docker compose -f deploy/compose.yaml exec -T s-ui ./sui healthcheck
```

固定版本与摘要见 [版本清单](../versions.json)。`deploy/state/db` 持久化面板数据库；证书放在 `deploy/state/cert`，容器内路径为 `/app/cert`，只读挂载。

## 3. 从自己的电脑访问面板

在自己的电脑执行，将 `my-vps` 换成 SSH 别名：

```sh
ssh -N -L 12095:127.0.0.1:2095 -L 12096:127.0.0.1:2096 my-vps
```

保持隧道运行，浏览器打开 `http://127.0.0.1:12095/app/`。默认管理路径按上游初始配置；如不一致，在服务器本地运行以下命令查看地址和初始管理员信息：

```sh
sudo docker compose -f /opt/sui-vps/deploy/compose.yaml exec s-ui ./sui uri
sudo docker compose -f /opt/sui-vps/deploy/compose.yaml exec s-ui ./sui admin -show
```

这两条命令可能显示敏感信息，只在自己的终端查看，不复制到聊天或公开日志。首次登录立即设置独立的管理员用户名、强密码；不要保留默认凭据。浏览器至本机虽显示 HTTP，跨网络部分由 SSH 隧道加密。

## 4. 创建 TLS 配置

按 [证书说明](tls.md) 准备证书。在 S-UI 的 TLS 配置中建立：

| 配置名 | 服务端 | 客户端订阅配置 |
| --- | --- | --- |
| `node-tls` | TLS 开启；证书 `/app/cert/fullchain.pem`；私钥 `/app/cert/privkey.pem` | TLS 开启；server_name 为证书覆盖的域名或 IP；insecure=false |
| `node-reality` | Reality 开启；独立私钥、short_id、握手地址/端口及匹配的 server_name | Reality 公钥、相同 short_id/server_name；uTLS 开启，fingerprint=chrome |

证书的私钥留在服务器，Reality 的私钥也只留服务端。证书续期后必须让服务加载新证书；见 [维护说明](maintenance.md)。

## 5. 添加三个入站和用户

在面板新增入站，根据以下表设置字段，监听 `0.0.0.0`。不要给 Hysteria2 添加 TCP 传输设置。

| 名称 | 类型 | 端口 | TLS 配置 | 认证 |
| --- | --- | --- | --- | --- |
| `anytls` | anytls | 8443/TCP | node-tls | 独立随机密码 |
| `hysteria2` | hysteria2 | 443/UDP | node-tls | 另一个独立随机密码 |
| `reality` | vless | 443/TCP | node-reality | 随机 UUID，flow=xtls-rprx-vision |

Hysteria2 首版不启用混淆和端口跳跃，不填写虚高带宽。若启用混淆，客户端类型和密码必须一致。

再创建客户端/用户并关联入站。不同协议若需要独立密码，可创建独立用户并分别关联相应入站。在入站的发布地址中填写 VPS 公网 IP 与外部端口。检查订阅的客户端出站配置不为空，否则可能不会出现在订阅中。原生字段参考 [服务端模板](../examples/server.json) 和 [客户端模板](../examples/client.json)。

**不要直接把这两个 JSON 文件导入 S-UI 数据库。** S-UI 另有用户、TLS 关联、发布地址和出站模板等面板对象，格式不同。[上游配置对象文档](https://github.com/alireza0/s-ui/wiki/Configuration-Objects)

## 6. 导出并验收

通过面板复制节点或导出客户端支持的配置。首次可在隧道内下载订阅再导入本地文件；需要手机长期自动刷新时另行提供 HTTPS 订阅入口，见 [客户端说明](clients.md)。

逐项完成 [验收清单](verification.md)。S-UI 健康检查通过仅表示面板监听正常，不代表三个协议都能连通。
