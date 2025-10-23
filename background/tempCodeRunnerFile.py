se case
    print('Base Case')
    print(CONSTANTS)
    Fs, Ts, B_sensor = calcSys(CONSTANTS)
    print(f'F_magnet_z {Fs["magnets"][2]:.3f} | F_EMon_z {Fs["EMon"][2]:.3f} | F_g {Fg:.3f} | sum {Fs["magnets"][2] + Fs["EMon"][2] + Fg:.3f}')
    print(f'restoring moment (care magnitude) {Ts["magnets"][1] + Ts["EMon"][1]:.5f}')
    print(f'F_destabilize_x {Fs["magnets"][0]:.4f} | F_stabilize_x {Fs["EMon"][0]:.4f} | ratio (small better) {Fs["magnets"][0]/Fs["EMon"][0]:.3f}')
    print(f'Sens