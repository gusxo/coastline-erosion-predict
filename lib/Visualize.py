import numpy as np
import os
from PIL import Image
from Utils import range_check, get_coastline_cells
import matplotlib.pyplot as plt
import math

def to_img(mat, center, interval):
  sedi_mat = np.zeros_like(mat)
  for r in range(mat.shape[0]):
    for c in range(mat.shape[1]):
      if mat[r,c]["state"] == "wall":
        sedi_mat[r,c] = -1
      else:
        sedi_mat[r,c] = mat[r,c]["sediments"]
  im_mat = np.ones((mat.shape[0], mat.shape[1], 3))
  colors = [[160/255, 160/255, 160/255], [0, 51/255, 102/255], [0, 76/255, 153/255], [0, 102/255, 204/255], [0, 128/255, 1], [51/255, 153/255, 1], [102/255, 178/255, 1],
            [1, 178/255, 102/255], [1, 178/255, 102/255], [1, 178/255, 102/255], [1, 178/255, 102/255], [1, 178/255, 102/255], [1, 178/255, 102/255]]
  r = [center] * 13
  for i in range(5):
    r[6 - i] = center - interval * i
    r[8 + i] = center + interval * i
  r[1] = 0
  r[0] = -1

  for i in range(12):
    mask = (sedi_mat >= r[i]) &  ( sedi_mat < r[i+1])
    im_mat[mask] = colors[i]

  mask = (sedi_mat >= r[12])
  im_mat[mask] = colors[12]

  return im_mat

def marking_active_cells(im_mat, params):
  im_mat[params["active_cells"]] = [1, 102/255, 102/255]
  return im_mat

def marking_coastline_cells(im_mat, coastline_cells, size = 1, color=[1,0,0]):
  target_list = list(coastline_cells)

  for r, c in target_list:
    sr = r - (size - 1)
    sc = c - (size - 1)
    er = r + (size - 1)
    ec = c + (size - 1)
    sr = max([0, sr])
    sc = max([0, sc])

    im_mat[sr:er+1, sc:ec+1] = color
  return im_mat

def marking_zero_white(im_mat, mat):
  for r in range(mat.shape[0]):
    for c in range(mat.shape[1]):
      if mat[r,c]["state"] == "sea":
        if mat[r,c]["sediments"] < 1:
          im_mat[r,c] = [1,1,1]
          
  return im_mat

def marking_line(im_mat, start, direction, length, size=1, color=[1,1,1]):
  r, c = start
  add_r = [-1, 0, 1, 0]
  add_c = [0, -1, 0, 1]
  dirs = [0b1000, 0b0100, 0b0010, 0b0001]
  for i in range(length):
    if not range_check(r,c,im_mat.shape):
      break
    im_mat[max([0, r-size+1]):r+size,max([0,c-size+1]):c+size] = color
    for i in range(4):
      if direction & dirs[i]:
        r += add_r[i]
        c += add_c[i]
  return im_mat

def get_coastline_gap_cal(points, mat, direction):
  r, c = points
  cnt = 0
  add_r = [-1, 0, 1, 0]
  add_c = [0, -1, 0, 1]
  dirs = [0b1000, 0b0100, 0b0010, 0b0001]
  ban_dirs = [0b1010, 0b0101]
  direction = direction & 0b1111

  if (direction & ban_dirs[0]) == ban_dirs[0] or (direction & ban_dirs[1]) == ban_dirs[1]:
    raise Exception("get_coastline_gap_cal : direction is not valid")

  if mat[r,c] == 3:
    return {"from":points, "direction":direction, "to":(r,c), "gap":0}

  add_values = []
  for i in range(4):
    if direction & dirs[i]:
      add_values += [(add_r[i], add_c[i])]
      if len(add_values) == 2:
        add_values += [(add_values[0][0] + add_r[i], add_values[0][1] + add_c[i])]
      elif len(add_values) >= 4:
        raise Exception("error")
  while(True):
    if not range_check(r,c,mat.shape):
      return {"from":points, "direction":direction, "to":(r,c), "gap":-1}

    for add_r, add_c in add_values:
      next_r = r + add_r
      next_c = c + add_c
      if range_check(next_r, next_c, mat.shape):
        if mat[next_r, next_c] == 2:
          r = next_r
          c = next_c
          return {"from":points, "direction":direction, "to":(next_r, next_c), "gap":cnt+1}
    r += add_values[-1][0]
    c += add_values[-1][1]
    cnt+=1



