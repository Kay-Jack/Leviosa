data = list(CONSTANTS.values()) + [
        Fs["magnets"][2], 
        Fs["EMon"][2], 
        Fg, 
        Fs["magnets"][2] + Fs["EMon"][2] + Fg, 
        -(Ts["magnets"][1] + Ts["EMon"][1]),
        Fs["magnets"][0],
        Fs["EMon"][0],
        Fs["EMon"][0] + Fs["magnets"][0],
        ]