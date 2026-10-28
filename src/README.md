# 构建研究用制品

以下命令在有 ARM 交叉编译支持的 Clang 和 Python 3 的机器上运行。它们只生成本地文件，不会连接或修改设备。

```sh
clang -target armv7-linux-gnueabi -c dhcp_filter.S -o dhcp_filter.o
python3 build_filter.py
python3 build_worker_bundle.py worker.jar /userconfig/h2-ap/filter 15000
```

`dhcp_filter` 依赖特定 ARM Linux 架构、设备私有 ioctl 和 `/proc/net/brport` 的格式。生成成功不代表适用于目标设备，也不等于设备端验证通过。`worker.jar` 需要目标设备的 Felix OSGi 环境，路径和接口名称是本次案例的值。

构建前请阅读主 README 的权限、兼容性和恢复说明。不要把本目录的构建输出自动设为 setuid 或复制到设备；应先完成设备识别、备份和受控测试。
