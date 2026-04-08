---
name: reference-index
description: 参考文档索引，指向 memory/ 目录下的详细文档
---

# 参考文档索引

## PaddlePaddle 架构

**文件**: `memory/paddlepaddle.md`

- 核心组件目录说明
- Eager/Static 执行模式
- YAML → 代码生成流程
- 添加新算子步骤
- PHI Kernel 注册与选择机制
- 组合算子分解

**触发**: 修改 Paddle 源码、添加算子、调试 kernel 选择

---

## EB5 XPU 预训练

**文件**: `memory/eb5.md`

- 项目目标与进度
- 目录结构
- paddle_xpu 插件架构
- kernel_plugin 命名约定
- GPU/XPU 算子对比工具

**触发**: EB5 训练、XPU 性能调优、paddle_xpu 开发
