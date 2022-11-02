if __name__ == "__main__":
    import argparse
    from tqdm import tqdm
    import numpy as np

    import sys
    from os.path import dirname, join, abspath
    libpath = abspath(join(dirname(__file__), "../lib"))
    sys.path.insert(0, libpath)    

    from Rules import rule_main, rule_toppling
    from CellularAutomata import CellularAutomata
    from Utils import load_inited_matrix, save_inited_matrix
    from Visualize import save_mat_with_visualize, coastline_gap_visualize
    from ReadConfig import ReadCompareConfig

    desc = "details"
    usage_msg = f"{sys.argv[0]} RUN_STEPS LOAD_DIR [-h] [-s SAVE_DIR] [--store_images [--line_size LINE_SIZE]] [--compare_coastlines COMPARE_CONFIG] [--save_per_steps SAVE_STEPS]"
    parser = argparse.ArgumentParser(description=desc,usage=usage_msg,
    formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(dest="run_steps", action="store", type=int, help="""
    셀룰러 오토마타를 STEP 횟수 만큼 실행합니다.

    """)

    parser.add_argument(dest="load_dir", action="store", help="""
    이미 초기화된 지도 디렉토리.
    matrix_initializer.py 또는 ca_runner.py의 결과물 디렉토리를 지정하세요.

    """)

    parser.add_argument("-s", "--save", dest="save_dir", action="store", default="ca_result", help="""
    결과가 저장될 디렉토리
    기본값 : ca_result

    """)

    parser.add_argument("--store_images", dest="visualize", action="store_true", help="""
    결과를 저장할 때, 결과 행렬의 시각화 이미지를 같이 저장할지 여부
    저장되는 이미지 리스트 : 
    - matrix : 지도를 표시합니다.
    - matrix_active_cells : 지도의 활성화 영역(CA에서 실제 탐색 영역)을 분홍색으로 표시합니다.
    - matrix_coastline_cells : 지도와 함께, 해안선을 빨간색으로 표시합니다.
    - matrix_weight : 지도의 파도 가중치 값(0~1)을 (파랑~빨강) 색으로 표시합니다.

    """)

    parser.add_argument("--line_size", dest="line_size", action="store", type=int, default=1, help="""
    --store_images 옵션 사용시에만 작동합니다.
    matrix_coastline_cells 이미지의 빨간선 크기를 결정합니다.
    기본값은 1입니다.

    """)

    parser.add_argument("--compare_coastlines", dest="compare_config", action="store", help="""
    해안선 비교 설정 파일을 지정하여, 초기 해안선(지도 초기화 직후)과 CA 적용 후 해안선을 비교합니다.
    SAVE_PER_STEPS 옵션을 같이 지정할 시, 중간 결과 저장시 마다 해안선 비교를 수행합니다.
    - compare_coastline.png : 비교 이미지
    - compare_info.txt : 비교이미지의 비교선들의 정보가 적힘
    
    파일 형식은 make_compare_config.py로 얻을 수 있습니다.
    check_compare_config.py로 체크 하였을때 성공한 파일이여야 합니다.

    """)

    parser.add_argument("--save_per_steps", dest="save_steps", action="store", type=int, help="""
    셀룰러 오토마타가 최종 결과 외에도 <SAVE_STEPS> 스텝 마다 중간 결과를 저장합니다.
    중간 결과 저장은 <SAVE_DIR>/<STEPS> 디렉토리에 이루어 집니다.

    """)

    args = parser.parse_args()
    #숫자 옵션들 음수일 경우 에러
    if args.run_steps < 0:
        print(f"error : run_steps arguments must at least 0, but input is {args.run_steps}")
        exit()
    if args.save_steps is not None:
        if args.save_steps < 1:
            print(f"error : save_steps arguments must at least 1, but input is {args.save_steps}")
            exit()
    if args.line_size < 1:
        print(f"error : line_size arguments must at least 1, but input is {args.line_size}")
        exit()

    #load
    is_success, msg_or_data = load_inited_matrix(args.load_dir)
    if not is_success:
        print(f"error : {msg_or_data}\n초기화 완료된 지도 불러오기에 실패하였습니다.")
        exit()
    mat = msg_or_data[0]
    params = msg_or_data[1]
    init_coastlines = msg_or_data[2]

    curr_steps = 0
    if "ca_curr_steps" in params:
        curr_steps = params["ca_curr_steps"]
    params["ca_curr_steps"] = curr_steps

    print(f"초기화된 지도 불러오기에 성공하였습니다.")

    if args.compare_config is not None:
        is_success, msg_or_data = ReadCompareConfig(args.compare_config)
        if not is_success:
            print(f"error : {msg_or_data}\n해안선 비교 설정 파일 불러오기에 실패하였습니다.")
            exit()
        line_min_length = msg_or_data[0]["line_min_length"]
        line_size = msg_or_data[0]["line_size"]
        before_color = msg_or_data[0]["before"]
        after_color = msg_or_data[0]["after"]
        compare_color = msg_or_data[0]["compare"]

        targets = msg_or_data[1:]

        print(f"해안선 비교 설정 파일 불러오기에 성공하였습니다.")

    #CA init
    CA = CellularAutomata()
    CA.set_rules(rule_main)
    CA.set_matrix(mat)
    CA.set_params(params)
    CA.warning_msg = False
    CA.init()

    print(f"셀룰러 오토마타를 실행합니다.")
    print(f"불러온 파일 steps : {curr_steps}, 목표 steps : {curr_steps+args.run_steps}")
    for i in tqdm(range(args.run_steps)):
        params["ca_curr_steps"] += 1
        # 메인 룰 적용
        CA.set_rules(rule_main)
        CA.step_part(params["active_cells"])
        # 토플링 초기화 : 전체 탐색
        toppling_steps = 1
        params["tmp_toppling_target"] = np.zeros((CA.mat.shape[0],CA.mat.shape[1]), dtype=bool)
        CA.set_rules(rule_toppling)
        CA.step_part(params["active_cells"])
        # 토플링 초기화 : 부분 탐색
        while(sum(params["tmp_toppling_target"].flatten()) > 0):
            toppling_steps += 1
            toppling_target = params["tmp_toppling_target"]
            params["tmp_toppling_target"] = np.zeros((CA.mat.shape[0],CA.mat.shape[1]), dtype=bool)
            CA.step_part(toppling_target)

        #save_per_steps check
        if args.save_steps is not None:
            if (i+1)%args.save_steps == 0:
                mat = CA.mat
                #save
                save_dir = f"{args.save_dir}/{curr_steps+i+1}"
                is_success, msg = save_inited_matrix(save_dir, mat, params, init_coastlines)
                if not is_success:
                    print(f"error : {msg}\n중간 결과 파일 저장에 실패했습니다.")
                    exit()

                #save - visualize
                if args.visualize:
                    is_success, msg = save_mat_with_visualize(save_dir, mat, params, init_coastlines, args.line_size)
                    if not is_success:
                        print(f"error : {msg}\n중간 이미지 파일 저장에 실패했습니다.")
                        exit()

                #save - compare coastlines
                if args.compare_config is not None:
                    is_success, msg = coastline_gap_visualize(mat, params, init_coastlines, line_size, line_min_length, before_color, after_color, compare_color, targets, False, save_dir)
                    if not is_success:
                        print(f"error : {msg}\n중간 해안선 비교 파일 저장에 실패했습니다.")
                        exit()

    mat = CA.mat
    #save
    save_dir = args.save_dir
    is_success, msg = save_inited_matrix(save_dir, mat, params, init_coastlines)
    if not is_success:
        print(f"error : {msg}\n결과 파일 저장에 실패했습니다.")
        exit()
    else:
        print(f"결과 파일 저장에 성공했습니다. : {save_dir}")

    #save - visualize
    if args.visualize:
        is_success, msg = save_mat_with_visualize(save_dir, mat, params, init_coastlines, args.line_size)
        if not is_success:
            print(f"error : {msg}\n이미지 파일 저장에 실패했습니다.")
            exit()
        else:
            print(f"이미지 파일 저장에 성공했습니다. : {save_dir}")

    #save - compare coastlines
    if args.compare_config is not None:
        is_success, msg = coastline_gap_visualize(mat, params, init_coastlines, line_size, line_min_length, before_color, after_color, compare_color, targets, False, save_dir)
        if not is_success:
            print(f"error : {msg}\n중간 해안선 비교 파일 저장에 실패했습니다.")
            exit()
        else:
            print(f"해안선 비교 파일 저장에 성공했습니다. : {save_dir}")
