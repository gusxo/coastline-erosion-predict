import warnings
import numpy as np
import datetime

class CellularAutomata:
  def __init__(self):
    self.automata_rule = None
    self.origin_matrix = None
    self.mat = None
    self.steps = None
    self.parameters = None
    self.warning_msg = True     #각종 경고메세지 출력 여부
    return
    
  def set_rules(self, rule):
    """
    rule : 매개변수로 (matrix, x, y, steps, parameters)를 받는 함수
          x와 y는 좌표, steps는 오토마타내에서 몇번째 루프인지 지정함
          parameters는 set_params로 지정했을 경우 값이 들어오고, 아니면 None임
          ***** matrix가 call by reference이므로 무조건 READ ONLY로 쓸 것, 직접 수정될 시 예측 불가능 함 *****
          ***** value가 object 타입일 경우엔 특히 주의할 것 *****
          return value가 새로운 (x,y) 좌표의 값이됨
          
    예시 : 현재 자신의 좌표만 값을 1 더하는 규칙
        def rule(mat, x, y, steps, parameters):
          mat[x,y] += 1
          return
                      
    """
    if self.steps is not None and self.warning_msg == True:
      warnings.warn("오토마타의 초기화 이후에 rule이 변경됨")
    self.automata_rule = rule
    return
  
  def set_matrix(self, matrix):
    """
    원본 행렬 저장
    """
    if self.mat is not None and self.warning_msg == True:
      warnings.warn("원본행렬이 변경되었지만, init()을 실행하여 초기화하거나 직접 mat 변수에 대입하여야 오토마타에 적용됩니다.")
    self.origin_matrix = np.array(matrix)
    return
    
  def set_params(self, parameters):
    """
    rule function에서 계속 참조가능한 추가변수 지정
    """
    self.parameters = parameters

  def init(self):
    """
    셀룰러 오토마타 시작시점으로 초기화
    """
    if self.origin_matrix is None:
      raise ValueError("set_matrix(mat)로 타겟 행렬을 지정하여야 합니다.")
    if self.automata_rule is None:
      raise ValueError("set_rules(rule)로 규칙을 지정하여야 합니다.")
    self.mat = self.origin_matrix.copy()
    self.steps = 0
    return
  
  def step(self):
    """
    1회의 step(stage)을 진행하고, 규칙함수의 실행시간 정보를 반환한다.
    """
    if self.steps is None:
      raise ValueError("init()을 먼저 실행해야 합니다.")
    
    time_avg = datetime.timedelta(days=0)
    time_best = 0
    time_worst = 0
    func_starttime = datetime.datetime.now()
    
    next_mat = np.zeros_like(self.mat)
    
    try:
      for x in range(self.mat.shape[0]):
        for y in range(self.mat.shape[1]):
          starttime = datetime.datetime.now()
          #규칙 적용
          # next_mat.itemset((x,y), self.automata_rule(self.mat, x, y, self.steps, self.parameters)) 
          next_mat[x,y] = self.automata_rule(self.mat, x, y, self.steps, self.parameters)
          #실행시간 측정
          endtime = datetime.datetime.now()
          timediff = endtime - starttime
          if time_best == 0:
            time_best = timediff
            time_worst = timediff
          else:
            time_best = np.min([timediff, time_best])
            time_worst = np.max([timediff, time_worst])
          time_avg += timediff
          
    except Exception as e:
      raise ValueError("rule function 실행 도중 에러가 발생하였음")
    
    self.mat = next_mat
    time_avg /= (self.mat.shape[0] * self.mat.shape[1])
    self.steps+=1

    func_endtime =  datetime.datetime.now()
    return {"time_avg":time_avg.total_seconds(), "time_best":time_best.total_seconds(),
            "time_worst":time_worst.total_seconds(), "function_total":(func_endtime-func_starttime).total_seconds()}

  def step_part(self, mask):
    """
    step()과 유사하지만, mask로 받은 좌표들에만 적용한다.
    mask는 mat과 동일한 shape의 boolean 2d numpy array로, True인 곳에만 규칙을 적용한다.
    """
    if self.steps is None:
      raise ValueError("init()을 먼저 실행해야 합니다.")
    
    time_avg = datetime.timedelta(days=0)
    time_best = 0
    time_worst = 0

    func_starttime = datetime.datetime.now()
    
    mask = mask.copy()
    target = np.where(mask)
    targetlen = len(target[0])
    results = np.zeros(targetlen).astype(self.mat.dtype)
    
    try:
      for i in range(targetlen):
        starttime = datetime.datetime.now()
        #규칙 적용
        results[i] = self.automata_rule(self.mat, target[0][i], target[1][i], self.steps, self.parameters)
        #실행시간 측정
        endtime = datetime.datetime.now()
        timediff = endtime - starttime
        if time_best == 0:
          time_best = timediff
          time_worst = timediff
        else:
          time_best = np.min([timediff, time_best])
          time_worst = np.max([timediff, time_worst])
        time_avg += timediff

      #다음 셀 값들 모두 계산후, 대입 시작
      self.mat[mask] = results
          
    except Exception as e:
      raise ValueError("rule function 실행 도중 에러가 발생하였음")
    
    time_avg /= (targetlen)
    self.steps+=1

    func_endtime =  datetime.datetime.now()
    return {"time_avg":time_avg.total_seconds(), "time_best":time_best.total_seconds(),
            "time_worst":time_worst.total_seconds(), "function_total":(func_endtime-func_starttime).total_seconds()}  