# TLS、IP 证书与 Reality

## AnyTLS / Hysteria2

两者都需要 TLS。可以用域名证书，也可以用证书 SAN 中覆盖 VPS 公网 IP 的证书。客户端的连接地址可以直接填 IP，`server_name` 必须与被验证的证书身份匹配；IP 身份无需伪造域名 SNI。

本项目不会默认关闭证书验证。自签证书只有在客户端明确安装信任或支持可靠的证书/公钥固定校验时才能作为可验证方案。

### 域名方式

使用自己控制的域名，配置 DNS 和 ACME 校验，申请覆盖该域名的证书。把完整证书链及私钥放入 `deploy/state/cert/`，客户端 `server_name` 填该域名。

### 不购买域名：IP 证书

Let's Encrypt 已提供公网 IP 证书，有效期 160 小时。可使用支持 `--ip-address` 的 Certbot（建议 5.4 或更高）；独立 HTTP 校验要求 VPS 的 TCP 80 可从公网到达且未被其他服务占用。

以下在 VPS 上执行，替换文档地址 `192.0.2.1`，先通过 Certbot 官方安装说明安装合适版本：

```sh
certbot --version
sudo certbot certonly --standalone --preferred-profile shortlived \
  --ip-address 192.0.2.1 --cert-name sui-vps
```

按提示输入自己的联系邮箱并阅读服务条款。若先在 staging 环境测试，其证书不被公网客户端信任，正式使用前需切换到生产签发。证书取得后：

```sh
sudo install -m 644 /etc/letsencrypt/live/sui-vps/fullchain.pem /opt/sui-vps/deploy/state/cert/fullchain.pem
sudo install -m 600 /etc/letsencrypt/live/sui-vps/privkey.pem /opt/sui-vps/deploy/state/cert/privkey.pem
```

这里复制证书而不是把单个 live 目录软链接挂入容器，避免链接目标在容器外。每次续期必须再次同步证书并重载服务；仅复制一次会在证书过期后断线。详见 [维护](maintenance.md)。

来源：[Let's Encrypt IP 证书](https://letsencrypt.org/2026/01/15/6day-and-ip-general-availability)、[Certbot IP 签发说明](https://letsencrypt.org/2026/03/11/shorter-certs-certbot)。

## Reality

本仓库使用常规 VLESS + Reality + Vision。握手目标选择能从 VPS 访问、符合 Reality 要求的 TLS 网站，客户端 `server_name` 与目标证书匹配。无需拥有目标域名；目标可达性和兼容性仍需实际测试。

在 S-UI 生成独立 Reality 密钥对、short ID 和 VLESS UUID。裸核心模式也可用 `sing-box generate reality-keypair`、`sing-box generate uuid` 与 `openssl rand -hex 8`。这些输出含私密参数，不上传 Git。

| 参数 | 服务端 | 客户端 |
| --- | --- | --- |
| UUID | 用户 UUID | 相同 UUID |
| Flow | xtls-rprx-vision | xtls-rprx-vision |
| Reality 密钥 | private_key | 配对的 public_key |
| short ID | short_id 数组 | 数组中一个值 |
| 握手目标 | 实际 TLS 网站与 443 | 配置匹配的 server_name |

`__REALITY_HANDSHAKE_SERVER__` 和 `__REALITY_SERVER_NAME__` 是必须选择并测试的目标，不要照抄文档保留域名作为真实目标。首版没有复刻参考项目的“IP 证书 + 本机 Reality 握手站点”设计。

来源：[sing-box Reality 配置](https://sing-box.sagernet.org/configuration/shared/tls/#reality-fields)。
