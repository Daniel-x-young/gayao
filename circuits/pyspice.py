# rc_filter.py
# RC低通滤波器 - 幅频特性仿真
# 理论截止频率 fc = 1/(2πRC) ≈ 1591.55 Hz

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. 创建电路
# ============================================================
circuit = Circuit('RC Low Pass Filter')

# 参数定义
R_value = 1@u_kΩ       # R = 1 kΩ
C_value = 100@u_nF     # C = 100 nF

# 添加元件
# R(编号, 节点1, 节点2, 阻值)
circuit.R(1, 'input', 'output', R_value)

# C(编号, 节点1, 节点2, 容值)
circuit.C(1, 'output', circuit.gnd, C_value)

# 添加交流电压源（用于AC分析）
# 幅度设为1V，方便直接读增益
circuit.SinusoidalVoltageSource('in', 'input', circuit.gnd, amplitude=1@u_V)

# ============================================================
# 2. 创建仿真器
# ============================================================
simulator = circuit.simulator(temperature=25, nominal_temperature=25)

# ============================================================
# 3. AC分析（扫频）
# ============================================================
# 从1Hz扫到1MHz，每十倍频程100个点
analysis = simulator.ac(
    start_frequency=1@u_Hz,
    stop_frequency=1@u_MHz,
    number_of_points=100,
    variation='dec'          # 'dec' = 每十倍频程
)

# ============================================================
# 4. 提取结果
# ============================================================
frequency = np.array(analysis.frequency)      # 频率数组
vout = np.array(analysis['output'])           # 输出电压（复数）
gain = np.abs(vout)                            # 幅值
gain_db = 20 * np.log10(gain)                 # 转成dB

# 计算仿真截止频率
# 找到最接近 -3dB 的频率点
idx = np.argmin(np.abs(gain_db - (-3)))
fc_sim = frequency[idx]
gain_at_fc = gain[idx]

# ============================================================
# 5. 打印结果
# ============================================================
print("=" * 50)
print("RC低通滤波器 - 仿真结果")
print("=" * 50)
print(f"理论截止频率:  {1/(2*np.pi*1000*100e-9):.2f} Hz")
print(f"仿真截止频率:  {fc_sim:.2f} Hz")
print(f"该点增益:      {gain_at_fc:.4f} ({20*np.log10(gain_at_fc):.2f} dB)")
print(f"误差:          {abs(fc_sim - 1591.55)/1591.55*100:.3f}%")

# 打印几个关键频率点的对比
print("\n" + "=" * 50)
print("关键频率点对比")
print("=" * 50)
print(f"{'频率(Hz)':<12}{'理论|H|':<12}{'仿真|H|':<12}{'误差':<10}")
print("-" * 50)

for f_test in [100, 1000, 1591.55, 10000]:
    # 理论值
    wRC = 2 * np.pi * f_test * 1000 * 100e-9
    h_theory = 1 / np.sqrt(1 + wRC**2)
    
    # 仿真值：找到最接近的频率点
    idx_test = np.argmin(np.abs(frequency - f_test))
    h_sim = gain[idx_test]
    
    error = abs(h_sim - h_theory) / h_theory * 100
    print(f"{f_test:<12.0f}{h_theory:<12.4f}{h_sim:<12.4f}{error:<10.3f}%")

# ============================================================
# 6. 画图
# ============================================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

# 上图：幅频特性（dB）
ax1.semilogx(frequency, gain_db, 'b-', linewidth=2)
ax1.axhline(y=-3, color='r', linestyle='--', alpha=0.7, label='-3dB')
ax1.axvline(x=1591.55, color='g', linestyle='--', alpha=0.7,
            label=f'理论 fc={1591.55:.0f}Hz')
ax1.axvline(x=fc_sim, color='orange', linestyle=':', alpha=0.7,
            label=f'仿真 fc={fc_sim:.0f}Hz')
ax1.set_xlabel('Frequency (Hz)', fontsize=12)
ax1.set_ylabel('Gain (dB)', fontsize=12)
ax1.set_title('RC Low Pass Filter - Bode Plot (Magnitude)', fontsize=14)
ax1.grid(True, which='both', alpha=0.3)
ax1.legend()

# 下图：幅频特性（线性）
ax2.semilogx(frequency, gain, 'b-', linewidth=2)
ax2.axhline(y=0.707, color='r', linestyle='--', alpha=0.7, label='0.707 (-3dB)')
ax2.axvline(x=1591.55, color='g', linestyle='--', alpha=0.7,
            label=f'理论 fc={1591.55:.0f}Hz')
ax2.set_xlabel('Frequency (Hz)', fontsize=12)
ax2.set_ylabel('Gain (linear)', fontsize=12)
ax2.set_title('RC Low Pass Filter - Frequency Response', fontsize=14)
ax2.grid(True, which='both', alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.savefig('rc_filter_bode.png', dpi=150)
print("\n波形图已保存为: rc_filter_bode.png")
plt.show()
