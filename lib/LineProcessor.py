import numpy as np
import math
from collections import deque
import matplotlib.pyplot as plt

# 점 두개 사이를 보간함
# p1 : 시작 점, [x, y] 로 이루어짐
# p2 : 끝 점, [x, y] 로 이루어짐
# return value : (n, 2) 형태의 numpy array
def interporation(p1, p2, step):
  x1, y1 = p1
  x2, y2 = p2
  dx = x2 - x1
  dy = y2 - y1
  #두 점 사이의 거리
  diff = math.sqrt(math.pow(dx,2) + math.pow(dy, 2))
  
  # 두 점 사이의 각도 계산
  radian = math.atan2(dy, dx)
  #print(f'interporation([{x1}, {y1}], [{x2}, {y2}], {step}) : diff is {diff}')
  #print(f'interporation([{x1}, {y1}], [{x2}, {y2}], {step}) : degrees is {math.degrees(radian)}')
  
  #루프 반복 횟수, (x2, y2)와 동일 지점에 보간하는걸 막기 위해 정수 나누기 대신 (ceil 후 -1) 사용
  loop_n = math.ceil(diff/step) - 1
  result = np.zeros((2 + loop_n, 2))
  
  result[0, 0] = x1
  result[0, 1] = y1
  result[-1, 0] = x2
  result[-1, 1] = y2
  
  for i in range(1, loop_n+1):
    # (n * step , 0) 을 회전 변환 함
    qx = math.cos(radian) * (i * step) - math.sin(radian) * (0)
    qy = math.sin(radian) * (i * step) + math.cos(radian) * (0)
    # qx, qy에 시작 점(x1, y1)을 더해 보간될 위치로 이동
    qx += x1
    qy += y1
    #저장
    result[i, 0] = qx
    result[i, 1] = qy
    
  return result

def interporation_points(a, step):
  #a : 좌표들이 저장된 (n, 2) 형태의 numpy array들로 구성된 List
  #step : 보간 간격
  #return value : 보간된 (k, 2) 형태의 numpy array
  
  #gca = plt.gca()
  inters = None
  for i in range(len(a)):
    for j in range(1, len(a[i])):
      inter = interporation(a[i][j-1], a[i][j], step)
      if inters is None:
        inters = inter
      else:
        inters = np.concatenate([inters, inter], axis = 0)
  #gca.scatter(inters[:,0], inters[:,1], color='dodgerblue', s = 0.1)
  return inters

def to_grid(a, x_range = None, y_range = None):
  #a : 좌표들이 저장된 (n, 2) 형태의 numpy array
  #x_range : grid화 시킬 x 범위, (begin, end) 형태의 tuple.
  #          begin과 end는 정수일 것
  #          default = None, None일 시 최소/최대 값으로 자동 지정
  #y_range : grid화 시킬 y 범위, (begin, end) 형태의 tuple.
  #          begin과 end는 정수일 것
  #          default = None, None일 시 최소/최대 값으로 자동 지정
  #return value : (x_range.end - x_range.begin, y_range.end - y_range.begin) 형태의 numpy array
  #               value가 1일 경우 a 에 저장되어있던 좌표 지점이며, 아닐 시 0
  if x_range is None:
    x_range = (int(np.min(a[:,0])), int(np.max(a[:,0]) + 1))
  if y_range is None:
    y_range = (int(np.min(a[:,1])), int(np.max(a[:,1]) + 1))
  print(f'to_grid() : a.shape : {a.shape} / x_range : {x_range} / y_range : {y_range}')
  
  #range 값에 따라 저장할 matrix 생성
  #  !!  range 입력 값이 정수가 아니거나, 다른 형식일 시 여기서 에러발생
  mat = np.zeros((x_range[1] - x_range[0], y_range[1] - y_range[0])).astype(int)
  print(f'to_grid() : matrix shape : {mat.shape}')
  
  for i in range(a.shape[0]):
    x = int(a[i, 0])
    y = int(a[i, 1])
    #범위 벗어나는지 체크
    if (x < x_range[0]) or (x >= x_range[1]) or (y < y_range[0]) or (y > y_range[1]):
      continue
    
    #matrix는 zero-based이므로 begin만큼 빼줌
    x -= x_range[0]
    y -= y_range[0]
    
    mat[x,y] = 1
    
  return mat, x_range, y_range

def paint_bfs(target_mat, starting_point, paint_value):
  #bfs ready
  queue = deque()
  target_mat[starting_point[0], starting_point[1]] = paint_value
  queue.append(starting_point)
  #start bfs
  while(len(queue) > 0):
    cur_x, cur_y = queue.popleft()
    next_case = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for nx, ny in next_case:
      next_x = cur_x + nx
      next_y = cur_y + ny
      if(next_x >= 0 and next_x < target_mat.shape[0] and next_y >= 0 and next_y < target_mat.shape[1]):
        if(target_mat[next_x, next_y] == 0):
          queue.append((next_x, next_y))
          target_mat[next_x, next_y] = paint_value
  #bfs end
  return

def painting(mat):
  #mat 과 동일한 shape의 배열을 반환함
  #mat에서 값이 0인 영역들을 찾아내, (mat 최대값 + 1) 이상의 값들로 채움
  #두번째 반환값은 영역갯수
  
  #hard copy
  result = mat.copy()
  maxval = np.max(mat)
  paint_value = maxval + 1
  
  for x in range(mat.shape[0]):
    for y in range(mat.shape[1]):
      if(result[x,y] == 0):
        paint_bfs(result, (x,y), paint_value)
        paint_value += 1
        
  #색칠한 영역 갯수
  area_cnt = paint_value - 1 - maxval
  return result, area_cnt

