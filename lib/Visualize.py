import numpy as np
import os
from PIL import Image
from Utils import range_check, get_coastline_cells
import matplotlib.pyplot as plt


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

def get_coastline_gap_cal(points, mat, direction, allow_gap):
  r, c = points
  cnt = 0
  add_r = [-1, 0, 1, 0]
  add_c = [0, -1, 0, 1]
  dirs = [0b1000, 0b0100, 0b0010, 0b0001]
  direction = direction & 0b1111
  while(True):
    if not range_check(r,c,mat.shape):
      cnt = -1
      break
    mask = (mat[max([0, r-allow_gap]):r+1+allow_gap, max([0, c-allow_gap]):c+1+allow_gap] & 2)
    if np.sum(mask):
      break
    for i in range(4):
      if direction & dirs[i]:
        r += add_r[i]
        c += add_c[i]
    cnt+=1
  return {"from":points, "direction":direction, "to":(r,c), "gap":cnt}

def get_coastline_gap(before_coastline, after_coastline, base_points, compare_dirs, allow_gap = 0):
  """
  before_coastline : get_coastline_cells()로 얻은 set
  after_coastline : get_coastline_cells()로 얻은 set
  base_points : 좌표 튜플의 리스트. ex: [(x1,y1),(x2,y2)]
                x 또는 y 좌표가 음수일 경우, 해당 축은 before_coastline에 속한 모든 좌표로 인식
  compare_dirs : base_points 좌표에서 어느 방향으로 거리를 잴것인지 지정하는 int의 리스트
                  방향 지정 방법 : 0bxxxx, bitmask 형태로 각각 북/서/남/동 flag
                  ex : 북서는 0b1100, 남은 0b0010
  allow_gap : 허용 오차, after_coastline과의 거리를 잴 때 allow_gap 만큼의 차이가 나더라도 맞는것으로 처리함
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
    if r < 0 and c < 0:
      raise Exception("base_points : x, y 좌표를 둘 다 음수로 지정할 수 없습니다.")
    elif r < 0:
      target_mask = (mat[:,c] & 1)
      indexs = np.where(target_mask)
      for index in indexs[0]:
        result += [get_coastline_gap_cal((index, c), mat, compare_dirs[i], allow_gap)]
    elif c < 0:
      target_mask = (mat[r, :] & 1)
      indexs = np.where(target_mask)
      for index in indexs[0]:
        result += [get_coastline_gap_cal((r, index), mat, compare_dirs[i], allow_gap)]
    else:
      result += [get_coastline_gap_cal((r, c), mat, compare_dirs[i], allow_gap)]
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

def coastline_gap_visualize(mat, params, init_coastlines, line_size, line_min_length, before_color, after_color, compare_color, targets, plot=False, save_path=None):

    after_coastlines = get_coastline_cells(mat)

    _ = to_img(mat,params["max_depth"], params["max_depth"]//6)
    _ = marking_coastline_cells(_, init_coastlines, size=line_size, color = before_color)
    _ = marking_coastline_cells(_, after_coastlines, size=line_size, color=after_color)

    valid_info = []
    for i in range(len(targets)):
        gap_info = get_coastline_gap(init_coastlines, after_coastlines,targets[i][0:2] ,targets[i][2], allow_gap=0, rules=targets[i][3])
        
        for j in range(len(gap_info)):
            if gap_info[j]["gap"] == -1:
                gap_info[j] = get_coastline_gap(init_coastlines, after_coastlines,gap_info[j]["from"] ,~targets[i][2], allow_gap=0)
                if gap_info[j]["gap"] != -1:
                    gap_info[j]["gap"] *= -1
                    valid_info += [gap_info[j]]
            else:
                valid_info += [gap_info[j]]

    for gaps in valid_info:
        r, c = gaps["from"]
        direction = gaps["direction"]
        add_r = [-1, 0, 1, 0]
        add_c = [0, -1, 0, 1]
        dirs = [0b1000, 0b0100, 0b0010, 0b0001]
        for i in range(4):
            if direction & dirs[i]:
                r += add_r[i] * -1 * (line_min_length // 2)
                c += add_c[i] * -1 * (line_min_length // 2)
        _ = marking_line(_, (r,c), direction, gaps["gap"]+line_min_length, size=line_size, color=compare_color)

    if plot:
        plt.imshow(_)
    if save_path is not None:
        try:
            im = Image.fromarray((_[i] * 255).astype(np.uint8))
            im.save(f"{save_path}.png")
        except Exception as e:
            raise Exception(f"save visualized images : save failed : {e}")

    return _