# 自建梯子与 IP 防泄露指南

自己买一台 VPS，搭一条自己用的线路。手机、电脑连上之后，再检查一遍：网站看到的到底是服务器的 IP，还是你家里的 IP。

这份教程会从买服务器开始，带你把线路配好，再把容易漏掉的地方检查一遍。不懂命令也可以把教程交给 AI，让它陪你操作。

> 教程还在完善。目前已经检查过配置，并测试了管理面板能否启动；新 VPS 和手机、电脑上的完整实测还没做。后面会照着教程从头跑一遍，把不好用、没讲清楚的地方补上。[查看进度](docs/verification.md)

## 1. 准备一台服务器

还没有 VPS 的话，可以先看看搬瓦工：

**[查看搬瓦工的套餐](https://bandwagonhost.com/aff.php?aff=82641)**

这是我的推广链接，通过它购买，我可能获得佣金。套餐价格、库存和退款条件以官网为准。你已经有服务器的话，先用现有的就好，不用再买一台。

这份教程按 Ubuntu 24.04 来准备。开通后，把服务器 IP、SSH 端口和登录方式记下来，后面会用到。拿不准怎么选，先看 [购买前要看什么](docs/buy-vps.md)。

## 2. 把线路配好

我们会用 S-UI 来管理节点。你可以把它理解成一个网页后台：以后加设备、换密码、看流量，都可以从这里操作。

服务器上会准备三种连接方式：**Reality、AnyTLS 和 Hysteria2**。名字先不用记，配好后在客户端里选对应的节点就行。Hysteria2 需要网络支持 UDP，所以也会保留 TCP 的连接方式，分别测试。

想自己动手，跟着 [部署教程](docs/deployment.md) 做。想让 AI 帮忙，就把下面这段话填好后发给它：

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

还没有 SSH 别名也没关系，可以告诉 AI 服务器 IP、用户名、端口和本机密钥文件的位置。初始密码请在自己的终端里输入，不要发在聊天里。

没有域名也能往下做，AnyTLS 和 Hysteria2 可以用签给服务器 IP 的证书。具体怎么申请、怎么续期，放在 [证书说明](docs/tls.md) 里。

## 3. 手机和电脑连上试试

在 S-UI 里导出节点，再导入支持对应协议的客户端。先一个节点一个节点地试，确认每条都能连上。[客户端怎么接入](docs/clients.md)

三个节点都在同一台服务器上。如果整台服务器断网，或者这个 IP 连不上，换节点也不一定有用。

## 4. 连上以后，再看有没有漏 IP

打开网页时显示服务器 IP，只说明这次网页请求走了代理。浏览器的通话功能、DNS 查询，或者电脑上的其他软件，也可能走了另一条路。

我们会接着检查四件事：

- **DNS**：查网址时，有没有意外走回本地网络。
- **IPv6**：IPv4 走了代理，IPv6 会不会还在直连。
- **WebRTC**：浏览器有没有把家里或手机网络的公网 IP 带出去。
- **断线**：节点连不上时，是停下来，还是悄悄改成直连。

不用一次弄懂这些名词，照着 [IP 防泄露检查](docs/leak-protection.md) 一项项看就好。里面也写了看到异常时先查哪里。

这里说的防泄露，是让你指定走代理的流量按预期走代理。主动设成直连的网站，仍然会看到本地 IP；登录账号的网站也仍然知道你是谁。

## 配好以后

- 想知道每一步有没有做完，看 [检查清单](docs/verification.md)。
- 要备份、升级，或者突然连不上了，看 [维护和排障](docs/maintenance.md)。
- 不想用网页后台，也可以 [直接运行 sing-box](docs/standalone.md)。

<details>
<summary>配置文件和开发检查</summary>

[部署配置](deploy/compose.yaml) · [服务端模板](examples/server.json) · [客户端模板](examples/client.json) · [版本清单](versions.json)

模板里的占位符需要替换。客户端模板目前只用于测试节点，没有配好 TUN 或断线保护，不能直接当作整台设备的防泄露方案。

```sh
python3 -m unittest discover -s tests -v
docker compose -f deploy/compose.yaml config --quiet
VALIDATE_CORE=1 python3 -m unittest discover -s tests -v
```

最后一条需要 Docker 和 OpenSSL。自动检查结果见 [GitHub Actions](https://github.com/makerkitt/vps-privacy-guide/actions/workflows/validate.yml)。

</details>

[MIT 许可证](LICENSE) · [第三方许可](NOTICE.md)
