import streamlit as st
import json
import os
from datetime import datetime, date

# 设置页面配置
st.set_page_config(
    page_title="个人行程计划",
    page_icon="✈️",
    layout="wide"
)

# 初始化数据文件
DATA_FILE = "trip_plans.json"

def init_data():
    """初始化行程数据文件"""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)

def load_plans():
    """加载所有行程计划"""
    init_data()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_plan(plan):
    """保存新行程"""
    plans = load_plans()
    # 添加唯一ID和创建时间
    plan["id"] = len(plans) + 1
    plan["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plans.append(plan)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(plans, f, ensure_ascii=False, indent=4)
    return True

def delete_plan(plan_id):
    """删除指定ID的行程"""
    plans = load_plans()
    new_plans = [p for p in plans if p["id"] != plan_id]
    # 重新分配ID以保持连续
    for i, p in enumerate(new_plans):
        p["id"] = i + 1
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_plans, f, ensure_ascii=False, indent=4)
    return True

# 主页面
def main():
    st.title("✈️ 个人行程计划管理")
    st.divider()

    # 侧边栏 - 添加新行程
    with st.sidebar:
        st.header("添加新行程")
        trip_name = st.text_input("行程名称", placeholder="例如：周末厦门游")
        trip_date = st.date_input("行程日期", value=date.today())
        trip_location = st.text_input("行程地点", placeholder="例如：厦门市思明区")
        trip_description = st.text_area("行程描述", placeholder="详细的行程安排...")
        trip_priority = st.selectbox("优先级", ["低", "中", "高"])

        if st.button("保存行程", type="primary"):
            if trip_name and trip_location:
                new_plan = {
                    "name": trip_name,
                    "date": trip_date.strftime("%Y-%m-%d"),
                    "location": trip_location,
                    "description": trip_description,
                    "priority": trip_priority
                }
                save_plan(new_plan)
                st.success("行程添加成功！")
                st.rerun()  # 刷新页面
            else:
                st.error("行程名称和地点不能为空！")

    # 主内容区 - 显示所有行程
    st.subheader("我的行程列表")
    
    plans = load_plans()
    
    if not plans:
        st.info("暂无行程计划，点击左侧添加吧！")
    else:
        # 按日期排序
        plans_sorted = sorted(plans, key=lambda x: x["date"])
        
        # 遍历显示行程
        for plan in plans_sorted:
            # 创建行程卡片
            with st.expander(f"📅 {plan['date']} | {plan['name']} | 优先级：{plan['priority']}", expanded=True):
                col1, col2 = st.columns([8, 2])
                
                with col1:
                    st.write(f"**地点：** {plan['location']}")
                    st.write(f"**描述：** {plan['description']}")
                    st.write(f"**创建时间：** {plan.get('created_at', '未知')}")
                
                with col2:
                    # 删除按钮
                    if st.button("🗑️ 删除", key=f"delete_{plan['id']}"):
                        delete_plan(plan['id'])
                        st.success("行程已删除！")
                        st.rerun()

if __name__ == "__main__":
    main()