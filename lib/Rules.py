import numpy as np
from .Utils import get_neighboor8

#아래 main 함수 내에서 운송물 이동 시 추락값 및 전송값 계산용
#return : (next_sediments_value, drop_value)
def calculate_drop_value(sediments_value, init_sediments_value, parameters, wave_dir, transport_dir):
  default_drop_rate = parameters["epsilon"]
  #파도 정방향과 90도 이상 차이나면 역방향
  is_reverse_dir = int(wave_dir & transport_dir == 0) 
  #역방향 아니면 0으로 세팅됨
  reverse_dir_drop_rate = parameters["theta"] * is_reverse_dir
  
  real_min_drop_value = int(parameters["min_drop_weight"] * init_sediments_value * (default_drop_rate + reverse_dir_drop_rate))
  sediments_drop_value = int(sediments_value * (default_drop_rate + reverse_dir_drop_rate))
  
  drop_value = max([real_min_drop_value, sediments_drop_value, 1])
  drop_value = min([drop_value, sediments_value])
  
  return (sediments_value - drop_value, drop_value)
  
#CA main rule
def rule_main(mat, r, c, steps, parameters):
  cell = mat.item((r,c))
  if cell["state"] == "wall":
    #벽은 다른 CA함수도 관여안하므로, 액티브셀에서 제거함.
    parameters["active_cells"][r,c] = False
    return {"state":"wall"}

  result = {}
  #hard copy
  for key, val in cell.items():
    result[key] = val
    
  #이함수 자체에서는 필요없지만, 토플링 함수를 안전하게 굴리기 위해 명시적으로 재 초기화함
  result["tmp_send_transports"] = [0] * 8
  
  nbs = get_neighboor8(mat, r, c, 0b11111111)
  
  direction_in_mask = [0b0010, 0b0011, 0b0001, 0b1001, 0b1000, 0b1100, 0b0100, 0b0110] #이웃 i번 셀이 자신을 가리킬때의 dir mask
  direction_out_mask = [0b1000, 0b1100, 0b0100, 0b0110, 0b0010, 0b0011, 0b0001, 0b1001] #자신이 이웃 i번 셀을 가리키는 dir mask
  transport_dir_in = [None] * 8       #이웃 i번의 weight[i] 이 셀을 가리킨다.
  for i in range(8):
    transport_dir_in[(i+4)%8] = i
    
  ##### recv part : 주변 이웃에게서 자신에게 보내는 transport_list를 '추락값' 빼고 가져옴.
  #####           : 주변의 '바다'에게서는 자신에게 가중치가 있을 시, 새로 만들어진 '운송' 퇴적물도 가져옴.
  #####           : 주변의 '지상'에게서는 자신이 바다이고, 대상에게 가중치를 보낼때 한정으로 '침식값'을 가져옴.(추락 1회 적용 후 가져옴.)
  recv_transport_list = []
  recv_weight = [0] * 8
  recv_flag = [False] * 8
      
  
  for i in range(8):
    nb = nbs[i]
    if nb is None:
      continue
    if nb["state"] == "wall":
      continue
      
    recv_weight[i] = nb["weight"][transport_dir_in[i]]
    
    if nb["state"] == "sea":
      # 1
      for ts in nb["transport_list"]:
        ts_dir = ts["transport_dir"]
        if ts_dir == direction_in_mask[i]:
          recv_sedim, _ = calculate_drop_value(ts["sediments"], ts["init_sediments"], parameters, nb["wave_dir"], ts_dir)
          if recv_sedim > 0:
            recv_transport_list += [{"sediments":recv_sedim, "transport_dir":ts_dir, "init_sediments":ts["init_sediments"]}]
            recv_flag[i] = True
              
      # 2
      recv_sedim = int(nb["sediments"] * recv_weight[i] * 0.001 * parameters["gamma"])
      if recv_sedim > 0:
        recv_transport_list += [{"sediments":recv_sedim, "transport_dir":direction_in_mask[i], "init_sediments":recv_sedim}]
        recv_flag[i] = True
    # 3
    if nb["state"] == "ground" and cell["state"] == "sea":
      send_weight = cell["weight"][i]
      if send_weight > 0:
        erosion_value = int(parameters["erosion_amount"] * send_weight * 0.001)
        recv_sedim, _ = calculate_drop_value(erosion_value, erosion_value, parameters, nb["wave_dir"], direction_in_mask[i])
        recv_transport_list += [{"sediments":recv_sedim, "transport_dir": direction_in_mask[i], "init_sediments":erosion_value}]
    
  ##### send part : 바다는 자신의 셀에서 일정량이 '운송'상태가 되어 사라짐.
  if cell["state"] == "sea":
    for i in range(8):
      lost = int(cell["weight"][i] * 0.001 * cell["sediments"] * parameters["gamma"])
      if lost > 0:
        result["sediments"] -= lost
      
  ##### send part : 지상은 퇴적물을 1개라도 받은 경우, 침식당한다. 단, 운송리스트는 생성하지 않는다.
  # (가져가는 셀이 만들어서 가져감, 지상에서 만들면 지상에서 운송물 모두 추락이랑 겹쳐서 문제생김)
  if cell["state"] == "ground":
    for i in range(8):
      if recv_flag[i]:
        erosion_value = int(parameters["erosion_amount"] * recv_weight[i] * 0.001)
        send_value, _ = calculate_drop_value(erosion_value, erosion_value, parameters, cell["wave_dir"], direction_out_mask[i])
        result["sediments"] -= send_value
      
  ##### send part : 자신 셀에 있는 운송 리스트에 대해서 다음 수행
  # 보내는 곳이 벽일 경우 : 자신 셀에 모두 추락
  # 자신이 지상일 경우 : 자신 셀에 모두 추락
  # else : 일정량 추락시킴
  # 이후 다른건 다른 셀에서 연산할 것임.
  for ts in cell["transport_list"]:
    ts_dir = ts["transport_dir"]
    ts_sedim = ts["sediments"]
    #자신이 지상
    if cell["state"] == "ground":
      result["sediments"] += ts_sedim
      continue
      
    #목표가 벽
    target_nbs_index = 0
    for i in range(8):
      if direction_out_mask[i] == ts_dir:
        target_nbs_index = i
        break
        
    if nbs[target_nbs_index] is not None:
      if nbs[target_nbs_index]["state"] == "wall":
        result["sediments"] += ts_sedim
        continue
        
    #아닐시 추락
    _, drop_value = calculate_drop_value(ts_sedim, ts["init_sediments"], parameters, cell["wave_dir"], ts_dir)
    result["sediments"] += drop_value
    
  #이제 임시저장한 recv_transport_list를 다음 step의 transport_list로 갱신시켜줌
  result["transport_list"] = recv_transport_list
  
  return result
  

