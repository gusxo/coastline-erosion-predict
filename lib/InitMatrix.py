import numpy as np
import math
from Utils import range_check, get_neighboor, get_neighboor8
from InitParams import calculate_parameters

### matrix to obj system
def to_object_type(x):
  y = np.zeros_like(x, dtype=object)
  for r in range(x.shape[0]):
    for c in range(x.shape[1]):
      if x[r,c] == 0:
        y[r,c] = {"state":"ground", "sediments":0, "transport_list":[], "wave_dir":0, "tmp_send_transports":[0]*8, "recv_weight":0}
      elif x[r,c] == 1:
        y[r,c] =  {"state":"sea", "sediments":0, "transport_list":[], "wave_dir":0, "tmp_send_transports":[0]*8, "recv_weight":0}
      elif x[r,c] == 2:
        y[r,c] = {"state":"wall"}
  return y

#파도/가중치 초기화
def wave_weight_recv(mat):
  cnt = mat.shape[0] * mat.shape[1]
  results = [0] * cnt

  direction_in_mask = [0b0010, 0b0011, 0b0001, 0b1001, 0b1000, 0b1100, 0b0100, 0b0110] #이웃 i번 셀이 자신을 가리킬때의 dir mask
  ##### 메모 : in_mask와 '일치'하면 정확히 자신을 가리키는 것이고, 불일치하지만 bitwise_and 가 TRUE일 경우엔 방향이 1칸 틀린 케이스임
  ##### 이웃8방향 번호 순서 : 북 부터 반시계 회전
  transport_dir_in = [None] * 8       #이웃 i번의 tmp_transports[i] 또는 weight[i] 이 셀을 가리킨다.
  for i in range(8):
    transport_dir_in[(i+4)%8] = i

  for i in range(cnt):
    r, c = i // mat.shape[1], i % mat.shape[1]

    #벽은 가중치 연산에서 제외됨
    if mat[r,c]["state"] == "wall":
      continue

    #recv wave
    nbs = get_neighboor8(mat, r, c, 0b11111111)
    results[i] = {}

    #파도 시작위치일 경우 가중치 1로 시작
    if "wave_starting_point" in mat[r,c]:
      results[i]["recv_weight"] = 1000
      results[i]["wave_dir"] = mat[r,c]["wave_dir"]
      continue
   
    
    tmp_recv = np.array([0] * 8)
    tmp_origin_recv = np.array([0] * 8)
    
    for j in range(8):
      if nbs[j] is None:
        continue
      if nbs[j]["state"] == "wall":
        continue

      #weight가 undefined일 가능성이 있음.
      if "weight" in nbs[j]:
        w = nbs[j]["weight"][transport_dir_in[j]]
      else:
        w = 0
      
      if w > 0:
        tmp_recv[j] += w
        tmp_recv[(j+1)%8] += w
        tmp_recv[j-1] += w
        tmp_origin_recv[j] = w

    
    max_recv_weight_index = np.argmax(tmp_recv)
    max_recv_weight = np.max(tmp_recv)
    if sum(tmp_recv == max_recv_weight) > 1:
      max_recv_weight_index = np.argmax(tmp_origin_recv)
      
    results[i]["recv_weight"] = tmp_recv[max_recv_weight_index]
    results[i]["recv_weight"] = min([results[i]["recv_weight"], 1000])
    if results[i]["recv_weight"] > 0:
      results[i]["wave_dir"] = direction_in_mask[max_recv_weight_index]
    else:
      results[i]["wave_dir"] = 0
    
    
    

  #결과는 마지막에 한번에 대입함.
  for i in range(cnt):
    if results[i] != 0:
      r, c = i // mat.shape[1], i % mat.shape[1]
      mat[r,c]["recv_weight"] = results[i]["recv_weight"]
      mat[r,c]["wave_dir"] = results[i]["wave_dir"]

  return


