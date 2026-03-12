import streamlit as st
import pandas as pd
import datetime
from datetime import date
import plotly.express as px

# 設置頁面配置
st.set_page_config(
    page_title="個人行程計劃管理",
    page_icon="🗓️",
    layout="wide"
)

# 初始化會話狀態 - 用於存儲行程數據
if 'trips' not in st.session_state:
    st.session_state.trips = pd.DataFrame({
        'id': [],
        '標題': [],
        '日期': [],
        '時間': [],
        '分類': [],
        '地點': [],
        '備註': [],
        '完成狀態': []
    })
    st.session_state.next_id = 1

# 定義核心功能函數
def add_trip(title, trip_date, trip_time, category, location, notes):
    """添加新行程"""
    new_trip = pd.DataFrame({
        'id': [st.session_state.next_id],
        '標題': [title],
        '日期': [trip_date],
        '時間': [trip_time],
        '分類': [category],
        '地點': [location],
        '備註': [notes],
        '完成狀態': [False]
    })
    st.session_state.trips = pd.concat([st.session_state.trips, new_trip], ignore_index=True)
    st.session_state.next_id += 1
    st.success("行程添加成功！")

def delete_trip(trip_id):
    """刪除指定行程"""
    st.session_state.trips = st.session_state.trips[st.session_state.trips['id'] != trip_id]
    st.success("行程刪除成功！")

def update_trip_status(trip_id, status):
    """更新行程完成狀態"""
    idx = st.session_state.trips[st.session_state.trips['id'] == trip_id].index
    st.session_state.trips.loc[idx, '完成狀態'] = status

# 頁面標題
st.title("🗓️ 個人行程計劃管理系統")
st.divider()

# 側邊欄 - 添加新行程
with st.sidebar:
    st.header("添加新行程")
    
    # 行程表單
    trip_title = st.text_input("行程標題", placeholder="例如：早上8點健身")
    trip_date = st.date_input("行程日期", value=date.today())
    trip_time = st.time_input("行程時間", value=datetime.time(9, 0))
    trip_category = st.selectbox(
        "行程分類",
        ["工作", "學習", "生活", "娛樂", "出行", "其他"]
    )
    trip_location = st.text_input("行程地點", placeholder="可選")
    trip_notes = st.text_area("備註信息", placeholder="可選")
    
    # 添加行程按鈕
    if st.button("添加行程", type="primary"):
        if trip_title.strip() == "":
            st.error("行程標題不能為空！")
        else:
            add_trip(trip_title, trip_date, trip_time, trip_category, trip_location, trip_notes)

# 主頁面 - 行程管理
tab1, tab2, tab3 = st.tabs(["📋 行程列表", "📊 行程統計", "⚙️ 設置"])

with tab1:
    # 篩選功能
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_date = st.date_input("按日期篩選", value=None)
    with col2:
        filter_category = st.selectbox("按分類篩選", ["全部"] + list(st.session_state.trips['分類'].unique()))
    with col3:
        filter_status = st.selectbox("按完成狀態篩選", ["全部", "已完成", "未完成"])
    
    # 應用篩選
    filtered_trips = st.session_state.trips.copy()
    
    if filter_date:
        filtered_trips = filtered_trips[filtered_trips['日期'] == filter_date]
    if filter_category != "全部":
        filtered_trips = filtered_trips[filtered_trips['分類'] == filter_category]
    if filter_status != "全部":
        filtered_trips = filtered_trips[filtered_trips['完成狀態'] == (filter_status == "已完成")]
    
    # 顯示行程列表
    if filtered_trips.empty:
        st.info("暫無行程數據，請添加新行程！")
    else:
        # 按日期和時間排序
        filtered_trips['datetime'] = pd.to_datetime(filtered_trips['日期'].astype(str) + ' ' + filtered_trips['時間'].astype(str))
        filtered_trips = filtered_trips.sort_values('datetime')
        
        # 遍歷顯示每個行程
        for idx, row in filtered_trips.iterrows():
            with st.expander(f"📌 {row['標題']} | {row['日期']} {row['時間']}"):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**分類**: {row['分類']}")
                    st.write(f"**地點**: {row['地點'] if row['地點'] else '未設置'}")
                    st.write(f"**備註**: {row['備註'] if row['備註'] else '無'}")
                    st.write(f"**狀態**: {'✅ 已完成' if row['完成狀態'] else '🔲 未完成'}")
                with col_b:
                    # 狀態切換按鈕
                    new_status = st.checkbox(
                        "標記為完成", 
                        value=row['完成狀態'],
                        key=f"status_{row['id']}"
                    )
                    if new_status != row['完成狀態']:
                        update_trip_status(row['id'], new_status)
                        st.rerun()
                    
                    # 刪除按鈕
                    if st.button("刪除", key=f"delete_{row['id']}", type="secondary"):
                        delete_trip(row['id'])
                        st.rerun()

with tab2:
    # 行程統計可視化
    st.header("行程數據統計")
    
    if st.session_state.trips.empty:
        st.info("暫無數據可統計，請先添加行程！")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            # 分類統計餅圖
            category_counts = st.session_state.trips['分類'].value_counts()
            fig1 = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="行程分類分布",
                hole=0.3
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # 完成狀態統計
            status_counts = st.session_state.trips['完成狀態'].value_counts()
            status_counts.index = status_counts.index.map({True: '已完成', False: '未完成'})
            fig2 = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title="行程完成狀態",
                color=status_counts.index,
                color_discrete_map={'已完成': 'green', '未完成': 'orange'}
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # 每日行程數量
        st.subheader("每日行程數量")
        daily_counts = st.session_state.trips['日期'].value_counts().sort_index()
        fig3 = px.line(
            x=daily_counts.index,
            y=daily_counts.values,
            title="每日行程趨勢",
            markers=True
        )
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.header("系統設置")
    
    # 清空所有行程
    if st.button("清空所有行程", type="secondary"):
        if st.checkbox("確認清空所有數據（不可恢復）"):
            st.session_state.trips = pd.DataFrame({
                'id': [],
                '標題': [],
                '日期': [],
                '時間': [],
                '分類': [],
                '地點': [],
                '備註': [],
                '完成狀態': []
            })
            st.session_state.next_id = 1
            st.success("所有行程已清空！")
            st.rerun()
    
    # 數據導出
    st.subheader("數據導出")
    csv_data = st.session_state.trips.to_csv(index=False)
    st.download_button(
        label="導出為CSV文件",
        data=csv_data,
        file_name=f"行程計劃_{date.today()}.csv",
        mime="text/csv"
    )