[toc]


## MySQL安装流程

能用的安装逻辑都放在 `install_mysql` 函数中，针对 replica | source 角色的特定操作放到上一层的函数中进行。

![](../imgs/install-mysql-source-replica-desgin.svg)

---
