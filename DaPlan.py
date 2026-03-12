import streamlit as st
import pandas as pd
import datetime
from datetime import date
import plotly.express as px

# 设置页面配置
st.set_page_config(
    page_title="个人行程计划管理",
    page_icon="🗓️",
    layout="wide"
)

# 初始化会话状态 - 用于存储行程数据
if 'trips' not in st.session_state:
    st.session_state.trips = pd.DataFrame({
        'id': [],
        '标题': [],
        '日期': [],
        '时间': [],
        '分类': [],
        '地点': [],
        '备注': [],
        '完成状态': []
    })
    st.session_state.next_id = 1

# 定义核心功能函数
def add_trip(title, trip_date, trip_time, category, location, notes):
    """添加新行程"""
    new_trip = pd.DataFrame({
        'id': [st.session_state.next_id],
        '标题': [title],
        '日期': [trip_date],
        '时间': [trip_time],
        '分类': [category],
        '地点': [location],
        '备注': [notes],
        '完成状态': [False]
    })
    st.session_state.trips = pd.concat([st.session_state.trips, new_trip], ignore_index=True)
    st.session_state.next_id += 1
    st.success("行程添加成功！")

def delete_trip(trip_id):
    """删除指定行程"""
    st.session_state.trips = st.session_state.trips[st.session_state.trips['id'] != trip_id]
    st.success("行程删除成功！")

def update_trip_status(trip_id, status):
    """更新行程完成状态"""
    idx = st.session_state.trips[st.session_state.trips['id'] == trip_id].index
    st.session_state.trips.loc[idx, '完成状态'] = status

# 页面标题
st.title("🗓️ 个人行程计划管理系统")
st.divider()

# 侧边栏 - 添加新行程
with st.sidebar:
    st.header("添加新行程")
    
    # 行程表单
    trip_title = st.text_input("行程标题", placeholder="例如：早上8点健身")
    trip_date = st.date_input("行程日期", value=date.today())
    trip_time = st.time_input("行程时间", value=datetime.time(9, 0))
    trip_category = st.selectbox(
        "行程分类",
        ["工作", "学习", "生活", "娱乐", "出行", "其他"]
    )
    trip_location = st.text_input("行程地点", placeholder="可选")
    trip_notes = st.text_area("备注信息", placeholder="可选")
    
    # 添加行程按钮
    if st.button("添加行程", type="primary"):
        if trip_title.strip() == "":
            st.error("行程标题不能为空！")
        else:
            add_trip(trip_title, trip_date, trip_time, trip_category, trip_location, trip_notes)

# 主页面 - 行程管理
tab1, tab2, tab3 = st.tabs(["📋 行程列表", "📊 行程统计", "⚙️ 设置"])

with tab1:
    # 筛选功能
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_date = st.date_input("按日期筛选", value=None)
    with col2:
        filter_category = st.selectbox("按分类筛选", ["全部"] + list(st.session_state.trips['分类'].unique()))
    with col3:
        filter_status = st.selectbox("按完成状态筛选", ["全部", "已完成", "未完成"])
    
    # 应用筛选
    filtered_trips = st.session_state.trips.copy()
    
    if filter_date:
        filtered_trips = filtered_trips[filtered_trips['日期'] == filter_date]
    if filter_category != "全部":
        filtered_trips = filtered_trips[filtered_trips['分类'] == filter_category]
    if filter_status != "全部":
        filtered_trips = filtered_trips[filtered_trips['完成状态'] == (filter_status == "已完成")]
    
    # 显示行程列表
    if filtered_trips.empty:
        st.info("暂无行程数据，请添加新行程！")
    else:
        # 按日期和时间排序
        filtered_trips['datetime'] = pd.to_datetime(filtered_trips['日期'].astype(str) + ' ' + filtered_trips['时间'].astype(str))
        filtered_trips = filtered_trips.sort_values('datetime')
        
        # 遍历显示每个行程
        for idx, row in filtered_trips.iterrows():
            with st.expander(f"📌 {row['标题']} | {row['日期']} {row['时间']}"):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**分类**: {row['分类']}")
                    st.write(f"**地点**: {row['地点'] if row['地点'] else '未设置'}")
                    st.write(f"**备注**: {row['备注'] if row['备注'] else '无'}")
                    st.write(f"**状态**: {'✅ 已完成' if row['完成状态'] else '🔲 未完成'}")
                with col_b:
                    # 状态切换按钮
                    new_status = st.checkbox(
                        "标记为完成", 
                        value=row['完成状态'],
                        key=f"status_{row['id']}"
                    )
                    if new_status != row['完成状态']:
                        update_trip_status(row['id'], new_status)
                        st.rerun()
                    
                    # 删除按钮
                    if st.button("删除", key=f"delete_{row['id']}", type="secondary"):
                        delete_trip(row['id'])
                        st.rerun()

with tab2:
    # 行程统计可视化
    st.header("行程数据统计")
    
    if st.session_state.trips.empty:
        st.info("暂无数据可统计，请先添加行程！")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            # 分类统计饼图
            category_counts = st.session_state.trips['分类'].value_counts()
            fig1 = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="行程分类分布",
                hole=0.3
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # 完成状态统计
            status_counts = st.session_state.trips['完成状态'].value_counts()
            status_counts.index = status_counts.index.map({True: '已完成', False: '未完成'})
            fig2 = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title="行程完成状态",
                color=status_counts.index,
                color_discrete_map={'已完成': 'green', '未完成': 'orange'}
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # 每日行程数量
        st.subheader("每日行程数量")
        daily_counts = st.session_state.trips['日期'].value_counts().sort_index()
        fig3 = px.line(
            x=daily_counts.index,
            y=daily_counts.values,
            title="每日行程趋势",
            markers=True
        )
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.header("系统设置")
    
    # 清空所有行程
    if st.button("清空所有行程", type="secondary"):
        if st.checkbox("确认清空所有数据（不可恢复）"):
            st.session_state.trips = pd.DataFrame({
                'id': [],
                '标题': [],
                '日期': [],
                '时间': [],
                '分类': [],
                '地点': [],
                '备注': [],
                '完成状态': []
            })
            st.session_state.next_id = 1
            st.success("所有行程已清空！")
            st.rerun()
    
    # 数据导出
    st.subheader("数据导出")
    csv_data = st.session_state.trips.to_csv(index=False)
    st.download_button(
        label="导出为CSV文件",
        data=csv_data,
        file_name=f"行程计划_{date.today()}.csv",
        mime="text/csv"
    )