import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib


import matplotlib.font_manager as fm
import platform
from matplotlib import rc


# 한글 폰트 설정 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 깃허브 리눅스 기준
if platform.system() == 'Linux':
    fontname = './NanumGothic.ttf'
    font_files = fm.findSystemFonts(fontpaths=fontname)
    fm.fontManager.addfont(fontname)
    fm._load_fontmanager(try_read_cache=False)
    rc('font', family='NanumGothic')

# ✅ 페이지 설정은 가장 먼저!
st.set_page_config(page_title="고당류/고나트륨 식품 알리미", layout="wide")

# ------------------------------
# 1단계: 데이터 불러오기
# ------------------------------
@st.cache_data

def load_data():
    df = pd.read_csv('전국통합식품영양성분정보_가공식품_표준데이터.csv', encoding='cp949')  # CSV 파일 경로와 인코딩 설정
    df = df[df['나트륨(mg)'] < 3000]  # 3000mg 이상 나트륨 데이터 제거
    return df

# 데이터 호출
df = load_data()

# ------------------------------
# 2단계: 사이드바 메뉴 구성
# ------------------------------
st.sidebar.title("📂 메뉴")
view_option = st.sidebar.radio("원하는 정보를 선택하세요:", ["고당류 식품 보기", "고나트륨 식품 보기", "식품명으로 검색"])
sort_order = st.sidebar.radio("당류/나트륨 양의 정렬 순서를 선택하세요:", ["내림차순", "오름차순"])
ascending = sort_order == "오름차순"

# ------------------------------
# 3단계: 타이틀과 설명
# ------------------------------
st.title("🍬 고당류 / 🧂 고나트륨 식품 알리미")

st.markdown("""
이 웹앱은 사용자가 선택한 식품 대분류에 따라
- **당류가 25g 이상이거나**
- **나트륨이 1500mg 이상인**
식품을 확인하고 정렬하며 시각화할 수 있는 건강 정보 제공 도구입니다.

※ 단, **나트륨 3000mg 이상인 식품은 제외**되었습니다.
""")

# ------------------------------
# 4단계: 조건 분기별 화면 구성
# ------------------------------
if view_option == "고당류 식품 보기":
    st.header("📊 대분류별 고당류 식품 개수")
    high_sugar = df[df['당류(g)'] >= 25]
    sugar_summary = high_sugar['식품대분류명'].value_counts().reset_index()
    sugar_summary.columns = ['식품대분류', '개수']
    st.dataframe(sugar_summary)

    # 시각화
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=sugar_summary.sort_values(by='개수', ascending=ascending), x='개수', y='식품대분류', ax=ax, palette='Reds_r')
    ax.set_title("고당류 식품 대분류별 개수")
    st.pyplot(fig)

    st.subheader("🔍 고당류 식품 보기")
    selected_category_sugar = st.selectbox("식품 대분류를 선택하세요:", df['식품대분류명'].dropna().unique(), key="sugar")
    filtered_sugar = df[(df['식품대분류명'] == selected_category_sugar) & (df['당류(g)'] >= 25)]
    filtered_sugar = filtered_sugar.sort_values(by='당류(g)', ascending=ascending).head(10)

    if not filtered_sugar.empty:
        st.bar_chart(filtered_sugar.set_index('식품명')['당류(g)'])
        for _, row in filtered_sugar.iterrows():
            st.markdown(f"**🔶 {row['식품명']}**")
            st.write(f"- 당류: {row['당류(g)']}g")
            st.write(f"- 나트륨: {row['나트륨(mg)']}mg")
            st.warning("🍭 고당류")
    else:
        st.success(f"'{selected_category_sugar}' 대분류에는 고당류 식품이 없습니다.")

elif view_option == "고나트륨 식품 보기":
    st.header("📊 대분류별 고나트륨 식품 개수")
    high_sodium = df[df['나트륨(mg)'] >= 1500]
    sodium_summary = high_sodium['식품대분류명'].value_counts().reset_index()
    sodium_summary.columns = ['식품대분류', '개수']
    st.dataframe(sodium_summary)

    # 시각화
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=sodium_summary.sort_values(by='개수', ascending=ascending), x='개수', y='식품대분류', ax=ax, palette='Blues_r')
    ax.set_title("고나트륨 식품 대분류별 개수")
    st.pyplot(fig)

    st.subheader("🔍 고나트륨 식품 보기")
    selected_category_sodium = st.selectbox("식품 대분류를 선택하세요:", df['식품대분류명'].dropna().unique(), key="sodium")
    filtered_sodium = df[(df['식품대분류명'] == selected_category_sodium) & (df['나트륨(mg)'] >= 2000)]
    filtered_sodium = filtered_sodium.sort_values(by='나트륨(mg)', ascending=ascending).head(10)

    if not filtered_sodium.empty:
        st.bar_chart(filtered_sodium.set_index('식품명')['나트륨(mg)'])
        for _, row in filtered_sodium.iterrows():
            st.markdown(f"**🔶 {row['식품명']}**")
            st.write(f"- 당류: {row['당류(g)']}g")
            st.write(f"- 나트륨: {row['나트륨(mg)']}mg")
            st.warning("🧂 고나트륨")
    else:
        st.success(f"'{selected_category_sodium}' 대분류에는 고나트륨 식품이 없습니다.")

elif view_option == "식품명으로 검색":
    st.header("🔎 식품명으로 검색")
    keyword = st.text_input("검색할 식품명을 입력하세요:")

    if keyword:
        result = df[df['식품명'].str.contains(keyword, case=False, na=False)]
        if not result.empty:
            for _, row in result.iterrows():
                st.markdown(f"**🔶 {row['식품명']}**")
                st.write(f"- 식품 대분류: {row['식품대분류명']}")
                st.write(f"- 당류: {row['당류(g)']}g")
                st.write(f"- 나트륨: {row['나트륨(mg)']}mg")
                if row['당류(g)'] >= 25:
                    st.warning("🍭 고당류")
                if row['나트륨(mg)'] >= 1500:
                    st.warning("🧂 고나트륨")
        else:
            st.error(f"❌ '{keyword}' 식품을 찾을 수 없습니다.")