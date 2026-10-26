# 把服务器配起来

这一步先把 S-UI 管理后台装好，再进去添加节点。证书和三种连接方式都要接着配置，不是运行完启动命令就全部完成了。

下面会分别写清楚哪些命令在服务器上运行，哪些在你自己的电脑上运行。如果让 AI 帮忙，也让它按这个顺序来。

## 1. 先看看服务器里有什么

先用 SSH 登录服务器，再运行下面几条命令。我们要看一下系统、Docker 是否可用，以及要用的端口有没有被其他服务占住。这里检查的是 VPS，不是你自己电脑上的 Docker。

```sh
uname -m
cat /etc/os-release
docker version
docker compose version
sudo ss -lntup
```

这份配置会用到 TCP 443、TCP 8443 和 UDP 443。如果已经有人在用，先弄清楚是什么服务，别直接停掉它。申请证书如果采用 HTTP-01 校验，还会用到 TCP 80。

服务商后台如果有防火墙或安全组，也要放行相应端口，SSH 的登录端口记得保留。Docker 的端口转发和普通入站规则不完全一样，所以不能只看 UFW 显示关闭，就认为外面一定连不进来。

## 2. 下载教程里的配置，启动后台

接着把仓库下载到服务器的 `/opt/sui-vps`。如果这里已经有同名目录，先检查里面是什么，不要直接覆盖。

如果刚才提示 Docker 或 Compose 不存在，要先安装好再继续。

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

最后一条会检查后台有没有开始监听。如果报错，先停在这里看原因，别急着继续添加节点。

以后用户和节点信息会保存在 `deploy/state/db`，证书放在 `deploy/state/cert`，不要随手删除这两个目录。容器里看到的证书路径是 `/app/cert`，后面填写时会用到。这里使用的具体版本放在 [版本清单](../versions.json)。

## 3. 从自己的电脑访问面板

现在回到你自己的电脑，另开一个终端。把 `my-vps` 换成你的 SSH 别名，运行：

```sh
ssh -N -L 12095:127.0.0.1:2095 -L 12096:127.0.0.1:2096 my-vps
```

这个终端先留着，不要关闭。它把你电脑上的入口接到了服务器后台。然后在电脑浏览器打开 `http://127.0.0.1:12095/app/`。

如果页面打不开，先看 SSH 连接是否还在。也可以在服务器终端运行下面的命令，查看实际入口和初始账号：

```sh
sudo docker compose -f /opt/sui-vps/deploy/compose.yaml exec s-ui ./sui uri
sudo docker compose -f /opt/sui-vps/deploy/compose.yaml exec s-ui ./sui admin -show
```

命令可能显示登录信息，自己看就好，不要贴到聊天或 Issue。第一次登录后，先把管理员用户名和密码改成自己的。

这里浏览器打开的是本机 HTTP 地址；电脑到服务器这一段由 SSH 加密，后台没有直接开放给公网。

## 4. 先把证书填好

AnyTLS 和 Hysteria2 会用到证书。先按 [证书说明](tls.md) 准备好，再回到 S-UI，添加下面两套 TLS 配置：

| 配置名 | 服务端 | 客户端订阅配置 |
| --- | --- | --- |
| `node-tls` | TLS 开启；证书 `/app/cert/fullchain.pem`；私钥 `/app/cert/privkey.pem` | TLS 开启；server_name 为证书覆盖的域名或 IP；insecure=false |
| `node-reality` | Reality 开启；独立私钥、short_id、握手地址/端口及匹配的 server_name | Reality 公钥、相同 short_id/server_name；uTLS 开启，fingerprint=chrome |

私钥留在服务器上，不要发给客户端。以后证书续期了，还得让服务读到新文件；这一步放在 [维护说明](maintenance.md) 里。

## 5. 添加三种连接方式

面板里说的“入站”，就是设备连接服务器的入口。新建三个入站，按下面填写，监听地址都设为 `0.0.0.0`。Hysteria2 用 UDP，不要给它套上 TCP 传输设置。

| 名称 | 类型 | 端口 | TLS 配置 | 认证 |
| --- | --- | --- | --- | --- |
| `anytls` | anytls | 8443/TCP | node-tls | 独立随机密码 |
| `hysteria2` | hysteria2 | 443/UDP | node-tls | 另一个独立随机密码 |
| `reality` | vless | 443/TCP | node-reality | 随机 UUID，flow=xtls-rprx-vision |

先用最少的设置把 Hysteria2 连通，混淆和端口跳跃暂时不用开，带宽也不要随便填一个很大的数字。以后如果加混淆，客户端还要填相同的类型和密码。

再创建客户端/用户并关联入站。不同协议若需要独立密码，可创建独立用户并分别关联相应入站。在入站的发布地址中填写 VPS 公网 IP 与外部端口。检查订阅的客户端出站配置不为空，否则可能不会出现在订阅中。原生字段参考 [服务端模板](../examples/server.json) 和 [客户端模板](../examples/client.json)。

**不要直接把这两个 JSON 文件导入 S-UI 数据库。** S-UI 另有用户、TLS 关联、发布地址和出站模板等面板对象，格式不同。[上游配置对象文档](https://github.com/alireza0/s-ui/wiki/Configuration-Objects)

## 6. 连上试试

通过面板复制节点或导出客户端支持的配置。首次可在隧道内下载订阅再导入本地文件；需要手机长期自动刷新时另行提供 HTTPS 订阅入口，见 [客户端说明](clients.md)。

接下来按 [检查清单](verification.md) 一项项测试。能打开 S-UI，只说明后台启动了；三种节点能不能用，还要在你的设备上分别连接一次。
