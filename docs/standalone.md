# 不使用面板

可以独立运行 sing-box，不必安装 S-UI。此模式使用 [server.json](../examples/server.json)，管理方式是编辑配置和使用 systemd。部署目标仍需 SSH、可信证书、三组节点凭据及防火墙设置。

## 与面板模式二选一

如果已有 S-UI，先备份并决定是否迁移；不要直接覆盖其数据库或启动另一个核心抢占端口。S-UI 的用户、TLS 和节点对象不是完整的 sing-box JSON，需要导出或重新整理。

## 配置准备

1. 根据 [官方安装说明](https://sing-box.sagernet.org/installation/package-manager/) 安装与 [versions.json](../versions.json) 对应的核心。
2. 将 `examples/server.json` 复制到被 Git 忽略的 `private/server.json`；文件权限设为 600。
3. 为 AnyTLS、Hysteria2 分别生成随机密码；生成 VLESS UUID 和 Reality 密钥对、short ID。
4. 替换全部 `__占位符__`，证书路径填写核心进程能读取的真实路径，Reality 目标按 [TLS 文档](tls.md) 选择。
5. 配对填写 `private/client.json`，客户端只放公钥，不放服务端私钥。

```sh
umask 077
mkdir -p private
cp examples/server.json private/server.json
cp examples/client.json private/client.json
chmod 600 private/server.json private/client.json
```

以上 `cp` 仅用于首次创建，已有私有配置时不要重复覆盖。使用本地编辑器填入凭据，避免在共享终端记录或聊天中显示。

## 校验和运行

```sh
sing-box check -c private/server.json
```

通过后，将配置安装到包管理器服务使用的位置。先用 `systemctl cat sing-box` 核对该发行版实际 `ExecStart` 和配置路径，再安装；常见位置为 `/etc/sing-box/config.json`。

```sh
sudo install -d -m 700 /etc/sing-box
sudo install -m 600 private/server.json /etc/sing-box/config.json
sudo systemctl enable --now sing-box
sudo systemctl status sing-box --no-pager
```

上面假设服务读取该路径且这是首次安装。已有服务应先备份，修改后执行 `systemctl restart sing-box`；`enable --now` 不会让已运行进程自动加载新配置。证书文件必须对服务实际运行用户可读，不能为省事把私钥设成全员可读。

## 维护差异

没有网页后台、配额自动停用和订阅生成服务。增加用户需要修改配置；证书续期后要让 sing-box 加载新文件。备份配置、密钥和证书到仓库之外，并完成与面板模式同样的三协议端到端验收。
