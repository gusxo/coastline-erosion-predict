import argparse

import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '../lib')))
from InitParams import ReadAndInitParmas
from InitMatrix import to_object_type, wave_weight_recv, wave_weight_send, init_active_cells, matrix_init, map_downsize
from Utils import save_matrix, load_matrix, convert_axis, to_img, marking_active_cells, marking_coastline_cells, weight_to_img

desc = "details"
usage_msg = f"{sys.argv[0]} -s SAVE_DIR (-m MATRIX_FILE -c CONFIG_FILE [-d DOWNSIZE_COUNT] | -l LOAD_DIR) [-w LOOP_RATE]"
parser = argparse.ArgumentParser(description=desc, usage=usage_msg,
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("-s", "--save", dest="save_dir", action="store", required=True, help="""
결과가 저장될 디렉토리(필수)

""")
parser.add_argument("-l", "--load", dest="load_dir", action="store", help="""
이미 초기화된 지도 디렉토리.
이 옵션이 제공되면 파도/가중치 초기화만 수행합니다.
파도/가중치 초기화를 추가로 수행해야 할 때 사용하세요.

""")
parser.add_argument("-m", "--matrix", dest="matrix_file", action="store", help="""
초기화가 되지 않은 지도 파일.

""")
parser.add_argument("-c", "--config", dest="config_file", action="store", help="""
파라미터 설정이 담긴 파일.
check_config.py로 체크 하였을때 성공한 파일이여야 합니다.

""")
parser.add_argument("-d", "--downsize", dest="downsize_count", action="store", type=int, default=0, help="""
지도 초기화시 downsizing을 몇회 수행할 것인지의 여부
1회 수행시마다 가로/세로 크기가 1/2로 감소합니다.
기본값은 0입니다.

""")
parser.add_argument("-w", "--wave_init", dest="loop_rate", action="store", type=float, default=1.0, help="""
파도/가중치 초기화를 수행할 횟수의 배율.
파도/가중치 초기화 수행 횟수는 '(지도의 가로 크기 + 세로 크기) * 배율' 입니다.
기본값은 1.0입니다.

""")

args = parser.parse_args()

#LOAD_DIR 옵션이 없을 경우, -m -c 옵션 다있는지 확인
if args.load_dir is None and (args.config_file is None or args.matrix_file is NOne):
    print(f"usage: {usage_msg}")
    print(f"error : -m 옵션과 -c 옵션 둘 다 제공되거나, -l 옵션을 사용해야 합니다.\n자세한 내용은 -h 또는 --help 옵션을 사용하세요.")
    exit()