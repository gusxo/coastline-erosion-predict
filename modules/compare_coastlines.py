if __name__ == "__main__":
    import argparse
    import numpy as np

    import os, sys
    from os.path import dirname, join, abspath
    sys.path.insert(0, abspath(join(dirname(__file__), "../lib")))
    from Utils import load_inited_matrix
    from Visualize import get_coastline_gap

    desc = "details"
    usage_msg = f"{sys.argv[0]} (-s SAVE_DIR | -p) LOAD_DIR COMPARE_CONFIG"
    parser = argparse.ArgumentParser(description=desc, usage=usage_msg,
    formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(dest="load_dir", action="store", help="""
    이미 초기화된 지도 디렉토리.
    matrix_initializer.py 또는 ca_runner.py의 결과물 디렉토리를 지정하세요.

    """)

    parser.add_argument(dest="compare_config", action="store", help="""
    비교할 방식이 적혀있는 파일입니다.
    파일 형식은 make_compare_config.py로 얻을 수 있습니다.
    check_compare_config.py로 체크 하였을때 성공한 파일이여야 합니다.

    """)

    parser.add_argument("-s", "--save", dest="save_dir", action="store", help="""
    결과를 지정한 경로에 이미지 파일로 저장합니다.
    확장자는 .png로 고정됩니다.

    """)

    parser.add_argument("-p", "--plot" ,dest="plot", action="store_true", help="""
    결과를 matplotlib를 이용하여 이미지 창을 띄워 표시합니다.

    """)


    args = parser.parse_args()
    #-s랑 -p 둘중 하나 요구
    if args.save_dir is None and args.plot == False:
        print(f"error : save_dir 또는 plot 옵션 중 하나는 반드시 사용하여야 합니다.")
        exit()

    #load
    is_success, msg_or_data = load_inited_matrix(args.load_dir)
    if not is_success:
        print(f"error : {msg_or_data}\n초기화 완료된 지도 불러오기에 실패하였습니다.")
        exit()
    mat = msg_or_data[0]
    params = msg_or_data[1]
    init_coastlines = msg_or_data[2]

    print(f"초기화된 지도 불러오기에 성공하였습니다.")
