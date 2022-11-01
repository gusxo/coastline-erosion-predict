import numpy as np
import os

#초기 gis data 불러오고 처리하는 작업을 행렬 shape가 (x, y) 형태여서,
#일반적인 형태(y,x)로 변환해주는 함수를 사용함
def convert_axis(mat):
  """
  (x,y), x축이 커지는 방향 : 오른쪽 / y축이 커지는 방향 : 위쪽
  인 행렬을
  (y,x), x축이 커지는 방향 : 오른쪽 / y축이 커지는 방향 : 아래쪽(일반적인 2차원 행렬/이미지 형태)
  로 바꿈
  """
  reverse = np.transpose(mat, [1,0])
  reverse = reverse[::-1, :]
  return reverse

def convert_axis_reverse(mat):
  """
  convert_axis의 반대로 동작
  """
  reverse = np.transpose(mat, [1,0])
  reverse = reverse[:, ::-1]
  return reverse

##### 범위 체크 함수 #####
def range_check(r,c,shape):
  return r >= 0 and r < shape[0] and c >= 0 and c < shape[1]

##### 이웃셀 값 바로 얻어오는 함수 #####
#bitmask : 0bxxxx, 8/4/2/1 순서대로 W/A/S/D(북/서/남/동)
def get_neighboor(mat, r, c, bitmask):
  result = []
  add_r = [-1, 0, 1, 0]
  add_c = [0, -1, 0, 1]
  use_dir = [bitmask & 0b1000, bitmask & 0b0100, bitmask & 0b0010, bitmask & 0b0001]
  for i in range(4):
    if use_dir[i]:
      target_r = r + add_r[i]
      target_c = c + add_c[i]
      if range_check(target_r, target_c, mat.shape):
        result += [mat[target_r, target_c]]
      else:
        result += [None]
  return result

  ##### 이웃셀 값 바로 얻어오는 함수 8방향 #####
#bitmask : 0bxxxxxxxx, 왼쪽부터 순서대로 북/북서/서/서남/남/남동/동/동북(북 부터 반시계 회전)
def get_neighboor8(mat, r, c, bitmask):
  result = []
  add_r = [-1, -1, 0, 1, 1, 1, 0, -1]
  add_c = [0, -1, -1, -1, 0, 1, 1, 1]
  use_dir = [bitmask & (1 << i) for i in range(8)]
  for i in range(8):
    if use_dir[i]:
      target_r = r + add_r[i]
      target_c = c + add_c[i]
      if range_check(target_r, target_c, mat.shape):
        result += [mat[target_r, target_c]]
      else:
        result += [None]
  return result

def get_coastline_cells(mat):
  result = set()
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
        if flag:
          result.add((r,c))

  return result


def save_matrix(filepath, mat):
  try:
    np.save(f"{filepath}", mat)
  except Exception as e:
    return False, f"save matrix : save failed : {e}"
  return True, None

def load_matrix(filepath):
  try:
    mat = np.load(f'{filepath}', allow_pickle=True)
  except Exception as e:
    return False, f"load matrix : load failed : {e}"
  return True, mat

def save_inited_matrix(dir, mat, params, coastlines):
  try:
    #디렉토리 확인 후 생성
    if not os.path.isdir(f'{dir}'):
      os.makedirs(f'{dir}')
    np.save(f"{dir}/mat", mat)
    np.save(f"{dir}/params", [params])
    np.save(f"{dir}/coastlines", [coastlines])
  except Exception as e:
    return False, f"save inited matrix : save failed : {e}"
  return True, None

def load_inited_matrix(dir):
  try:
    mat = np.load(f'{dir}/mat.npy', allow_pickle=True)
    params = np.load(f'{dir}/params.npy', allow_pickle=True)[0]
    coastlines = np.load(f'{dir}/coastlines.npy', allow_pickle=True)[0]
  except Exception as e:
    return False, f"load inited matrix : load failed : {e}"
  return True, (mat, params, coastlines)

