import numpy as np

##### convert to img : fast version
def convert_to_img(mat, color_table = None, return_color_table = False):
  im_mat = np.ones((mat.shape[1], mat.shape[0], 3))
  if color_table is None:
    colors = np.array([[0,0.2,0.4,0.6,0.8], [0,0.2,0.4,0.6,0.8], [0, 0.2, 0.4, 0.6,0.8]])    
    np.random.shuffle(colors[0])
    np.random.shuffle(colors[1])
    np.random.shuffle(colors[2])
  else:
    colors = color_table
    
#   print(f'convert_to_img : colors = \n{colors}')
  
  area_cnt = np.max(mat)
  for area_num in range(1, min(area_cnt, colors.shape[1] ** 3) + 1):
    tmp = area_num-1
    r = tmp%colors.shape[1]
    tmp = tmp//colors.shape[1]
    g = tmp%colors.shape[1]
    tmp = tmp//colors.shape[1]
    b = tmp%colors.shape[1]
    color = [colors[0,r], colors[1,g], colors[2,b]]
    
    #영역이 area_num인 곳을 추출함
    #(x,y) 형태인 것을 (y(::-1), x) 형태로 치환해야 이미지 출력시 왜곡안됨
    mask = np.transpose((mat == area_num), [1,0])
    mask = mask[::-1, :]
    im_mat[mask] = color
    
  if return_color_table:
    return im_mat, colors
  else:
    return im_mat

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