#시작 : 처음에 어떻게든 각도 벗어난놈들 찾아서, 더 높은 셀을 탐색 대상에 넣는다.
#이후 아래 함수에선 다음을 수행한다.
# - 주변 8방향에서 자신에게 보내는걸 받아옴
# - 근처 8방향으로 보낼 양을 계산하고 저장함
# - 보내는 셀은 다음 탐색 대상으로 삼음.
def rule_toppling(mat, r,c ,steps, parameters):
  result = {}
  #hard copy
  for key, val in mat[r,c].items():
    result[key] = val
  cell = mat[r,c]
  if cell["state"] == "wall":
    return result

  nbs = get_neighboor8(mat, r, c, 0b11111111)
  transport_dir_in = [None] * 8       #이웃 i번의 tmp_transports[i] 또는 weight[i] 이 셀을 가리킨다.
  for i in range(8):
    transport_dir_in[(i+4)%8] = i

  add_r = [-1, -1, 0, 1, 1, 1, 0, -1]
  add_c = [0, -1, -1, -1, 0, 1, 1, 1]

  
  nbs_sedim = []
  nbs_send = [0] * 8
  nbs_index = []

  for i in range(8):
    if nbs[i] is None:
      continue
    if nbs[i]["state"] == "wall":
      continue
    #이웃이 벽 아니면 일단 이웃 번호랑 sediments 받아옴
    nbs_sedim += [nbs[i]["sediments"]]
    nbs_index += [i]
      
    #이웃이 보내는 sediments 받아옴
    #바로 직전 토플링 함수로 보낸게 아니면 무시해야됨.
    if "tmp_send_timing" not in nbs[i]:
      continue
    if nbs[i]["tmp_send_timing"] + 1 != steps:
      continue

    recv_sedim = nbs[i]["tmp_send_transports"][transport_dir_in[i]]
    if recv_sedim > 0:
      result["sediments"] += recv_sedim

  #토플링 적용
  while True:
    #유효한 이웃들과의 모래량 차이를 계산한다. 결과가 음수인 경우는 이 셀보다 더 높은 셀로, 관여하지 않는다.
    #(이 구간은 모래를 보내는 입장에서만 생각한다.)
    diff = np.array([result["sediments"] - nbs_sedim[i] for i in range(len(nbs_sedim))])
    max_index = np.argmax(diff)
    #차이가 가장 큰 셀에 대해서만 생각하고 나머지는 다음 루프로 넘긴다.
    if diff[max_index] > parameters["allow_sediments_diff"]:
      send_value =  parameters["toppling_change_value"]
      result["sediments"] -= send_value             #보낸 퇴적물은 바로 뺌
      nbs_sedim[max_index] += send_value            #받는 쪽은 임시 저장된 배열에서만 수정함
      nbs_send[nbs_index[max_index]] += send_value  #실제 적용은 다음 step에서 처리될 것임.
    else:
      break #차이가 가장 큰 셀이 안식각 규칙 적용 필요없는 경우, 루프 탈출함.   

  #다음 방문지 저장
  for i in range(8):
    if nbs_send[i] > 0:
      parameters["tmp_toppling_target"][r+add_r[i], c+add_c[i]] = True

  #nbs_send 값 실제로 저장
  result["tmp_send_transports"] = nbs_send
  #중복 전송 방지용
  result["tmp_send_timing"] = steps
  
  #change_state
  #sea -> ground
  if result["state"] == "sea" and result["sediments"] >= parameters["max_depth"]:
    result["state"] = "ground"
  #ground -> sea
  elif result["state"] == "ground" and result["sediments"] < parameters["max_depth"]:
    result["state"] = "sea"
    #주변 (7 x 7 범위) 셀을 active에 포함함
    parameters["active_cells"][max([0, r-3]):r+4, max([0,c-3]):c+4] = True

  return result