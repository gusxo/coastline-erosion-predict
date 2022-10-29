def ReadConfig(filepath):
    def bit2int(x):
        return int(x, 2)

    args = {
        "cell_length": [int, "cell_length", None],
        "coast_height": [int, "coast_height", None],
        "sea_max_depth": [int, "max_depth", None],
        "coast_angle": [float, "coast_angle", None],
        "allow_angle": [float, "allow_angle", None],
        "wave_energy_avg": [float, "wave_energy_avg", None],
        "wave_energy_target": [float, "wave_energy_target", None],
        "default_wave_dir": [bit2int, "default_wave_dir", None],
        "s2tr": [float, "beta", None],
        "reverse_drop": [float, "theta", None],
        "default_drop": [float, "epsilon", None],
        "min_drop_weight": [float, "min_drop_weight", None],
        "toppling_rate": [float, "rho", None],
        "exp_hb": [float, "exp_hb", None],
        "exp_f": [float, "exp_f", None],
        "exp_gamma": [float, "exp_gamma", None],
        "alpha_weight":[float, "alpha_weight", None],
    }

    try:
        f = open(filepath, "r")
    except Exception as e:
        return False, f"load config : file open failed :{e}"
    
    try:
        while True:
            line = f.readline()
            if not line:
                break
            words = line.split()
            if len(words) < 3:
                continue
            if words[0] != "set":
                continue
            if words[1] not in args:
                f.close()
                return False, f"load config : wrong parameter name : {words[1]}"
            try:
                func = args[words[1]][0]
                value = func(words[2])
                args[words[1]][2] = value
            except Exception as e:
                f.close()
                return False, f"load config : unmatch types : {words[1]} type is {func.__name__}, but input = {words[2]}"

    except Exception as e:
        f.close()
        return False, f"load config : file readline failed : {e}"

    f.close()
    result = {}
    #check all params is valid
    for key, value in args.items():
        if value[2] is None:
            return False, f"load config : not suplied parameters : {key}"
        real_params_name = value[1]
        result[real_params_name] = value[2]
    
    return True, result

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"usages : {sys.argv[0]} <config_file_path>")
        exit()
    filepath = sys.argv[1]
    is_success, msg = ReadConfig(filepath)
    if is_success:
        print(f":: Read Config is Success!")
    else:
        print(f":: Read Config is Failed...\n{msg}")
