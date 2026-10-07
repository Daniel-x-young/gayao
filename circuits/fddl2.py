from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import matplotlib.pyplot as plt

# 创建电路
circuit = Circuit('NMOS Common Source Amplifier Transient')

# 添加元件
circuit.V('DD', 'VDD', circuit.gnd, 5@u_V)
circuit.R(1, 'VDD', 'D', 3.3@u_kΩ)
circuit.R(2, 'G', circuit.gnd, 100@u_kΩ)
circuit.R(3, 'VDD', 'G', 100@u_kΩ)
circuit.R(4, 'S', circuit.gnd, 1@u_kΩ)

# 正弦输入信号源
circuit.SinusoidalVoltageSource(1, 'G', circuit.gnd, 
                                 dc_offset=2@u_V, 
                                 amplitude=10@u_mV, 
                                 frequency=1@u_kHz)

# NMOS 模型定义
circuit.model('nmos_model', 'nmos', level=1, vto=1.0, kp=1e-3)

# 添加 NMOS
circuit.M(1, 'D', 'G', 'S', circuit.gnd, model='nmos_model')

# 创建仿真器并运行瞬态分析
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
transient_analysis = simulator.transient(step_time=10@u_us, end_time=5@u_ms)

# 绘制波形
plt.figure(figsize=(10, 6))
plt.plot(transient_analysis.time * 1000, transient_analysis['G'], label='V(G)')
plt.plot(transient_analysis.time * 1000, transient_analysis['D'], label='V(D)')
plt.xlabel('Time (ms)')
plt.ylabel('Voltage (V)')
plt.title('NMOS Common Source Amplifier Transient Response')
plt.legend()
plt.grid(True)
plt.show()