def find_shortest_points(dmat, n, max_diff):
  distance = None
  points = None
  line_a = None
  line_b = None
  for i in range(n):
    for j in range(n):
      if i==j:
        continue
      #점 연결 케이스
      for point_a in dmat[i]:
        for point_b in dmat[j]:
          tmp_distance = math.sqrt(math.pow(point_a[0]-point_b[0],2)+math.pow(point_a[1]-point_b[1],2))
          if (distance is None):
            if tmp_distance <= max_diff:
              distance = tmp_distance
              points = [point_a, point_b]
              line_a = i
              line_b = j
          elif distance > tmp_distance and tmp_distance <= max_diff:
            distance = tmp_distance
            points = [point_a, point_b]
            line_a = i
            line_b = j
  if distance is None:
    return None, None, None
  else:
    return np.array(points), line_a, line_b

def concat_line(a, max_diff):
  #a : 좌표들이 저장된 (n, 2) 형태의 numpy array들로 구성된 List
  #max_diff : line간의 거리가 max_diff 이하일때만 연결함
  
  n = len(a)
  print(f'concat_line : input line {n}개')
  #각 LINE의 시작점과 끝점만 추출해서 저장함
  #(n)(dots)(2) 형태의 nested list, 3차원에는 x좌표, y좌표
  dmat = [[a[i][0,:], a[i][-1,:]] for i in range(n)]
  
  #연결할 점들 모아 저장할 list
  concat_points = [0] * (n-1)
  
  #dmat 크기 1이 될때까지
  for i in range(n-1):
    #최단거리인 선 2개를 찾아서, 연결할 점 정보를 가져온다.
    #이후, 비교대상 점들을 저장한 dmat을 선 중 하나로 합치고, 나머지 하나는 삭제한다.
    #또한, 연결할 점 정보는 별도의 list에 저장
    points, line_a, line_b = find_shortest_points(dmat, n, max_diff)
    
    #모든 선이 max_diff보다 멀리 떨어져있을 경우
    #concat_points의 비어있는(0으로 채워진) 인덱스들 자른 후 loop 종료
    if points is None:
      concat_points = concat_points[:i]
      print(f'concat_line : line {len(a) - i}개가 max_diff보다 멀리 떨어져 있어 연결되지 않음.')
      break
      
    #정상적으로 받아온 경우
    concat_points[i] = points
    dmat[line_a] = dmat[line_a] + dmat[line_b]
    del dmat[line_b]
    n = len(dmat)

  #concat_points에 저장된 '연결할 점' 들을 각각 1개의 line으로 취급하여 합친다.
  result = a + concat_points

  return result

def cutting(data, x_range, y_range):
  result = []
  for line in data:
    tmpline = []
    for point in line:
      #check point in range
      if point[0] < x_range[0] or point[0] >= x_range[1] or point[1] < y_range[0] or point[1] >= y_range[1]:
        continue
      tmpline = tmpline + [point]
    if len(tmpline) > 0:
      result = result + [np.array(tmpline)]
  return result

def img_matrix_lines(mat):
  im_mat = np.ones((mat.shape[0], mat.shape[1], 3))
  
  #해안선 값은 1임
  mask = (mat == 1)
  im_mat[mask] = [0,0,0]
    
  return im_mat

def img_matrix_areas(mat):
  im_mat = np.ones((mat.shape[0], mat.shape[1], 3))
  
  #지상 영역 색칠
  mask = (mat == 0)
  im_mat[mask] = [1, 2/3, 0]

  #바다 영역 색칠
  mask = (mat == 1)
  im_mat[mask] = [0, 0, 1]

  #바다 영역 색칠
  mask = (mat == 2)
  im_mat[mask] = [2/3, 2/3, 2/3]
    
  return im_mat

#영역 확장
#dir : 0 / 1 / 2 / 3 : 북 / 서 / 남 / 동
def expand_mat(mat, dir:int, length:int, fill_value = None):
  if dir < 0 or dir > 3 or length < 0:
    raise Exception("parameter error")
  if dir == 0:
    new_mat = np.zeros((mat.shape[0]+ length, mat.shape[1])).astype(int)
    new_mat[length:,:] = mat
    if fill_value is not None:
      new_mat[:length, :] = fill_value
    else:
      for i in range(mat.shape[1]):
        new_mat[:length, i] = mat[0, i]
  elif dir == 1:
    new_mat = np.zeros((mat.shape[0], mat.shape[1] + length)).astype(int)
    new_mat[:,length:] = mat
    if fill_value is not None:
      new_mat[:, :length] = fill_value
    else:
      for i in range(mat.shape[0]):
        new_mat[i, :length] = mat[i, 0]
  elif dir == 2:
    new_mat = np.zeros((mat.shape[0] + length, mat.shape[1])).astype(int)
    new_mat[:mat.shape[0],:] = mat
    if fill_value is not None:
      new_mat[mat.shape[0]:, :] = fill_value
    else:
      for i in range(mat.shape[1]):
        new_mat[mat.shape[0]:, i] = mat[-1,i]
  elif dir == 3:
    new_mat = np.zeros((mat.shape[0], mat.shape[1] + length)).astype(int)
    new_mat[:,:mat.shape[1]] = mat
    if fill_value is not None:
      new_mat[:, mat.shape[1]:] = fill_value
    else:
      for i in range(mat.shape[0]):
        new_mat[i, mat.shape[1]:] = mat[i, -1]

  return new_mat

def img_painting(mat):
  im_mat = np.ones((mat.shape[0], mat.shape[1], 3))
  colormap = plt.get_cmap("tab10")
  cmapfunc = lambda x : list(map(lambda y : int(y * 255), colormap((x%10)/10)[:3]))
  for i in range(1, np.max(mat)+1):
    im_mat[(mat == i)] = cmapfunc(i-1) 
  return im_mat