# 本地独立复现

使用上传的 motor/ 和 Release 2 的 environment/ 原始代码，没有修改肌肉参数、身体模型、初始静置流程或输入。

输入：support/motor_experiments_20261013/walk_1khz/open_loop_program.npz，5000×78，1 kHz；物理积分 10 kHz。执行原始 SixLegMNBackend.step 接口，开始前验证 graph_sha256、body_ids、R、q_reference。安装隔离虚拟环境 .venv，FlyGym 2.1.0、MuJoCo 3.9.0；完整版本见 requirements-frozen.txt。

先运行未修改的 examples/replay_walk.py，写 original_interface_report.json。再运行 render_replay.py 录制独立第二次回放。两次回放与存档 public_replay.json 的全部报告字段完全一致。视频250帧，50fps，覆盖完整5秒；另有0.25倍速20秒版。重放轨迹保存 reproduced_trajectory.npz；报告 reproduced_report.json。渲染检查 qpos 和 warmstart 未被改变，没有姿态修正、重置或轨迹拟合。

5秒前进59.32284245193584mm，最低身体竖直度0.9875809546847888。平地短序列达标，不代表扰动恢复或长期自主步态。输入为离线拟合的预定 MN 序列，并非 MaleCNS 自主产生。原有50ms位置控制静置在行走计时之前；行走阶段无在线位置伺服、CPG或黏附。

运行：
```bash
MUJOCO_GL=egl OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
PYTHONPATH=/workspace/server-motor-import/motor:/workspace/server-motor-import/support/malecns_simulation_core_20261013/environment \
/workspace/server-motor-import/.venv/bin/python /workspace/server-motor-import/reproduced/render_replay.py
```

当前旧A/B双文件模型未改动。