def get_coastline_gap(before_coastline, after_coastline, base_points, compare_dirs, rules="all"):
  """
  before_coastline : get_coastline_cells()로 얻은 set
  after_coastline : get_coastline_cells()로 얻은 set
  base_points : 좌표 튜플의 리스트. ex: [(x1,y1),(x2,y2)]
                x 또는 y 좌표가 음수일 경우, 해당 축은 before_coastline에 속한 모든 좌표로 인식
  compare_dirs : base_points 좌표에서 어느 방향으로 거리를 잴것인지 지정하는 int의 리스트
                  방향 지정 방법 : 0bxxxx, bitmask 형태로 각각 북/서/남/동 flag
                  ex : 북서는 0b1100, 남은 0b0010
  """
  
  result = []
  beforelist = list(before_coastline)
  afterlist = list(after_coastline)
  before_x = [beforelist[i][0] for i in range(len(beforelist))]
  before_y = [beforelist[i][1] for i in range(len(beforelist))]
  after_x = [afterlist[i][0] for i in range(len(afterlist))]
  after_y = [afterlist[i][1] for i in range(len(afterlist))]
  
  x_max = max(before_x + after_x)
  y_max = max(before_y + after_y)
  
  mat = np.zeros((x_max+1,y_max+1), dtype=int)
  
  for r, c in beforelist:
    mat[r,c] |= 1
  for r, c in afterlist:
    mat[r,c] |= 2
    
  for i in range(len(base_points)):
    r, c = base_points[i]
    compare_start_points_r = []
    compare_start_points_c = []
    if r < 0 and c < 0:
      raise Exception("base_points : x, y 좌표를 둘 다 음수로 지정할 수 없습니다.")
    elif r < 0:
      target_mask = (mat[:,c] & 1)
      indexs = np.where(target_mask)
      for index in indexs[0]:
        compare_start_points_r += [index]
        compare_start_points_c += [c]
    elif c < 0:
      target_mask = (mat[r, :] & 1)
      indexs = np.where(target_mask)
      for index in indexs[0]:
        compare_start_points_r += [r]
        compare_start_points_c += [index]
    else:
      compare_start_points_r += [r]
      compare_start_points_c += [c]
    #시작 포인트 다수일 경우를 대비해 규칙 적용
    cnt = len(compare_start_points_r)
    if rules == "all":
      for k in range(cnt):
        result += [get_coastline_gap_cal((compare_start_points_r[k], compare_start_points_c[k]), mat, compare_dirs[i])]
    elif rules == "min":
      result += [get_coastline_gap_cal((np.min(compare_start_points_r), np.min(compare_start_points_c)), mat, compare_dirs[i])]
    elif rules == "max":
      result += [get_coastline_gap_cal((np.max(compare_start_points_r), np.max(compare_start_points_c)), mat, compare_dirs[i])]
    elif rules == "mean":
      result += [get_coastline_gap_cal((int(np.mean(compare_start_points_r)), int(np.mean(compare_start_points_c))), mat, compare_dirs[i])]
    else:
      raise Exception("get_coastline_gap : rules parameter is not valid")

  return result
  

def weight_to_img(mat):
  w_mat = np.zeros_like(mat).astype(int)
  for r in range(mat.shape[0]):
    for c in range(mat.shape[1]):
      if mat[r,c]["state"] == "wall":
        w_mat[r,c] = -1
      else:
        w_mat[r,c] = int(mat[r,c]["recv_weight"])
  im_mat = np.ones((mat.shape[0], mat.shape[1], 3))
  colors = [[160/255, 160/255, 160/255], [0, 0, 1], [0, 0.2, 1], [0, 0.4, 1], [0, 0.6, 1], [0, 0.8, 1], [0, 1, 1],
            [0, 1, 0.8], [0, 1, 0.6], [0, 1, 0.4], [0, 1, 0.2], [0, 1, 0],
            [0.2, 1, 0], [0.4, 1, 0], [0.6, 1, 0], [0.8, 1, 0], [1, 1, 0],
            [1, 0.8, 0], [1, 0.6, 0], [1, 0.4, 0], [1, 0.2, 0], [1, 0, 0]]
  r = [-1] * len(colors)
  for i in range(len(colors) - 1):
    r[i+1] = 50 * i

  for i in range(len(colors) - 1):
    mask = (w_mat >= r[i]) &  ( w_mat < r[i+1])
    im_mat[mask] = colors[i]

  mask = (w_mat >= r[len(colors) - 1])
  im_mat[mask] = colors[len(colors) - 1]

  return im_mat

