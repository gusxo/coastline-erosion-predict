import argparse
from tqdm import tqdm

import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '../lib')))
from InitParams import ReadAndInitParmas
from InitMatrix import to_object_type, wave_weight_recv, wave_weight_send, init_active_cells, matrix_init, map_downsize
from Utils import convert_axis, to_img, marking_active_cells, get_coastline_cells, marking_coastline_cells, weight_to_img, load_matrix, load_inited_matrix, save_inited_matrix, save_imgs

desc = "details"
usage_msg = f"{sys.argv[0]} [-s SAVE_DIR] (-m MATRIX_FILE -c CONFIG_FILE [-d DOWNSIZE_COUNT] | -l LOAD_DIR) [-w LOOP_RATE] [-v]"
parser = argparse.ArgumentParser(description=desc, usage=usage_msg,
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("-s", "--save", dest="save_dir", action="store", default="./result", help="""
결과가 저장될 디렉토리
기본값 : ./result

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

parser.add_argument("-v", "--visualize", dest="visualize", action="store_true", help="""
결과를 저장할 때, 결과 행렬의 시각화 이미지를 같이 저장할지 여부
저장되는 이미지 리스트 : 
- matrix : 지도를 표시합니다.
- matrix_active_cells : 지도의 활성화 영역(CA에서 실제 탐색 영역)을 분홍색으로 표시합니다.
- matrix_coastline_cells : 지도와 함께, 해안선을 빨간색으로 표시합니다.
- matrix_weight : 지도의 파도 가중치 값(0~1)을 (파랑~빨강) 색으로 표시합니다.

""")

args = parser.parse_args()

#LOAD_DIR 옵션이 없을 경우, -m -c 옵션 다있는지 확인
if args.load_dir is None and (args.config_file is None or args.matrix_file is None):
    print(f"usage: {usage_msg}")
    print(f"error : -m 옵션과 -c 옵션 둘 다 제공되거나, -l 옵션을 사용해야 합니다.\n자세한 내용은 -h 또는 --help 옵션을 사용하세요.")
    exit()



#LOAD_DIR 옵션이 있을 경우, 로드 시도
if args.load_dir is not None:
    is_success, msg_or_data = load_inited_matrix(args.load_dir)
    if not is_success:
        print(f"error : {msg_or_data}\n초기화 완료된 지도 불러오기에 실패하였습니다.")
        exit()
    inited_mat = msg_or_data[0]
    params = msg_or_data[1]
    init_coastlines = msg_or_data[2]
    print(f"초기화된 지도 불러오기에 성공하였습니다.")
#아닐경우 지도초기화 수행
else:
    is_success, msg_or_data = ReadAndInitParmas(args.config_file)
    if not is_success:
        print(f"error : {msg_or_data}\nconfig 파일 불러오기에 실패하였습니다.")
        exit()
    params = msg_or_data
    
    is_success, msg_or_data = load_matrix(args.matrix_file)
    if not is_success:
        print(f"error : {msg_or_data}\지도 파일 불러오기에 실패하였습니다.")
        exit()
    mat = msg_or_data

    try:
        #init matrix
        inited_matrix = matrix_init(to_object_type(convert_axis(mat)), params)

        #downsizing
        origin_shape = inited_matrix.shape
        predicted_shape = origin_shape
        for i in range(args.downsize_count):
            predicted_shape = (predicted_shape[0] // 2, predicted_shape[1] // 2)
        if (predicted_shape[0] == 0 or predicted_shape[1] == 0) and args.downsize_count:
            print(f"error : too much downsizing : origin shape is {origin_shape}, downsizing result shape is {predicted_shape}\n너무 많이 downsizing 하여 행/열 중 하나의 길이가 0이 되었습니다. downsizing 횟수를 줄여주세요.")
            exit()
        elif (predicted_shape[0] < 100 or predicted_shape[1] < 100) and args.downsize_count:
            print(f"warning : origin shape is {origin_shape}, downsizing result shape is {predicted_shape}\n경고 : 지도를 너무 작게 줄이는 것은 권장하지 않습니다. 이 메시지를 보지 않으려면 downsizing 횟수를 줄여주세요.")
       
        for i in range(args.downsize_count):
            inited_matrix, params = map_downsize(inited_matrix, params)

        #init active cells
        init_coastlines = get_coastline_cells(inited_matrix)
        init_active_cells(inited_matrix, params, init_coastlines)
    except:
        print(f"error : 지도 초기화에 실패하였습니다. 유효한 지도인지 확인해주세요.")
        exit()
    print(f"지도 초기화에 성공하였습니다.")

wave_init_loop_cnt = (inited_mat.shape[0]+inited_mat.shape[1]) * args.loop_rate
wave_init_loop_cnt = int(wave_init_loop_cnt)
print(f"파도/가중치 초기화를 진행합니다. 루프 횟수 : {wave_init_loop_cnt}회")
for i in tqdm(range(wave_init_loop_cnt)):
    wave_weight_recv(inited_mat)
    wave_weight_send(inited_mat)

#save
save_dir = args.save_dir
while(True):
    is_success, msg = save_inited_matrix(save_dir, inited_mat, params, init_coastlines)
    if not is_success:
        print(f"error : {msg}\n결과 파일 저장에 실패했습니다.")
        save_dir += ".tmp"
        print(f"다음 디렉토리에 재시도합니다 : {save_dir}")
    else:
        print(f"결과 파일 저장에 성공했습니다. : {save_dir}")
        break

#save - visualize
if args.visualize:
    img_mat = to_img(inited_mat, params["max_depth"], params["max_depth"]//6)
    img_active_cells = marking_active_cells(to_img(inited_mat,params["max_depth"], params["max_depth"]//6),params)
    img_coastline_cells = marking_coastline_cells(to_img(inited_mat,params["max_depth"], params["max_depth"]//6),init_coastlines, size=3)
    img_weight = weight_to_img(inited_mat)
    imgs = [img_mat, img_active_cells, img_coastline_cells, img_weight]
    names = ["matrix", "matrix_active_cells", "matrix_coastline_cells", "matrix_weight"]
    is_success, msg = save_imgs(save_dir, names, imgs)
    if not is_success:
        print(f"error : {msg}\n이미지 파일 저장에 실패했습니다.")