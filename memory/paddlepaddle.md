# PaddlePaddle 架构

## 核心组件

| 目录 | 说明 |
|------|------|
| `paddle/phi/kernels/` | kernel 实现（`cpu/`, `gpu/`, `xpu/`, `onednn/`）|
| `paddle/phi/infermeta/` | shape/dtype 推导 |
| `paddle/phi/ops/yaml/` | 算子 YAML 定义（`ops.yaml`, `backward.yaml`）|
| `paddle/phi/core/` | `DenseTensor`, `KernelFactory`, `KernelRegistry` |
| `paddle/fluid/eager/` | eager 运行时 + 代码生成器 |
| `paddle/fluid/pir/` | PIR dialect、passes、transforms |
| `paddle/fluid/primitive/` | 组合算子分解规则 |

## 执行模式

**Eager**：`_C_ops` → generated eager fn → PHI API → PHI kernel

**Static**：PIR Program → `pd_op_to_kernel_pass` → device kernel

## YAML → 代码生成

| 生成器 | 产出 |
|--------|------|
| `phi/api/yaml/generator/api_gen.py` | `phi/api/lib/api.cc` |
| `fluid/eager/.../eager_gen.py` | `dygraph_functions.cc`, `nodes.cc` |
| `fluid/pybind/.../python_c_gen.py` | `eager_op_function.cc` |

修改 YAML 后执行 `make api_gen` 或完整 `make` 重新生成。

## 添加新算子

1. `paddle/phi/ops/yaml/ops.yaml` + `backward.yaml` 添加定义
2. `paddle/phi/infermeta/` 写 InferMeta 函数
3. `paddle/phi/kernels/{cpu,gpu}/` 实现 kernel，`PD_REGISTER_KERNEL` 注册
4. 代码生成器自动产出 C++ API / Python 绑定
5. `python/paddle/tensor/` 添加 Python 封装，`test/` 补测试

## PHI Kernel 注册与选择

**KernelKey**：Backend(bit 0-7) / DataLayout(bit 8-11) / DataType(bit 12-19) 哈希为 32-bit

**注册**：`PD_REGISTER_KERNEL` → `KernelRegistrar` → `KernelFactory::InsertKernel()`

**选择（Eager）**：`ParseKernelKeyByInputArgs` → YAML 覆盖 → 6 步 fallback（GPUDNN→目标 backend→CPU）→ `PrepareData`

```bash
GLOG_vmodule=phi_kernel_adaptor=4 python test.py   # 调试 kernel 选择
```

关键文件：`phi/core/kernel_registry.h`, `phi/core/kernel_factory.h/.cc`

## 组合算子

~1061 个原生算子 → ~200 个 primitive 算子，降低新硬件/分布式适配成本。

- 前向：`fluid/primitive/composite/composite.h` 实现 → `register.h` 注册
- 反向 VJP：`fluid/primitive/rule/vjp/details.h` 实现 → `REGISTER_VJP_INTERFACE` 注册
- 数值敏感算子用 CustomVJP 复用前向输出
