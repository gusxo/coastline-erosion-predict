def ReadConfig(filepath):
    def bitmask(x):
        return int(x, 2)

    args = {
        "cell_length": [int, "cell_length", None],
        "coast_height": [int, "coast_height", None],
        "sea_max_depth": [int, "max_depth", None],
        "coast_angle": [float, "coast_angle", None],
        "allow_angle": [float, "allow_angle", None],
        "wave_energy_avg": [float, "wave_energy_avg", None],
        "wave_energy_target": [float, "wave_energy_target", None],
        "default_wave_dir": [bitmask, "default_wave_dir", None],
        "s2tr": [float, "beta", None],
        "reverse_drop": [float, "theta", None],
        "default_drop": [float, "epsilon", None],
        "min_drop_weight": [float, "min_drop_weight", None],
        "toppling_rate": [float, "rho", None],
        "exp_hb": [float, "exp_hb", None],
        "exp_f": [float, "exp_f", None],
        "exp_gamma": [float, "exp_gamma", None],
        "alpha_weight": [float, "alpha_weight", None],
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

def ReadCompareConfig(filepath):
    def bitmask(x):
        return int(x, 2)

    result = [{
        "line_min_length":0, 
        "line_size":1, 
        "before":[1,0,0],
        "after":[0,1,0],
        "compare":[1,1,0]
        }]

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
            try:
                #그리기 옵션일경우 별도 처리
                if words[1] == "line_min_length":
                    value = int(words[2])
                    if value < 0:
                        raise Exception(f"line_min_length는 0 이상을 요구함 : {value}")
                    result[0]["line_min_length"] = value
                    continue
                elif words[1] == "line_size":
                    value = int(words[2])
                    if value < 1:
                        raise Exception(f"line_size는 1 이상을 요구함 : {value}")
                    result[0]["line_size"] = value
                    continue
                elif words[1] == "line_color":
                    if len(words) < 6:
                        raise Exception(f"선 색상 지정을 위한 인수가 모두 제공되지 않음 : {line}")
                    line_type = words[2]
                    r = int(words[3])
                    g = int(words[4])
                    b = int(words[5])
                    if line_type != "before" and line_type != "after" and line_type != "compare":
                        raise Exception(f"line_color_type : {line_type}은 유효한 값이 아님")
                    if r < 0 or r > 255:
                        raise Exception(f"R color value : 0~255 값이여야함 : {r}")
                    if g < 0 or g > 255:
                        raise Exception(f"G color value : 0~255 값이여야함 : {g}")
                    if b < 0 or b > 255:
                        raise Exception(f"B color value : 0~255 값이여야함 : {b}")
                    r = r / 255
                    g = g / 255
                    b = b / 255
                    result[0][line_type] = [r,g,b]
                    continue
                #위 목록에 안걸릴 경우, 좌표 입력으로 판단함
                if len(words) < 5:
                    raise Exception(f"좌표 입력을 위한 최소한의 인수가 제공되지 않음 : {line}")
                row = int(words[1])
                col = int(words[2])
                if row < 0 and col < 0:
                    raise Exception("<row> 와 <col> 둘 다 wildcard로 지정할 수 없습니다.")
                dir_type = words[3]
                if dir_type != "string" and dir_type != "bitmask":
                    raise Exception("<direction_type>은 반드시 string 또는 bitmask여야 합니다.")
                dir_value = 0
                if dir_type == "string":
                    valuelen = len(words[4])
                    for i in range(valuelen):
                        if words[4][i] == "N" or words[4][i] == "n":
                            dir_value |= 0b1000
                        elif words[4][i] == "S" or words[4][i] == "s":
                            dir_value |= 0b0010
                        elif words[4][i] == "W" or words[4][i] == "w":
                            dir_value |= 0b0100
                        elif words[4][i] == "E" or words[4][i] == "e":
                            dir_value |= 0b0001
                elif dir_type == "bitmask":
                    dir_value = bitmask(words[4])
                if dir_value == 0:
                    raise Exception("<direction_value> : 방향이 지정되지 않음")
                elif (dir_value & 0b1010) == 0b1010:
                    raise Exception("<direction_value> : 북/남 방향이 동시에 지정됨")
                elif (dir_value & 0b0101) == 0b0101:
                    raise Exception("<direction_value> : 동/서 방향이 동시에 지정됨")

                wildcard_rule = "all"
                if len(words) >= 6:
                    wildcard_rule = words[5]

                if (wildcard_rule != "all" and wildcard_rule != "min" and wildcard_rule != "max" and wildcard_rule != "mean"):
                    raise Exception(f"<wildcard_rule> : {words[5]}은 유효한 값이 아님")

                result += [[row, col, dir_value, wildcard_rule]]

            except Exception as e:
                f.close()
                return False, f"load config : failed read value : {e}"

    except Exception as e:
        f.close()
        return False, f"load config : file readline failed : {e}"

    f.close()    
    return True, result
