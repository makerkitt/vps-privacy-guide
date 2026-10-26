# 客户端与订阅

本页先完成节点接入；随后按 [IP 防泄露检查](leak-protection.md) 验证客户端，不能把连接成功当作没有泄露。

服务端和客户端不必使用相同内核，但必须支持相同协议与参数。导入之前核对客户端具体版本是否支持 AnyTLS、Hysteria2、VLESS/Reality/Vision，以及所用订阅格式。不能因为能导入订阅就认为所有节点可用。

## S-UI 模式

1. 在面板创建用户、关联入站并填写公网发布地址。
2. 选择客户端支持的节点链接或订阅格式。S-UI 提供链接、sing-box JSON 和 Clash 等形式；具体协议能否导出需检查实际内容。
3. 保持 SSH 隧道开启时，可以把面板给出的本机订阅地址的主机/端口改为 `127.0.0.1:12096`，其余路径与凭据保持不变，再在自己的电脑下载。
4. 如果导出的节点地址是 `127.0.0.1` 或 Docker 地址，回面板修改入站发布地址；节点地址应该是 VPS 公网 IP，而不是订阅下载地址。
5. 手机不能把电脑上的 `127.0.0.1` 订阅当作自己的远程订阅使用。首次可以安全传输下载好的配置文件；远程自动刷新需要 HTTPS 订阅服务。

发布公网订阅时，另行配置 HTTPS 反向代理到回环 2096，使用可信证书和专用端口，隐藏含凭据的访问日志。TCP 443 已被 Reality 使用，不能再让 Nginx 简单占用同一个 IP 的 TCP 443。面板继续保持回环访问，不随订阅一起公开。

订阅链接相当于访问凭据。不要使用公开第三方订阅转换服务处理私人节点，也不要在 Issue 中粘贴订阅。

来源：[S-UI 订阅文档](https://github.com/alireza0/s-ui/wiki/Subscription-Service)。

## 原生 sing-box 模板

[examples/client.json](../examples/client.json) 是最小测试配置：仅开放本机 `127.0.0.1:1080` 的 HTTP/SOCKS 代理，默认选择 Reality。它没有启用 TUN、没有自动故障转移，也没有提供国内外 DNS/流量分流。

替换占位符后，可将 selector 的 `default` 分别改成 `reality`、`anytls`、`hysteria2`，重启客户端测试每条入口。客户端与服务端的 UUID、密码、Reality 公钥/short ID 必须配对；AnyTLS/Hysteria2 的 `server_name` 填证书覆盖的身份。

```sh
sing-box check -c private/client.json
sing-box run -c private/client.json
```

在另一个终端，用自己确认的 HTTPS 测试地址检查代理请求：

```sh
curl --proxy socks5h://127.0.0.1:1080 --max-time 20 https://example.com/
```

`socks5h` 会把目标域名交给代理侧解析。它只验证此请求经过代理，不代表整台电脑的其他程序、DNS 或 WebRTC 都经过代理。全设备接入需要另外配置客户端的 TUN/路由策略，并单独验收。

## 常见差异

- Hysteria2 使用 UDP；面板能打开、AnyTLS 能连通，都不能证明 UDP 已放行。
- Reality 不使用普通 TLS 证书路径，但要正确填写公钥、short ID、server_name 和 flow。
- IP 证书模式下，确保客户端能够按证书的 IP SAN 验证；不要通过跳过验证来掩盖参数错误。
- TCP/UDP 入口在同一台 VPS 上不会自动组成主备组；自动选择和切换应在客户端明确配置。
