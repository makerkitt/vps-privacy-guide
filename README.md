# 自建梯子与 IP 防泄露指南

自己买一台 VPS，搭一条自己用的代理线路；手机、电脑连上后，再检查网站看到的到底是服务器 IP，还是你家 / 手机的 IP。

> 教程还在完善。配置和面板启动已做过检查；新 VPS 与真机完整实测还没做。[查看进度](docs/verification.md)

## 跟完教程，你能得到什么

按步骤做完后，你手里会有一套**自己掌控**的个人线路：

| 你得到的 | 具体是什么 |
| --- | --- |
| 一台可用的个人节点服务 | 在 VPS 上用 S-UI 管着 **Reality、AnyTLS、Hysteria2** 三种连接方式（TCP / UDP 都有备份路径） |
| 一个网页管理后台 | 以后加设备、换密码、看流量，不用每次 SSH 改配置 |
| 手机 / 电脑能连上 | 从面板导出节点，导入客户端，逐条确认能上网 |
| 一套防泄露检查方法 | 对照查 **DNS、IPv6、WebRTC、断线后会不会偷跑直连** |
| 后续怎么养着它 | 备份、升级、连不上时怎么排障的文档入口 |

简单说：跟完之后，你有自己的服务器、自己的面板、自己的节点，以及一套把常见漏 IP 点查清楚的方法。

## 适合谁、要准备什么

- **最适合**：需要**自己的节点**、对网络访问有要求的人——不想完全依赖别人机场，希望线路、账号、设备都在自己手里管。
- **也适合**：愿意自己买一台小 VPS，并能接受跟着文档（或让 AI 陪着）把服务配起来的人。
- **系统**：按 **Ubuntu 24.04** 写的；需要独立公网 IPv4、能 SSH、能装软件，且允许使用 UDP（Hysteria2 需要；另外两种走 TCP）。
- **域名**：现在可以没有。AnyTLS / Hysteria2 也能用签给服务器 IP 的证书，见 [证书说明](docs/tls.md)。
- **已有服务器**：也可以直接用现有机器跟着部署；没有的话，先买下面这台就够了。

## 先准备一台服务器

本教程按 **搬瓦工** 来写。个人自用先买这台就行——**$49.99 / 三个月，每月 1TB 流量**，大概够 **1～2 人** 日常上网；开通后装 Ubuntu 24.04，就能接着往下配。

| | |
| --- | --- |
| 硬盘 | 20 GB SSD |
| 内存 | 1 GB |
| CPU | 2 核 |
| 带宽 | 2.5 Gbps |
| 流量 | **1 TB / 月** |
| 价格 | **$49.99 / 三个月** |
| 适合 | **1～2 人** 自用 |
| 线路 | CN2 GIA 电商优化（多机房可选） |

<p align="center">
  <a href="https://bandwagonhost.com/aff.php?aff=82641&pid=87">
    <img src="https://img.shields.io/badge/%E5%8A%A0%E5%85%A5%E8%B4%AD%E7%89%A9%E8%BD%A6-%2449.99%2F%E4%B8%89%E4%B8%AA%E6%9C%88%20%C2%B7%201TB-1677ff?style=for-the-badge&logo=shopping-cart&logoColor=white" alt="加入购物车 · $49.99/三个月 · 1TB">
  </a>
</p>

<p align="center">
  <a href="https://bandwagonhost.com/aff.php?aff=82641&pid=87"><strong>👉 一键加入购物车（$49.99 / 三个月 · 1TB）</strong></a>
</p>

点进去会直接进搬瓦工下单页。选好机房，系统选 **Ubuntu 24.04**，付完记下 IP 和 SSH 登录信息，就可以去部署了。更细的购买注意点见 [购买前要看什么](docs/buy-vps.md)。

## 怎么走完（两条路）

1. **买 / 准备服务器**（上面那台，或你已有的机器）  
2. **把线路配好** → [部署教程](docs/deployment.md)（或下面「让 AI 帮忙」）  
3. **手机电脑连上** → [客户端怎么接入](docs/clients.md)  
4. **查有没有漏 IP** → [IP 防泄露检查](docs/leak-protection.md)

### 路径 A：自己动手

打开 [部署教程](docs/deployment.md)，按顺序做。卡在证书时看 [证书说明](docs/tls.md)。

### 路径 B：让 AI 帮忙

把下面填好后发给 AI（先让它读约定，再动服务器）：

```text
请按这个教程帮我配置服务器：
https://github.com/makerkitt/vps-privacy-guide

先阅读 AGENTS.md 和 docs/pilot.md。
我的 SSH 别名：填写这里
我要使用的设备和客户端：填写这里

请先检查服务器上有没有其他服务，再开始配置。
使用 S-UI 管理 Reality、AnyTLS 和 Hysteria2。
密码、私钥和订阅链接只保存在私有文件里，不要显示在聊天中。
配好后，帮我检查 DNS、IPv6、WebRTC，以及断线后会不会直接联网。
教程里有缺少的步骤，请一起补上；没测过的地方请告诉我。
```

没有 SSH 别名也可以，改成告诉它 IP、用户名、端口和本机密钥路径。**初始密码在自己的终端里输入，不要发在聊天里。**

## 连上以后：漏 IP 要查什么

网页显示服务器 IP，只说明**这一次网页请求**走了代理。浏览器通话、DNS、或其他软件仍可能另走一条路。至少查这四项：

- **DNS** — 解析有没有绕回本地运营商  
- **IPv6** — IPv4 走了代理，IPv6 会不会还在直连  
- **WebRTC** — 浏览器有没有带出家里 / 手机的公网 IP  
- **断线** — 节点挂了是停住，还是悄悄改成直连  

照着 [IP 防泄露检查](docs/leak-protection.md) 一项项做即可。

## 配好以后

- 进度与勾选清单：[检查清单](docs/verification.md)  
- 备份、升级、连不上：[维护和排障](docs/maintenance.md)  
- 不想用网页后台：[直接运行 sing-box](docs/standalone.md)

<details>
<summary>配置文件和开发检查</summary>

[部署配置](deploy/compose.yaml) · [服务端模板](examples/server.json) · [客户端模板](examples/client.json) · [版本清单](versions.json)

模板里的占位符需要替换。客户端模板目前只用于测试节点，没有配好 TUN 或断线保护，不能直接当作整台设备的防泄露方案。

```sh
python3 -m unittest discover -s tests -v
docker compose -f deploy/compose.yaml config --quiet
VALIDATE_CORE=1 python3 -m unittest discover -s tests -v
```

最后一条需要 Docker 和 OpenSSL。自动检查见 [GitHub Actions](https://github.com/makerkitt/vps-privacy-guide/actions/workflows/validate.yml)。

</details>

[MIT 许可证](LICENSE) · [第三方许可](NOTICE.md)
