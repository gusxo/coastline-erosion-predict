import math
from ReadConfig import ReadConfig

def calculate_parameters(parameters):
    result = {}
    for key, value in parameters.items():
        result[key] = value

    #delta
    exp_a = ((parameters["exp_gamma"] ** 2) * parameters["exp_f"] * parameters["exp_hb"] )/(16 * parameters["coast_angle"] * (parameters["exp_f"] - parameters["exp_hb"]**(1/2)))
    S_eq = (parameters["wave_energy_target"] - parameters["wave_energy_avg"])/exp_a
    result["delta"] = int(S_eq * 1000)

    #alpha
    init_sea_sediments = parameters["max_depth"] / math.tan(math.radians(parameters["coast_angle"])) * parameters["max_depth"] / 2
    predict_erosion_sediments = (parameters["max_depth"] + parameters["coast_height"]) * result["delta"]                #델타 값이 침식되는 경우 음수임, 따라서 이 변수 값이 보통 음수일것
    result["alpha"] = parameters["beta"] * (init_sea_sediments - 2 * predict_erosion_sediments) / init_sea_sediments
    result["alpha"] = result["alpha"] * result["alpha_weight"]                                                    #침식률 보정

    #gamma / theta / epsilon
    result["gamma"] = result["beta"]
    result["theta"] = parameters["theta"] * (parameters["cell_length"] / 1000)
    result["epsilon"] = parameters["epsilon"] * (parameters["cell_length"] / 1000)

    #pre_calculate
    result["erosion_amount"] = int(result["alpha"] * result["max_depth"])
    result["allow_sediments_diff"] = int(parameters["cell_length"] * math.tan(math.radians(result["allow_angle"])))
    result["toppling_change_value"] = int(result["allow_sediments_diff"] * parameters["rho"])

    #최소드랍비율에 기반하여 해안선으로 부터 몇칸까지만 활성화할지 계산
    #max[최소드랍비율 기반 범위, 해빈경사 기반 해저 모래 초기화 거리]
    cnt = 1
    erosion_transports = result["erosion_amount"]
    erosion_w1_min_drop_value = max([int((result["theta"] + result["epsilon"]) * erosion_transports * result["min_drop_weight"]), 1])
    while erosion_transports > 0:
        erosion_transports -= max([int(erosion_transports* (result["theta"] + result["epsilon"])), erosion_w1_min_drop_value])
        cnt += 1
    sea_sediments_length = int(parameters["max_depth"] / math.tan(math.radians(parameters["coast_angle"])) / parameters["cell_length"])
    result["active_range"] = max([cnt, sea_sediments_length ])+ 1

    return result

def ReadAndInitParmas(filepath):
    is_success, msg_or_parmas = ReadConfig(filepath)
    if not is_success:
        return False, msg_or_parmas

    inited_params = calculate_parameters(msg_or_parmas)
    return True, inited_params

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"usages : {sys.argv[0]} <config_file_path>")
        exit()
    filepath = sys.argv[1]
    is_success, result = ReadAndInitParmas(filepath)
    if is_success:
        print(f":: Read Config is Success!")
        print(f":: init parameters complete...")
        print(result)
    else:
        print(f":: Read Config is Failed...\n{result}")
