---
name: commands
description: 常用命令速查表
---

# 常用命令速查

## 环境配置

```bash
PROJECT_ROOT=/root/paddlejob/workspace/env_run/liuyi39

# 网络代理
export http_proxy=http://agent.baidu.com:8188 && export https_proxy=$http_proxy

# Paddle 开发模式（无需安装）
export PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT/Paddle/build/python
```

## 仓库克隆与构建

```bash
# PaddleFormers
git clone https://github.com/PaddlePaddle/PaddleFormers.git
cd PaddleFormers && pip install -e .

# Paddle GPU 版
git clone https://github.com/PaddlePaddle/Paddle.git -b develop
cd Paddle && mkdir build && cd build
pip install -r ../python/requirements.txt && pip install wheel
cmake .. -DPY_VERSION=3.10 -DWITH_GPU=ON -DCMAKE_BUILD_TYPE=Release -DWITH_TESTING=OFF -DWITH_DISTRIBUTE=ON -DCUDA_ARCH_NAME=Manual -DCUDA_ARCH_BIN="80"
make -j16

# Paddle XPU 版（cmake 与 GPU 不同，其余相同）
cmake .. -DPY_VERSION=3.10 -DCMAKE_BUILD_TYPE=Release -DWITH_GPU=OFF -DWITH_XPU=ON -DON_INFER=OFF -DWITH_PYTHON=ON -DWITH_MKL=OFF -DWITH_XPU_BKCL=ON -DWITH_DISTRIBUTE=ON -DWITH_XPU_XRE5=ON -DWITH_XPTI=OFF
make -j16                 # 完整构建
make -j16 copy_libpaddle  # 增量（只更新 .so）
ctest -R "test_name" --output-on-failure
```

## paddle_xpu 构建

```bash
cd $PROJECT_ROOT/baidu/xpu/fast_paddle
bash scripts/build.sh && pip install dist/paddle_xpu-0.0.1-py3-none-any.whl -I
bash scripts/rebuild.sh  # 增量重建
```

## EB5 训练

```bash
# 检查 XPU 残留进程
mpirun xpu-smi 2>/dev/null | grep -A 3 "Processes"
# 有残留则清理
mpirun pkill -9 -f pretrain.py

# 启动训练
cd $PROJECT_ROOT/baidu/ernie/erniebot
bash debug.sh && tail -f run.log
```

## 代码风格

```bash
pre-commit run --files $(git diff --name-only)
```

## 更多参考

详细文档见 `$PROJECT_ROOT/memory/` 目录：
- PaddlePaddle 架构/构建 → `$PROJECT_ROOT/memory/paddlepaddle.md`
- EB5 XPU 训练 → `$PROJECT_ROOT/memory/eb5.md`
