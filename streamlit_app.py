import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium

# 원본 데이터 파일 경로
file_path_1 = "5.xlsx"
file_path_2 = "4.xlsx"

# 첫 번째 데이터 불러오기 (2018~2022년)
try:
    data_1 = pd.read_excel(file_path_1, engine='openpyxl')
    if "연도" not in data_1.columns:
        st.error(f"{file_path_1}에 '연도' 컬럼이 없습니다.")
        st.stop()
    data_1_filtered = data_1[data_1["연도"].isin(range(2018, 2023))]
except FileNotFoundError:
    st.error(f"파일을 찾을 수 없습니다: {file_path_1}")
    st.stop()

# 두 번째 데이터 불러오기 (2021~2023년)
try:
    data_2 = pd.read_excel(file_path_2, engine='openpyxl')
    if "연도" not in data_2.columns:
        st.error(f"{file_path_2}에 '연도' 컬럼이 없습니다.")
        st.stop()
    data_2_filtered = data_2[data_2["연도"].isin(range(2021, 2024))]
except FileNotFoundError:
    st.error(f"파일을 찾을 수 없습니다: {file_path_2}")
    st.stop()

# 좌표 데이터 파일 경로
coord_file_path = "coords.xlsx"
try:
    coord_data = pd.read_excel(coord_file_path, engine='openpyxl')
    coord_dict = coord_data.set_index("행정구역(읍면동)").T.to_dict()
except FileNotFoundError:
    st.error("❌ coords.xlsx 파일을 찾을 수 없습니다.")
    st.stop()

# 연도 선택 (두 데이터의 전체 연도 범위에서 선택)
available_years_1 = sorted(data_1_filtered["연도"].unique(), reverse=True)
available_years_2 = sorted(data_2_filtered["연도"].unique(), reverse=True)
all_available_years = sorted(list(set(available_years_1) | set(available_years_2)), reverse=True)
selected_year = st.selectbox("연도를 선택하세요:", all_available_years)

# 선택한 연도의 데이터 필터링 (각 데이터프레임에서)
filtered_data_1 = data_1_filtered[data_1_filtered["연도"] == selected_year]
filtered_data_2 = data_2_filtered[data_2_filtered["연도"] == selected_year]

# 지도 생성 (대한민국 중심)
map_center = [33.5, 126.5]  # 제주도 중심 좌표
m = folium.Map(location=map_center, zoom_start=10)

# 첫 번째 데이터 지도에 마커 표시
successful_locations_1 = []
missing_locations_1 = []
for _, row in filtered_data_1.iterrows():
    region = row['읍면동']
    crops = {
        '노지온주(극조생)': row['노지온주(극조생)'],
        '노지온주(조생)': row['노지온주(조생)'],
        '노지온주(보통)': row['노지온주(보통)'],
        '하우스감귤(조기출하)': row['하우스감귤(조기출하)'],
        '비가림(월동)감귤': row['비가림(월동)감귤'],
        '만감류(시설)': row['만감류(시설)'],
        '만감류(노지)': row['만감류(노지)']
    }

    if region in coord_dict:
        lat = coord_dict[region]["위도"]
        lon = coord_dict[region]["경도"]
        crop_details = "\n".join([f"{crop}: {amount:,.2f} 톤" for crop, amount in crops.items()])

        folium.Marker(
            location=[lat, lon],
            popup=f"{region}의 재배량:\n{crop_details}",
            tooltip=region,
            icon=folium.Icon(color='blue')  # 첫 번째 데이터 마커 색상 설정
        ).add_to(m)

        successful_locations_1.append(region)
    else:
        missing_locations_1.append(region)

# 두 번째 데이터 지도에 마커 표시
successful_locations_2 = []
missing_locations_2 = []
for _, row in filtered_data_2.iterrows():
    region = row['행정구역(읍면동)']
    crop_amount = row['재배량(톤)']

    if region in coord_dict:
        lat = coord_dict[region]["위도"]
        lon = coord_dict[region]["경도"]
        formatted_crop_amount = f"{crop_amount:,}"
        folium.Marker(
            location=[lat, lon],
            popup=f"{region}: 감귤{formatted_crop_amount}톤",
            tooltip=region,
            icon=folium.Icon(color='green')  # 두 번째 데이터 마커 색상 설정
        ).add_to(m)

        successful_locations_2.append(region)
    else:
        missing_locations_2.append(region)

# 제목 및 메시지 출력
st.title(f"📍 {selected_year}년도 제주도 귤 재배량")

if successful_locations_1 or successful_locations_2:
    st.success(f"총 {len(successful_locations_1) + len(successful_locations_2)}개 지역을 지도에 표시했습니다.")
else:
    st.warning("선택한 연도에 지도에 표시할 수 있는 지역이 없습니다.")

if missing_locations_1 or missing_locations_2:
    st.warning(f"좌표 정보가 없는 지역: {', '.join(missing_locations_1 + missing_locations_2)}")

# 지도 출력
st_folium(m, width=700, height=500)