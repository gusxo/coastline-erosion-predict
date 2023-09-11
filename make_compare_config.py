if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(f"usages : {sys.argv[0]} <config_file_path>")
        exit()

    filepath = f"{sys.argv[1]}.txt"

    f = open(filepath, "w", encoding='utf8')
    default_config_str = """
#compare coastlines config file

#그리기 옵션 지정:
#set line_min_length <line_min_length>
#                   비교 선을 그릴때, 해당 값의 1/2만큼 앞뒤로 더 길게 그립니다.
#set line_size <line_size>
#                   선의 두께(크기), 1 이상의 정수
#set line_color (before | after | compare) R G B
#                   초기 해안선/CA 후 해안선/비교 선의 색상을 지정합니다.
#                   R, G, B 값은 0~255 사이의 정수입니다.

#비교 타겟 작성법 :
#set <row> <col> <direction_type> <direction_value> [wildcard_rules]

#<row>, <col> : 비교를 시작할 좌표를 지정합니다.
#               만약 둘 중 하나의 값을 '-1'로 할 경우, 해당 값은 wildcard가 됩니다.
#               wildcard가 있을 경우 초기 해안선에서 일치하는 좌표를 찾아 사용합니다.

#(y,x)좌표라 생각하면 되며, y의 경우 위쪽이 0, 아래로 갈수록 값이 커집니다.

#<direction_type> : string, bitmask 지원

#<direction_value> :
#       <direction_type>이 string일 경우, "WN", "N" 등의 형식으로 동서남북을 지정합니다.
#       <direction_type>이 bitmask일 경우, 0bxxxx 으로 8방향을 표현함.
#                                       왼쪽 비트부터 북/서/남/동 플래그

#[wildcard_rules] : optional, wildcard 사용시에만 작동합니다.
#                   wildcard로 2개 이상의 좌표를 찾았을 시 처리 방법을 지정합니다.
#                   all : 기본값, 모든 좌표를 해안선 비교에 사용합니다.
#                   min : 찾은 좌표 중 <wildcard value>가 최소값인 좌표만 사용합니다.
#                   max : 찾은 좌표 중 <wildcard value>가 최대값인 좌표만 사용합니다.
#                   mean: 찾은 좌표들의 <wildcard value> 평균값을 새로운 좌표로 하여 사용합니다.(소수점 내림)
#                   

# 아래 기본값은 '낙산해수욕장' 지도에 맞게 설정되었습니다.
set line_min_length 50
set line_size 2
set line_color before 255 0 0
set line_color after 0 255 0
set line_color compare 255 255 0

set -1 50 bitmask 0b0110 mean
set -1 100 string WS mean
set -1 150 string SW mean
set -1 200 bitmask 0b0110 mean
set -1 300 bitmask 0b0110 mean
set -1 400 bitmask 0b0110 mean
    """
    f.write(default_config_str)
    f.close()
    print(f"default config has writed at {filepath}")