# 自建梯子与 IP 防泄露指南

想自己管一条线路：买台小 VPS，把 Reality / AnyTLS / Hysteria2 配好，手机电脑连上，再确认网站看到的是服务器 IP，而不是家里或手机的。

**推荐做法是把本仓库交给 AI，让它按文档帮你部署。** 不会敲命令也没关系。没有 AI、或者你更想自己一步步做时，文末有手工文档。

> 教程还在完善。配置和面板启动已经查过；新机器和真机完整实测还没做。[查看进度](docs/verification.md)

## 做完之后手里会有什么

- 一台自己管的节点（S-UI 管 Reality、AnyTLS、Hysteria2）
- 网页后台：加设备、改密码、看流量
- 能导入手机 / 电脑客户端的节点
- 一套查漏 IP 的办法（DNS、IPv6、WebRTC、断线会不会直连）

## 谁更适合看这份教程

最对口的是：**需要自己的节点、对网络访问质量比较在意**的人——线路、账号、设备都想自己拿着。

机器按 **Ubuntu 24.04** 来写。要有独立公网 IPv4，能 SSH，能装软件；Hysteria2 还要能走 UDP。域名不是必须的，没有域名也可以用签给 IP 的证书，见 [证书说明](docs/tls.md)。

## 服务器：先买搬瓦工这台

教程按 **搬瓦工** 写。个人自用，先上这台季付促销就够用：

**SPECIAL 20G KVM PROMO V5 · CN2 GIA 电商优化** — **$49.99 / 三个月**，每月 **1TB**，大概够 **1～2 人** 日常。

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
    <img height="80" src="https://img.shields.io/badge/%E5%8A%A0%E5%85%A5%E8%B4%AD%E7%89%A9%E8%BD%A6-%2449.99%2F%E4%B8%89%E4%B8%AA%E6%9C%88%20%C2%B7%201TB-1677ff?style=for-the-badge&logo=shopping-cart&logoColor=white" alt="加入购物车 · $49.99/三个月 · 1TB">
  </a>
</p>

### [加入购物车（$49.99 / 三个月 · 1TB）](https://bandwagonhost.com/aff.php?aff=82641&pid=87)


为什么用搬瓦工：CN2 GIA / 电商线回国相对稳，季付好上手，机房选择多，面板和重装也成熟。代价也很实在——比杂牌贵，流量按月卡死在 1TB，1GB 内存别往上堆一堆无关服务。

下单时选好机房，系统选 **Ubuntu 24.04**。付完后把下面几项记下来（下一步要交给 AI）：

- IP 地址：
- SSH 端口：
- 用户名：
- 登录方式（密钥路径，或密码——密码只写在本机，不要贴进聊天）：
- SSH 别名（如果有）：

---

## 主路径：让 AI 部署

整体就是三件事：机器买好 → 把仓库和 SSH 信息交给 AI → 导入客户端并做防泄露检查。

### 需要准备给 AI 的信息

| 内容 | 怎么给 |
| --- | --- |
| 本仓库 | `https://github.com/makerkitt/vps-privacy-guide` |
| 怎么连上服务器 | 优先 SSH 别名；没有就写 IP、用户名、端口、本机私钥文件路径 |
| 你的设备 | 手机 / 电脑系统，以及打算用的客户端 |
| 证书 | 有域名写域名；没有就写「用公网 IP 证书」 |
| 机器现状 | 是不是全新；上面有没有网站或其他 Docker |

**密码、私钥内容、面板密码、订阅链接不要贴进聊天。** 需要登录时在自己的终端输入；敏感信息让 AI 写到本机或服务器上权限收紧的私有文件里。

### 配好之后，你应该拿到这些

1. S-UI 已在服务器跑着，以及怎么用本机 SSH 隧道打开面板  
2. Reality、AnyTLS、Hysteria2 三种节点都能导出 / 订阅  
3. 首次登录后如何改管理员密码（具体密码不会出现在聊天里）  
4. 连上之后怎么查 DNS、IPv6、WebRTC，以及断线后会不会直连  
5. 哪些步骤做完了、哪些还没实测——没测过的会直接说，不会假装全过  

### 安全上几条硬规矩

- 管理面板默认只听本机回环，用 SSH 隧道访问，不要直接暴露到公网。  
- AI 动手前先只读检查已有服务和端口；机器上已有业务时，不要直接重装或覆盖。  
- 节点密码、UUID、私钥在部署时新生成，教程里的占位符不能当真。  
- 这份教程管的是「该走代理的流量按预期走」；登录过的账号、你主动直连的网站，仍然知道你是谁。这不是「完全匿名」。

### 可以直接发给 AI 的一段话

把括号换成你的情况，整段发出去即可：

```text
请按这个教程帮我配置服务器：
https://github.com/makerkitt/vps-privacy-guide

先阅读 AGENTS.md 和 docs/pilot.md。
我的 SSH 别名：（填写，或改成 IP / 用户名 / 端口 / 本机密钥路径）
我要使用的设备和客户端：（例如 iPhone + xxx、Windows + xxx）
证书：（有域名写域名；没有就写「用公网 IP 证书」）

请先检查服务器上有没有其他服务，再开始配置。
使用 S-UI 管理 Reality、AnyTLS 和 Hysteria2。
密码、私钥和订阅链接只保存在私有文件里，不要显示在聊天中。
配好后，帮我检查 DNS、IPv6、WebRTC，以及断线后会不会直接联网。
教程里有缺少的步骤，请一起补上；没测过的地方请告诉我。
```

配好之后，按 [客户端怎么接入](docs/clients.md) 连设备，再按 [IP 防泄露检查](docs/leak-protection.md) 验一遍。

---

## 没有 AI 时：手工文档

1. [部署教程](docs/deployment.md)  
2. [证书说明](docs/tls.md)  
3. [客户端怎么接入](docs/clients.md)  
4. [IP 防泄露检查](docs/leak-protection.md)  
5. [检查清单](docs/verification.md)  

备份、升级、连不上：看 [维护和排障](docs/maintenance.md)。不想用网页后台：也可以 [直接运行 sing-box](docs/standalone.md)。

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
