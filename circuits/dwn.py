# thevenin.py
# 戴维南定理验证
# 原始电路：Vin=10V, R1=10kΩ, R2=10kΩ, R3=10kΩ
# 等效电路：Vth=5V, Rth=15kΩ

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

print("=" * 50)
print("戴维南定理验证")
print("=" * 50)

# ============================================================
# 第一部分：原始电路
# ============================================================
print("\n【原始电路】")
print("Vin=10V, R1=10kΩ, R2=10kΩ, R3=10kΩ")

# --- 1.1 开路电压 ---
circuit1 = Circuit('Original Circuit - Open Load')
circuit1.V('in', 'n1', circuit1.gnd, 10@u_V)
circuit1.R(1, 'n1', 'n2', 10@u_kΩ)   # R1
circuit1.R(2, 'n2', 'n3', 10@u_kΩ)   # R2
circuit1.R(3, 'n2', circuit1.gnd, 10@u_kΩ)  # R3

sim1 = circuit1.simulator(temperature=25, nominal_temperature=25)
op1 = sim1.operating_point()

V_n1 = float(op1['n1'])
V_n2 = float(op1['n2'])
V_n3 = float(op1['n3'])

print(f"\n开路时节点电压：")
print(f"  V_n1 (Vin)  = {V_n1:.4f} V")
print(f"  V_n2 (节点A) = {V_n2:.4f} V")
print(f"  V_n3 (Vout)  = {V_n3:.4f} V")
print(f"\n  开路电压 V_th = {V_n3:.4f} V")
print(f"  理论值 V_th   = 5.0000 V")

# --- 1.2 接负载 RL=10kΩ ---
circuit1.R('L', 'n3', circuit1.gnd, 10@u_kΩ)  # 加负载

sim1b = circuit1.simulator(temperature=25, nominal_temperature=25)
op1b = sim1b.operating_point()

V_out_original = float(op1b['n3'])
print(f"\n接负载 RL=10kΩ 后：")
print(f"  原始电路 Vout = {V_out_original:.4f} V")
print(f"  理论值       = 2.0000 V")

# ============================================================
# 第二部分：戴维南等效电路
# ============================================================
print("\n【戴维南等效电路】")
print("Vth=5V, Rth=15kΩ")

# --- 2.1 开路电压 ---
circuit2 = Circuit('Thevenin Equivalent - Open Load')
circuit2.V('th', 'n1', circuit2.gnd, 5@u_V)
circuit2.R('th', 'n1', 'n2', 15@u_kΩ)

sim2 = circuit2.simulator(temperature=25, nominal_temperature=25)
op2 = sim2.operating_point()

V_th_eq = float(op2['n2'])
print(f"\n开路电压 V_th = {V_th_eq:.4f} V")

# --- 2.2 接负载 RL=10kΩ ---
circuit2.R('L', 'n2', circuit2.gnd, 10@u_kΩ)

sim2b = circuit2.simulator(temperature=25, nominal_temperature=25)
op2b = sim2b.operating_point()

V_out_thevenin = float(op2b['n2'])
print(f"\n接负载 RL=10kΩ 后：")
print(f"  等效电路 Vout = {V_out_thevenin:.4f} V")

# ============================================================
# 第三部分：对比验证
# ============================================================
print("\n" + "=" * 50)
print("【对比验证】")
print("=" * 50)

print(f"\n{'项目':<20} {'原始电路':<15} {'等效电路':<15} {'误差':<10}")
print("-" * 60)
print(f"{'开路电压':<20} {V_n3:<15.4f} {V_th_eq:<15.4f} {abs(V_n3-V_th_eq):<10.6f}")
print(f"{'接10kΩ负载':<20} {V_out_original:<15.4f} {V_out_thevenin:<15.4f} {abs(V_out_original-V_out_thevenin):<10.6f}")

print(f"\n结论：原始电路与戴维南等效电路在开路和接负载时输出一致，")
print(f"      戴维南定理验证通过。")

# ============================================================
# 第四部分：改变负载，验证更一般的情况
# ============================================================
print("\n" + "=" * 50)
print("【改变负载，进一步验证】")
print("=" * 50)

loads = [1, 5, 10, 20, 50, 100]  # kΩ
print(f"\n{'负载(kΩ)':<12} {'原始电路(V)':<15} {'等效电路(V)':<15} {'误差(V)':<10}")
print("-" * 55)

for RL in loads:
    # 原始电路
    c1 = Circuit('original')
    c1.V('in', 'n1', c1.gnd, 10@u_V)
    c1.R(1, 'n1', 'n2', 10@u_kΩ)
    c1.R(2, 'n2', 'n3', 10@u_kΩ)
    c1.R(3, 'n2', c1.gnd, 10@u_kΩ)
    c1.R('L', 'n3', c1.gnd, RL@u_kΩ)
    o1 = c1.simulator().operating_point()
    v1 = float(o1['n3'])
    
    # 等效电路
    c2 = Circuit('thevenin')
    c2.V('th', 'n1', c2.gnd, 5@u_V)
    c2.R('th', 'n1', 'n2', 15@u_kΩ)
    c2.R('L', 'n2', c2.gnd, RL@u_kΩ)
    o2 = c2.simulator().operating_point()
    v2 = float(o2['n2'])
    
    print(f"{RL:<12} {v1:<15.4f} {v2:<15.4f} {abs(v1-v2):<10.6f}")

print("\n所有负载下误差均接近 0，戴维南定理完全验证。")
