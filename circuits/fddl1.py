from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

# 创建电路
circuit = Circuit('NMOS Common Source Amplifier')

# 添加元件
circuit.V('DD', 'VDD', circuit.gnd, 5@u_V)
circuit.R(1, 'VDD', 'D', 3.3@u_kΩ)
circuit.R(2, 'G', circuit.gnd, 100@u_kΩ)
circuit.R(3, 'VDD', 'G', 100@u_kΩ)
circuit.R(4, 'S', circuit.gnd, 1@u_kΩ)

# NMOS 模型定义 (使用通用 NMOS 模型)
circuit.model('nmos_model', 'nmos', level=1, vto=1.0, kp=1e-3)

# 添加 NMOS (D, G, S, B, model)
circuit.M(1, 'D', 'G', 'S', circuit.gnd, model='nmos_model')

# 创建仿真器并运行直流工作点分析
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
op_analysis = simulator.operating_point()

# 打印结果
print("=== DC工作点仿真结果 ===")
print(f"V(G) = {float(op_analysis['G']):.4f} V")
print(f"V(D) = {float(op_analysis['D']):.4f} V")
print(f"V(S) = {float(op_analysis['S']):.4f} V")