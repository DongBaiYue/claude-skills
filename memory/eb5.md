# EB5 XPU 预训练

## 目标

- **功能支持**：实现 XPU 对 EB5 模型预训练的支持，Loss 曲线与 GPU 基线对齐
- **性能优化**：端到端训练效率达成 H800 的 30%

### 进度

- ✅ 性能分析：P800 达 H800 的 27%
- 🔄 性能优化中
  - paddle_xpu 仅大 shape 算子有收益（+4.5%）
  - 原因：`_C_ops._run_custom_op` 调用存在 100+us CPU 开销
- 📋 下一步：优化 paddle_xpu CPU 调度开销

## 目录结构

```
/root/paddlejob/workspace/env_run/liuyi39/
├── Paddle/                 # PaddlePaddle 框架源码
├── baidu/
│   ├── ernie/erniebot/     # EB5 训练代码
│   └── xpu/fast_paddle/    # paddle_xpu 插件源码
├── venv/                   # Python 虚拟环境
└── workspace/
    ├── eb5_xpu_profiler/   # XPU 环境变量对比实验
    └── profiler_xpu_gpu/   # GPU/XPU 算子级对比工具
```

**平台**：2机16卡昆仑 XPU

## paddle_xpu 架构

```
core/ops/           # C++ 算子后端 (paddle_xpu_nn)，纯计算不含权重
    ↓
paddle_xpu/layers/  # Python 前端，封装权重管理
    ↓
kernel_plugin/      # 底层 XPU kernel (.xpu → wrapper → 单测)
```

**新算子流程**：`core/ops/` 写 C++ → `paddle_xpu/layers/` 写 Python Layer → 补单测 → 更新 `doc/OPs.md`

**kernel_plugin 命名空间**：
- `KERNEL_NAMESPACE_BEGIN/END` → `PLUGIN_*`
- `xpu2` → `plugin_xpu2`
- 需手动 `namespace api = baidu::xpu::api;`

## GPU/XPU 算子对比

```bash
cd workspace/profiler_xpu_gpu/
python operator_profiler.py --top 10
python operator_profiler.py --outlier --outlier-threshold 20
```

输入：`gpu_0.json` / `xpu_0.json`（Chrome Trace Event），`operator_mapping.yaml`（算子别名映射）