def save_imgs(dir, filenames, imgs):
  try:
    filecnt = len(filenames)
    imgcnt = len(imgs)
    if filecnt != imgcnt:
      return False, f"save visualized images : save failed : unmatch filenames length & imgs length"
    #디렉토리 확인 후 생성
    if not os.path.isdir(f'{dir}'):
      os.makedirs(f'{dir}')
    for i in range(filecnt):
      im = Image.fromarray((imgs[i] * 255).astype(np.uint8))
      im.save(f"{dir}/{filenames[i]}.png")
  except Exception as e:
    return False, f"save visualized images : save failed : {e}"
  return True, None

def save_mat_with_visualize(dir, mat, params, init_coastlines, line_size):
  img_mat = to_img(mat, params["max_depth"], params["max_depth"]//6)
  img_active_cells = marking_active_cells(to_img(mat,params["max_depth"], params["max_depth"]//6),params)
  img_coastline_cells = marking_coastline_cells(to_img(mat,params["max_depth"], params["max_depth"]//6),init_coastlines, size=line_size)
  img_weight = weight_to_img(mat)
  imgs = [img_mat, img_active_cells, img_coastline_cells, img_weight]
  names = ["matrix", "matrix_active_cells", "matrix_coastline_cells", "matrix_weight"]
  return save_imgs(dir, names, imgs)

def coastline_gap_visualize(mat, params, init_coastlines, line_size, line_min_length, before_color, after_color, compare_color, targets, plot=False, save_dir=None):

  after_coastlines = get_coastline_cells(mat)

  _ = to_img(mat,params["max_depth"], params["max_depth"]//6)
  _ = marking_coastline_cells(_, init_coastlines, size=line_size, color = before_color)
  _ = marking_coastline_cells(_, after_coastlines, size=line_size, color=after_color)

  valid_info = []
  for i in range(len(targets)):
    gap_info = get_coastline_gap(init_coastlines, after_coastlines,[targets[i][0:2]] ,[targets[i][2]], rules=targets[i][3])
    for j in range(len(gap_info)):
      if gap_info[j]["gap"] == -1:
        gap_info[j] = get_coastline_gap(init_coastlines, after_coastlines,[gap_info[j]["from"]] ,[~targets[i][2]])[0]
        if gap_info[j]["gap"] != -1:
          gap_info[j]["gap"] *= -1
          valid_info += [gap_info[j]]
      else:
        valid_info += [gap_info[j]]

  info_txt = ""
  for i in range(len(valid_info)):
    gaps = valid_info[i]
    r, c = gaps["from"]
    direction = gaps["direction"]
    if gaps["gap"] < 0:
      direction = (~direction) & 0b1111
    add_r = [-1, 0, 1, 0]
    add_c = [0, -1, 0, 1]
    dirs = [0b1000, 0b0100, 0b0010, 0b0001]
    dirs_txt = ["N", "W", "S", "E"]
    direction_txt = ""
    for j in range(4):
      if direction & dirs[j]:
        r += add_r[j] * -1 * (line_min_length // 2)
        c += add_c[j] * -1 * (line_min_length // 2)
        direction_txt += dirs_txt[j]
    _ = marking_line(_, (r,c), direction, gaps["gap"]+line_min_length, size=line_size, color=compare_color)
    diff = int(params["cell_length"] * gaps["gap"] * (math.sqrt(2) if len(direction_txt) >= 2 else 1))
    info_txt += f"Line {i+1}\nBefore-Coastline-Point: {gaps['from'][0]} {gaps['from'][1]}\nAfter-Coastline-Point: {gaps['to'][0]} {gaps['to'][1]}\n"
    info_txt += f"Compare-Dir: {direction_txt}\nDiff: {diff/1000} m\n"


  if plot:
    plt.imshow(_)
    print(info_txt)
  if save_dir is not None:
    try:
      #디렉토리 확인 후 생성
      if not os.path.isdir(f'{save_dir}'):
        os.makedirs(f'{save_dir}')
      im = Image.fromarray((_ * 255).astype(np.uint8))
      im.save(f"{save_dir}/compare_coastline.png")
    except Exception as e:
          raise Exception(f"save results images failed : {e}")
    try:
      f = open(f"{save_dir}/compare_info.txt", "w", encoding='utf8')
      f.write(info_txt)
      f.close()
    except Exception as e:
      raise Exception(f"save results info failed : {e}")

  return _