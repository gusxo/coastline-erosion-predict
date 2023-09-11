# coastline-erosion-predict
해안침식 시뮬레이션 프로그램

<흐름도 사진 추가>

# Data
해양수산부 - 연안포털 - 2020년도 현황도/관리도
- [access link](https://coast.mof.go.kr/coastKnowledge/coastDatumView.do?dt3=&seq=7669&data_type=3&page=1)
- `samples/shapefile/`에 저장되어 있습니다.

# Requirements
```
shapely 2.01
geopandas 0.13.2
python 3.10.12
```
Google Colab <여기에 링크> 에서 예시 코드를 실행해볼 수 있습니다.

# Main Programs
- `matrix_initializer.py` : 2차원 행렬 -> 셀룰러 오토마타 초기상태로 변환하는 프로그램
    - (주의) 실행 시간이 깁니다.
- `ca_runner.py` : 셀룰러 오토마타 실행 프로그램
    - (주의) 실행 시간이 깁니다.

# Util Programs
- `compare_coastlines.py` : 셀룰러 오토마타의 시작과 결과 해안선을 비교합니다. (시각화)
-----
- `check_matrix_config.py` : `matrix_initializer.py`에 필요한 설정파일을 검사합니다.
- `check_compare_config` : `compare_coastlines.py`에 필요한 설정파일을 검사합니다.
----
- `make_matrix_config.py` : `matrix_initializer.py`에 필요한 설정파일의 기본값을 생성합니다.
- `make_compare_config.py` : `compare_coastlines.py`에 필요한 설정파일의 기본값을 생성합니다.
