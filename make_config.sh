#!/bin/sh

if [ $# -lt 1 ]
then
    echo "Error : No arguments supplied"
    echo "usages: /bin/bash $0 <config_file_path>"
    exit 1
fi
rm $1
echo -e "\
#parameters file\n\
#파라미터 값 작성법 : set <param_name> <value>\n\
#set으로 시작하지 않는 줄은 무시됨.\n\
#동일한 파라미터 중복 정의시, 더 뒤에있는 줄이 유효.\n\
\n\
##### 아래 파라미터들을 지도 행렬에 맞게 수정해주세요.\n\
# 아래 기본값은 '낙산해수욕장' 지도에 맞게 설정되었습니다.\n\
\n\
#cell_length : 셀 1칸 당 거리 단위(mm)\n\
set cell_length 1000\n\
\n\
#coast_height : 해안(지상) 최고 높이(mm)\n\
set coast_height 1000\n\
\n\
#sea_max_depth : 해저 최대 깊이(mm)\n\
set sea_max_depth 9000\n\
\n\
#coast_angle : 해빈경사\n\
set coast_angle 10.0\n\
\n\
#allow_angle : 모래 최대 안식각\n\
set allow_angle 20.0\n\
\n\
#wave_energy_avg : 연간 평균 파도에너지(단위 m^2)\n\
set wave_energy_avg 0.1\n\
\n\
#wave_energy_target : 시뮬레이션에 사용할 평균 파도에너지\n\
set wave_energy_target 0.5\n\
\n\
#default_wave_dir : 기본 파도방향을 지정함.\n\
#   bitmask value = 0bxxxx 으로 8방향을 표현함. 왼쪽 비트부터 북/서/남/동 플래그\n\
#                   예를 들어 0b0001은 서쪽 외각 셀들에 동쪽으로 파도를 보내게 설정함.\n\
#                   예를 들어 0b1100은 동쪽과 남쪽 외각 셀들에 북서쪽으로 파도를 보내게 설정함.\n\
set default_wave_dir 0b0110\n\
\n\
##### 아래 파라미터들은 가급적 수정하지 않는것을 권장함.\n\
\n\
#s2tr : sediments to transports rate, 퇴적물에서 운송상태로 바뀌는 비율\n\
#이 값에 비례해서 침식 비율(값)이 결정됩니다.\n\
set s2tr 0.08\n\
\n\
#alpha_weight : 침식값 가중치(배율)\n\
set alpha_weight 1.2\n\
\n\
#reverse_drop : 운송물 진행방향이 파도방향과 일치하지 않을시, 추가 추락비율\n\
set reverse_drop 0.03\n\
\n\
#default_drop : 운송물이 1m마다 추락하는 비율\n\
set default_drop 0.02\n\
\n\
#min_drop_weight : 운송물 추락값의 최소비율\n\
set min_drop_weight 0.01\n\
\n\
#toppling_rate : 안식각 규칙 1회당 퇴적물값 변경 배율\n\
set toppling_rate 0.1\n\
\n\
#exp_hb : 수렴해안선 공식에서 '쇄파가 시작되는 수심'에 해당하는 값, 단위 m\n\
set exp_hb 3\n\
\n\
#exp_f : 수렴해안선 공식에서의 f, 상수\n\
set exp_f 1.18\n\
\n\
#exp_gamma : 수렴해안선 공식에서의 감마, 상수\n\
set exp_gamma 0.78\n\
" | tee -a $1 >> /dev/null

echo "default config has writed at $1"
exit 0