#파도/가중치 초기화 - 가중치 전송
def wave_weight_send(mat):
  cnt = mat.shape[0] * mat.shape[1]
  results = [0] * cnt

  direction_out_mask = [0b1000, 0b1100, 0b0100, 0b0110, 0b0010, 0b0011, 0b0001, 0b1001] #자신이 이웃 i번 셀을 가리키는 dir mask

  for i in range(cnt):
    r, c = i // mat.shape[1], i % mat.shape[1]

    #벽은 가중치 연산에서 제외됨
    if mat[r,c]["state"] == "wall":
      continue
      
    if mat[r,c]["recv_weight"] < 1:
      results[i] = [0] * 8
      continue
      
    cell = mat[r,c]
    nbs = get_neighboor8(mat, r,c,0b11111111)
    #이웃들에게 보낼 에너지의 가중치 계산
    weight = [0] * 8 

    #자신의 파도방향에 따른 초기값
    for j in range(8):
      if direction_out_mask[j] == cell["wave_dir"]:
        front_idx = j
        left_idx = (j+7)%8
        right_idx = (j+1)%8
        lli = (j+6)%8
        rri = (j+2)%8
        front = nbs[front_idx]["state"] if nbs[front_idx] is not None else "sea"
        left = nbs[left_idx]["state"] if nbs[left_idx] is not None else "sea"
        right = nbs[right_idx]["state"] if nbs[right_idx] is not None else "sea"
        ll =  nbs[lli]["state"] if nbs[lli] is not None else "sea"
        rr =  nbs[rri]["state"] if nbs[rri] is not None else "sea"

        weight[front_idx] = int(cell["recv_weight"] // 3)
        weight[left_idx] = int(cell["recv_weight"] // 3)
        weight[right_idx] = int(cell["recv_weight"] // 3)

        wall_param = 0.9    #벽 부딪힐때 파쇄 파라미터

        #벽이나 고립에 따른 가중치 변동
        if front == "wall":
          weight[left_idx] += int((weight[front_idx] / 2) * wall_param)
          weight[right_idx] += int((weight[front_idx] / 2) * wall_param)
          weight[front_idx] = 0
        
        if left == "wall":
          weight[front_idx] += int((weight[left_idx] / 2)  * wall_param)
          weight[lli] +=  int((weight[left_idx] / 2)  * wall_param)
          weight[left_idx] = 0
        
        if right == "wall":
          weight[front_idx] += int((weight[right_idx] / 2)* wall_param)
          weight[rri] += int((weight[right_idx] / 2)* wall_param)
          weight[right_idx] = 0
          
        if front == "wall":
          weight[front_idx] = 0

        #정방향이 좌표상 대각선 방향이면 고립 체크
        if (front_idx & 1) and left == "wall" and right == "wall":
          weight[lli] += int((weight[front_idx] / 2) * wall_param)
          weight[rri] += int((weight[front_idx] / 2) * wall_param)
          weight[front_idx] = 0

        #사이드방향이 좌표상 대각선 방향일 때 고립 체크
        if not (front_idx & 1) and front == "wall" and ll == "wall":
          weight[lli] += int(weight[left_idx] * wall_param)
          weight[left_idx] = 0
        if not (front_idx & 1) and front == "wall" and rr == "wall":
          weight[rri] += int(weight[right_idx] * wall_param)
          weight[left_idx] = 0

        if ll == "wall":
          if front != "wall":
            weight[front_idx] += int(weight[lli] * wall_param)
          weight[lli] = 0
        
        if rr == "wall":
          if front != "wall":
            weight[front_idx] += int(weight[rri] * wall_param)
          weight[rri] = 0

    #가중치 저장
    results[i] = weight

  #결과는 마지막에 한번에 대입함.
  for i in range(cnt):
    if results[i] != 0:
      r, c = i // mat.shape[1], i % mat.shape[1]
      mat[r,c]["weight"] = results[i]

  return



#지도 초기화 과정에서, 해안선 셀 리스트를 받아 거기서부터 지상 방향으론 1칸, 바다 방향으론 n칸 액티브 셀에 저장함
def init_active_cells(mat,parameters, coastline_cells):
  coastline_cells = list(coastline_cells)
  active_cells = np.zeros((mat.shape[0], mat.shape[1]),dtype=bool)
  active_range = int(parameters["active_range"])
  
  for r, c in coastline_cells:
    #인접 n칸에 대해서, 다넣음
    active_cells[max([0, r-active_range]):r+active_range+1, max([0, c-active_range]):c+active_range+1] = True
    
  #지상지역은 한번 다 빼주기
  target_cells = np.where(active_cells)
  for i in range(len(target_cells[0])):
    r = target_cells[0][i]
    c = target_cells[1][i]
    active_cells[r,c] = (mat[r,c]["state"] == "sea")
    
  #해안선 근처 지역 다시 넣어주기
  for r, c in coastline_cells:
    active_cells[max([0, r-1]):r+2, max([0, c-1]):c+2] = True
    
  parameters["active_cells"] = active_cells
  return




### 지도 초기화
def matrix_init(mat, parameters):
  ##### find coastline cell & init sediments value #####  
  # 해안선 위치의 퇴적물값
  coastline_cell_sediments = int(parameters["max_depth"])
  # 각도에 따라 셀 1칸당 퇴적물값 변화량 계산
  # 삼각비를 이용하여 셀 1칸 거리를 밑변으로 삼아 높이를 계산
  radian = math.radians(parameters["coast_angle"])
  diff_sediments = int(parameters["cell_length"] * math.tan(radian))
  #모든 지상셀 일단 최고높이로 초기화
  for r in range(mat.shape[0]):
    for c in range(mat.shape[1]):
      if mat[r,c]["state"] == "ground":
        mat[r,c]["sediments"] = int(parameters["coast_height"] + parameters["max_depth"])

  #모든 지상셀 중에서 해안선 찾기 & 적용
  for r in range(mat.shape[0]):
    for c in range(mat.shape[1]):
      if mat[r,c]["state"] == "ground":
        #지상 셀일 경우, 이웃을 다 가져와 바다 셀이 있는지 확인함.
        neighboors = get_neighboor(mat, r, c, 0b1111)
        flag = False
        for neighboor in neighboors:
          if neighboor is not None:
            if neighboor["state"] == "sea":
              flag = True

        add_r = [-1, 0, 1, 0]
        add_c = [0, -1, 0, 1]
        #해안선 셀일 경우, 높이 변경하고 상하좌우 셀들로 높이 변경을 시도함
        #지상 셀 방향으로는 최소값이 유효하고, 바다 셀 방향으로는 최대값이 유효함.
        if flag:
          mat[r,c]["sediments"] = coastline_cell_sediments
          for i in range(4):
            if neighboors[i] is None:
              continue
            bitmask_val = 0b1000 >> i
            target_state = neighboors[i]["state"]
            is_ground = int(target_state == "ground")
            diff_sign = (is_ground << 1) - 1 # true는 1이 되고 false 는 -1이 됨
            target_r = r
            target_c = c
            while True:
              target = get_neighboor(mat, target_r, target_c, bitmask_val)
              target = target[0]
              if target is None:
                break
              if target["state"] != target_state or target["state"] == "wall":
                break
              if is_ground:
                target["sediments"] = int(min([target["sediments"], mat[target_r, target_c]["sediments"] + diff_sediments * diff_sign]))
              else:
                target["sediments"] = int(max([target["sediments"], mat[target_r, target_c]["sediments"] + diff_sediments * diff_sign]))

              target_r = target_r + add_r[i]
              target_c = target_c + add_c[i]

  #외각지역 기본 파도방향 설정 : 파라미터 값 잇을시 그쪽 방향만 활성화
  if parameters["default_wave_dir"] is not None:
    # 북쪽
    if parameters["default_wave_dir"] & 0b0010:
      for obj in mat[0,:]:
        if obj["state"] != "wall":
          obj["wave_dir"] = parameters["default_wave_dir"]
          obj["wave_starting_point"] = 1
    #서쪽
    if parameters["default_wave_dir"] & 0b0001:
      for obj in mat[:,0]:
        if obj["state"] != "wall":
          obj["wave_dir"] = parameters["default_wave_dir"]
          obj["wave_starting_point"] = 1
    #남쪽
    if parameters["default_wave_dir"] & 0b1000:
      for obj in mat[-1, :]:
        if obj["state"] != "wall":
          obj["wave_dir"] = parameters["default_wave_dir"]
          obj["wave_starting_point"] = 1
    #동쪽
    if parameters["default_wave_dir"] & 0b0100:
      for obj in mat[:, -1]:
        if obj["state"] != "wall":
          obj["wave_dir"] = parameters["default_wave_dir"]
          obj["wave_starting_point"] = 1
  else:
    #북쪽
    for obj in mat[0,:]:
      if obj["state"] != "wall":
        obj["wave_dir"] = obj["wave_dir"] | 0b0010
        obj["wave_starting_point"] = 1
    #서쪽
    for obj in mat[:,0]:
      if obj["state"] != "wall":
        obj["wave_dir"] = obj["wave_dir"] | 0b0001
        obj["wave_starting_point"] = 1
    #남쪽
    for obj in mat[-1,:]:
      if obj["state"] != "wall":
        obj["wave_dir"] = obj["wave_dir"] | 0b1000
        obj["wave_starting_point"] = 1
    #동쪽
    for obj in mat[:,-1]:
      if obj["state"] != "wall":
        obj["wave_dir"] = obj["wave_dir"] | 0b0100
        obj["wave_starting_point"] = 1

  return mat



#맵 크기를 1/4로 줄이고, 그에 맞게 파라미터 추가 조정후 새로운 값으로 반환
#지도의 sediment 초기화(matrix_init)까지만 하고 실행해야 함.(다른 추가 초기화함수 수행후면 예상불가)
def map_downsize(mat, parameters):
  #작아지는 크기에 따른 맵 크기(소수점 올림)
  m,n = (int(math.ceil(mat.shape[0]/2)), int(math.ceil(mat.shape[1]/2)))
  
  #새 파라미터 저장소 생성
  new_param = {}
  #hard copy
  for key, val in parameters.items():
    new_param[key] = val
  #
  #파라미터 변경
  #theta와 epsilon을 파라미터 계산함수 호출 전으로 되돌리고, cell_length를 수정한 후 재실행
  new_param["theta"] = new_param["theta"] * (1000 / new_param["cell_length"])
  new_param["epsilon"] = new_param["epsilon"] * (1000 / new_param["cell_length"])
  new_param["cell_length"] *= 2
  new_param = calculate_parameters(new_param)
  
  #새로운 매트릭스 생성
  result = np.zeros((m,n)).astype(mat.dtype)
  
  for r in range(m):
    for c in range(n):
      value = {}
      refers = []
      #result[r,c] 에 저장할 mat의 2x2 범위 모두 가져옴, 범위 밖은 안가져옴
      for i in range(4):
        target_r = r*2 + i//2
        target_c = c*2 + i%2
        if range_check(target_r, target_c, mat.shape):
          refers += [mat[target_r, target_c]]
      #refers에 저장된 정보들을 바탕으로 새로운 셀의 값을 정함. 이론상 1/2/4개 들어올 수 있음

      #refers에 1개만 들어온경우 : 그대로 붙여넣기
      if len(refers) == 1:
        #hard copy
        for key, val in refers[0].items():
          value[key] = val

      #refers에 2 or 4개 들어온 경우 : 
      elif len(refers) == 2 or len(refers) == 4:
        wall_count = 0
        total_sedim = 0
        wave_starting_point = 0
        wave_dir = 0
        value["transport_list"] = []
        value["tmp_send_transports"] = [0]*8
        value["recv_weight"] = 0

        #refers 정보 합산
        for ref in refers:
          if ref["state"] == "wall":
            wall_count += 1
            continue
          if "wave_starting_point" in ref:
            wave_starting_point += 1
          wave_dir |= ref["wave_dir"]
          total_sedim += ref["sediments"]
        
        #wall_count가 50% 이상이면 벽
        #아닐시 sediment기반으로 결정
        if wall_count >= (len(refers)//2):
          value["state"] = "wall"
        else:
          avg_sedim = int(round(total_sedim / (len(refers) - wall_count)))
          value["state"] = "sea" if avg_sedim < new_param["max_depth"] else "ground"
          value["sediments"] = avg_sedim
          value["wave_dir"] = wave_dir
          if wave_starting_point > 0:
            value["wave_starting_point"] = 1
      #case들에 따라 결정된 value를 실제 위치에 대입
      result[r,c] = value

  return result, new_param

