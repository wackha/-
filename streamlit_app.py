import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

# 页面配置
st.set_page_config(
    page_title="上海现金中心看板",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

#预留真实数据接口
class RealDataConnector:
    """真实数据连接器 - 预留数据接入端口"""
    
    def __init__(self):
        print("🔌 真实数据连接器已初始化")
        print("📝 数据接入说明:")
        print("   1. 替换 load_real_data() 方法连接你的数据库")
        print("   2. 替换 load_real_cost_rates() 方法加载真实成本单价")
        print("   3. 替换 load_real_anomaly_rules() 方法加载异常检测规则")
        
    def load_real_data(self):
        """
        🔌 真实数据加载接口
        
        请在这里替换为你的真实数据源:
        - 数据库连接 (MySQL, PostgreSQL, Oracle等)
        - API接口调用
        - Excel/CSV文件读取
        - 其他数据源
        
        返回格式要求: pandas.DataFrame，包含以下必需字段:
        必需字段:
        - txn_id: 交易ID
        - business_type: 业务类型 ('金库调拨', '金库运送', '上门收款', '现金清点')
        - region: 区域
        - specific_area: 具体地点
        - start_time: 开始时间 (datetime格式)
        - distance_km: 距离(公里)
        - labor_hours: 工时
        - cash_amount: 现金金额
        - vehicle: 车辆
        - security_count: 安保人员数量
        - driver_count: 司机数量
        - equipment_usage: 设备使用率
        - weather: 天气
        
        现金清点专用字段:
        - hundred_notes: 百元券金额
        - non_hundred_notes: 非百元券金额  
        - damaged_notes: 残损券金额
        - hundred_rate: 百元券费率
        - non_hundred_rate: 非百元券费率
        - damaged_rate: 残损券费率
        - base_rate: 基本费率
        """
        
        # 🔴 这里是数据接入点 - 请替换为你的真实数据源
        print("⚠️  当前使用模拟数据，请在 load_real_data() 方法中接入真实数据源")
        return None
    
    def load_real_cost_rates(self):
        """
        🔌 真实成本单价加载接口
        
        请在这里替换为你的真实成本单价数据源
        
        返回格式: dict，包含成本单价配置
        """
        
        # 🔴 这里是成本单价接入点 - 请替换为你的真实数据
        print("⚠️  当前使用默认成本单价，请在 load_real_cost_rates() 方法中接入真实成本配置")
        return None
    
    def load_real_anomaly_rules(self):
        """
        🔌 真实异常检测规则加载接口
        
        请在这里替换为你的真实异常检测规则
        
        返回格式: dict，包含异常检测参数
        """
        
        # 🔴 这里是异常规则接入点 - 请替换为你的真实规则
        print("⚠️  当前使用默认异常检测规则，请在 load_real_anomaly_rules() 方法中接入真实规则")
        return None

# 自定义CSS样式 - 白底主题，大字体版本
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
        background-color: #ffffff;
    }
    .stMetric {
        background-color: #f8f9fa;
        border: 1px solid #007bff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0, 123, 255, 0.15);
        font-size: 1.2rem !important;
    }
    .stMetric label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    .stMetric .metric-value {
        font-size: 1.8rem !important;
        font-weight: bold !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 1px solid #007bff;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
    }
    .stApp {
        background-color: #ffffff;
    }
    /* 修改侧边栏背景 */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    /* 大字体样式类 */
    .big-font {
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        color: #333 !important;
        line-height: 1.6 !important;
    }
    .huge-font {
        font-size: 2rem !important;
        font-weight: bold !important;
        color: #007bff !important;
        line-height: 1.4 !important;
    }
    .large-container {
        background: white;
        border: 2px solid #007bff;
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 6px 20px rgba(0, 123, 255, 0.15);
        font-size: 1.2rem;
    }
    /* Streamlit表格字体放大 */
    .stDataFrame {
        font-size: 1.1rem !important;
    }
    /* 按钮字体放大 */
    .stButton button {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
    }
    /* Expander标题字体放大 */
    .streamlit-expander {
        font-size: 1.2rem !important;
    }
    /* Plotly图表字体 */
    .plotly .svg-container {
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

def get_shanghai_area_classification():
    """上海区域分类：市区、近郊、远郊"""
    return {
        # 市区（网点密集，标准公里数较少）
        '市区': {
            'regions': ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '虹口区', '杨浦区'],
            'standard_km': {
                '金库运送': 8,     # 市区金库运送标准8公里
                '上门收款': 10,    # 市区上门收款标准10公里
                '现金清点': 0      # 现金清点无距离费用
            }
        },
        # 近郊（网点适中，标准公里数适中）
        '近郊': {
            'regions': ['闵行区', '宝山区', '嘉定区', '浦东新区'],
            'standard_km': {
                '金库运送': 30,    # 近郊金库运送标准30公里
                '上门收款': 35,    # 近郊上门收款标准35公里
                '现金清点': 0      # 现金清点无距离费用
            }
        },
        # 远郊（网点稀少，标准公里数较多）
        '远郊': {
            'regions': ['金山区', '松江区', '青浦区', '奉贤区', '崇明区'],
            'standard_km': {
                '金库运送': 45,    # 远郊金库运送标准45公里
                '上门收款': 50,    # 远郊上门收款标准50公里
                '现金清点': 0      # 现金清点无距离费用
            }
        }
    }

def get_area_type(region):
    """根据区域获取地区类型"""
    area_classification = get_shanghai_area_classification()
    for area_type, config in area_classification.items():
        if region in config['regions']:
            return area_type
    return '近郊'  # 默认返回近郊

def calculate_cash_counting_cost(amount):
    """
    现金清点成本计算函数
    根据金额大小区分大笔清点和小笔清点
    """
    # 设定大笔清点阈值（100万以上为大笔）
    large_amount_threshold = 1000000
    
    if amount >= large_amount_threshold:
        # 大笔清点：2个人 + 机器
        # 人工成本：15000元/月/人 × 2人
        monthly_labor_cost = 15000 * 2
        # 机器折旧：200万设备，30年折旧期
        machine_cost = 2000000 / (30 * 12)  # 每月折旧成本
        monthly_total_cost = monthly_labor_cost + machine_cost
        
        # 按工作日计算（每月22个工作日，每天8小时）
        hourly_cost = monthly_total_cost / (22 * 8)
        
        # 大笔清点时间：2-4小时
        processing_hours = np.random.uniform(2, 4)
        
        total_cost = hourly_cost * processing_hours
        
        return {
            'total_cost': total_cost,
            'labor_cost': (monthly_labor_cost / (22 * 8)) * processing_hours,
            'equipment_cost': (machine_cost / (22 * 8)) * processing_hours,
            'time_duration': processing_hours * 60,  # 转换为分钟
            'counting_type': '大笔清点',
            'staff_count': 2,
            'has_machine': True,
            'processing_hours': processing_hours
        }
    else:
        # 小笔清点：8个人手工清点
        # 人工成本：7000-8000元/月/人，8个人
        avg_salary = np.random.uniform(7000, 8000)
        monthly_labor_cost = avg_salary * 8
        
        # 无机器成本
        monthly_total_cost = monthly_labor_cost
        
        # 按工作日计算
        hourly_cost = monthly_total_cost / (22 * 8)
        
        # 小笔清点时间：1-3小时
        processing_hours = np.random.uniform(1, 3)
        
        total_cost = hourly_cost * processing_hours
        
        return {
            'total_cost': total_cost,
            'labor_cost': total_cost,  # 小笔清点全部为人工成本
            'equipment_cost': 0,       # 无设备成本
            'time_duration': processing_hours * 60,  # 转换为分钟
            'counting_type': '小笔清点',
            'staff_count': 8,
            'has_machine': False,
            'processing_hours': processing_hours
        }

# ...existing code...
def calculate_vehicle_cost(distance_km, time_hours, business_type, region):
    """
    统一运钞车成本计算函数（与金额无关）
    """
    hourly_cost = 75000 / 30 / 8  # 312.5元/小时
    basic_cost = time_hours * hourly_cost
    standard_time = {
        '金库运送': distance_km * 0.08 + 0.5,
        '上门收款': distance_km * 0.1 + 0.8,
    }
    overtime_hours = max(0, time_hours - standard_time.get(business_type, 1.0))
    overtime_cost = overtime_hours * 300
    over_km_cost = 0
    standard_distance = 0
    if business_type in ['金库运送', '上门收款']:
        area_type = get_area_type(region)
        area_classification = get_shanghai_area_classification()
        standard_distance = area_classification[area_type]['standard_km'].get(business_type, 15)
        over_km = max(0, distance_km - standard_distance)
        over_km_cost = over_km * 12
    return basic_cost + overtime_cost + over_km_cost, {
        'basic_cost': basic_cost,
        'overtime_cost': overtime_cost,
        'over_km_cost': over_km_cost,
        'standard_distance': standard_distance,
        'area_type': get_area_type(region) if business_type in ['金库运送', '上门收款'] else '无'
    }

def calculate_vault_transfer_cost():
    """
    金库调拨专用成本计算函数（与金额无关）
    """
    hourly_cost = 75000 / 30 / 8
    base_hours = np.random.uniform(1, 2)
    overtime_hours = np.random.uniform(0.5, 1.5) if np.random.random() < 0.1 else 0
    over_km = np.random.uniform(1, 3) if np.random.random() < 0.05 else 0
    basic_cost = base_hours * hourly_cost
    overtime_cost = overtime_hours * 300
    over_km_cost = over_km * 12
    total_vehicle_cost = basic_cost + overtime_cost + over_km_cost
    total_time = (base_hours + overtime_hours) * 60
    return {
        'vehicle_cost': total_vehicle_cost,
        'time_duration': total_time,
        'basic_cost': basic_cost,
        'overtime_cost': overtime_cost,
        'over_km_cost': over_km_cost,
        'distance_km': 15.0,
        'standard_distance': 15,
        'area_type': '专线',
        'amount': np.random.uniform(5000000, 20000000)  # 仅用于展示，不参与成本
    }

# 数据生成函数
@st.cache_data(ttl=60)  # 缓存1分钟
def generate_sample_data():
    """生成示例数据 - 根据业务比例要求调整"""
    np.random.seed(int(time.time()) // 60)  # 每分钟更新
    
    business_types = ['金库运送', '上门收款', '金库调拨', '现金清点']
    # 业务比例配置：金库运送占大头(45%)，上门收款较少(20%)，现金清点为两者40%(28.75%)，金库调拨每天1次(6.25%)
    business_probabilities = [0.45, 0.20, 0.0625, 0.2875]
    
    regions = ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '虹口区', '杨浦区', '闵行区',
              '宝山区', '嘉定区', '浦东新区', '金山区', '松江区', '青浦区', '奉贤区', '崇明区']
    
    n_records = 300
    
    # 生成业务类型
    business_type_list = np.random.choice(business_types, n_records, p=business_probabilities)
    
    # 生成区域，金库调拨特殊处理
    region_list = []
    for i in range(n_records):
        if business_type_list[i] == '金库调拨':
            # 金库调拨固定为浦东新区（浦东到浦西）
            region_list.append('浦东新区')
        else:
            # 其他业务类型随机选择区域
            region_list.append(np.random.choice(regions))
    
    # 生成金额数据，确保现金清点业务有合理的大笔小笔分布
    amount_list = []
    for i in range(n_records):
        if business_type_list[i] == '现金清点':
            # 现金清点：30%概率为大笔(100万以上)，70%概率为小笔
            if np.random.random() < 0.3:
                amount = np.random.uniform(1000000, 10000000)
            else:
                amount = np.random.uniform(10000, 800000)
            amount_list.append(amount)
        elif business_type_list[i] == '金库调拨':
            # 金库调拨金额可以保留，但后续成本计算不再用到
            amount_list.append(np.random.uniform(5000000, 20000000))
        else:
            # 金库运送、上门收款金额随机，但不影响成本
            amount_list.append(np.random.uniform(10000, 1000000))
    
    data = {
        'txn_id': [f'TXN{i:06d}' for i in range(n_records)],
        'business_type': business_type_list,
        'region': region_list,
        'amount': amount_list,  # 使用新的金额生成逻辑
        'distance_km': np.random.gamma(2, 5, n_records),
        'time_duration': np.random.gamma(3, 20, n_records),
        'vehicle_cost': np.random.normal(200, 50, n_records),
        'labor_cost': np.random.normal(150, 30, n_records),
        'efficiency_ratio': np.random.beta(3, 2, n_records),
        'start_time': pd.date_range(start=datetime.now() - timedelta(hours=24), 
                                   periods=n_records, freq='5min'),
        'is_anomaly': np.random.choice([True, False], n_records, p=[0.1, 0.9]),
        # 新增字段：市场冲击场景
        'market_scenario': np.random.choice(['正常', '高需求期', '紧急状况', '节假日'], 
                                          n_records, p=[0.6, 0.2, 0.1, 0.1]),
        # 动态时段权重
        'time_weight': np.random.choice([1.0, 1.1, 1.3, 1.6], n_records, p=[0.4, 0.3, 0.2, 0.1])
    }
    
    df = pd.DataFrame(data)
    
    # 特殊处理金库调拨的距离和成本
    vault_transfer_mask = df['business_type'] == '金库调拨'
    
    # 金库调拨固定距离15km
    df.loc[vault_transfer_mask, 'distance_km'] = 15.0
    
    # 运钞车成本计算：75000元/月 ÷ 30天 ÷ 8小时 = 312.5元/小时
    hourly_cost = 75000 / 30 / 8  # 312.5元/小时
    
    # 金库调拨成本构成
    vault_count = vault_transfer_mask.sum()
    if vault_count > 0:
        # 基础运行时间（假设1-2小时）
        base_hours = np.random.uniform(1, 2, vault_count)
        
        # 超时情况（10%概率超时0.5-1.5小时）
        overtime_hours = np.where(
            np.random.random(vault_count) < 0.1,  # 10%概率超时
            np.random.uniform(0.5, 1.5, vault_count),
            0
        )
        
        # 超公里情况（5%概率超出1-3公里）
        over_km = np.where(
            np.random.random(vault_count) < 0.05,  # 5%概率超公里
            np.random.uniform(1, 3, vault_count),
            0
        )
        
        # 计算总成本
        basic_cost = base_hours * hourly_cost  # 基础成本
        overtime_cost = overtime_hours * 300   # 超时费用
        over_km_cost = over_km * 12           # 超公里费用
    
    df.loc[vault_transfer_mask, 'vehicle_cost'] = basic_cost + overtime_cost + over_km_cost
    df.loc[vault_transfer_mask, 'labor_cost'] = np.random.uniform(200, 400, vault_count)  # 人工成本
    df.loc[vault_transfer_mask, 'amount'] = np.random.uniform(5000000, 20000000, vault_count)  # 调拨金额
    df.loc[vault_transfer_mask, 'time_duration'] = (base_hours + overtime_hours) * 60  # 转换为分钟

    # 计算各业务类型的成本（使用新的分类计算方法）
    vehicle_costs = []
    labor_costs = []
    equipment_costs = []
    time_durations = []
    cost_details = []
    counting_details = []  # 现金清点详情
    
    for idx, row in df.iterrows():
        business_type = row['business_type']
        
        if business_type == '现金清点':
            # 现金清点：使用专门的成本计算
            counting_result = calculate_cash_counting_cost(row['amount'])
            
            vehicle_costs.append(0)  # 现金清点无车辆成本
            labor_costs.append(counting_result['labor_cost'])
            equipment_costs.append(counting_result['equipment_cost'])
            time_durations.append(counting_result['time_duration'])
            counting_details.append(counting_result)
            
            # 成本明细
            cost_details.append({
                'basic_cost': 0,
                'overtime_cost': 0,
                'over_km_cost': 0,
                'standard_distance': 0,
                'area_type': '清点中心'
            })
            
        elif business_type == '金库调拨':
            # 金库调拨：使用专门的成本计算
            vault_result = calculate_vault_transfer_cost()
            
            vehicle_costs.append(vault_result['vehicle_cost'])
            labor_costs.append(vault_result['labor_cost'])
            equipment_costs.append(0)  # 金库调拨无特殊设备成本
            time_durations.append(vault_result['time_duration'])
            counting_details.append({})  # 空的清点详情
            
            # 成本明细
            cost_details.append({
                'basic_cost': vault_result['basic_cost'],
                'overtime_cost': vault_result['overtime_cost'],
                'over_km_cost': vault_result['over_km_cost'],
                'standard_distance': vault_result['standard_distance'],
                'area_type': vault_result['area_type']
            })
            
        else:
            # 金库运送、上门收款：使用通用车辆成本计算
            time_hours = row['time_duration'] / 60  # 转换为小时
            vehicle_cost, cost_detail = calculate_vehicle_cost(
                row['distance_km'], 
                time_hours, 
                row['region']
            )
            
            vehicle_costs.append(vehicle_cost)
            equipment_costs.append(row['distance_km'] * 2.5)  # 设备成本按距离计算
            time_durations.append(row['time_duration'])
            counting_details.append({})  # 空的清点详情
            cost_details.append(cost_detail)
    
    # 更新DataFrame
    df['vehicle_cost'] = vehicle_costs
    df['labor_cost'] = labor_costs
    df['equipment_cost'] = equipment_costs
    df['time_duration'] = time_durations
    
    # 添加成本明细
    df['area_type'] = [detail['area_type'] for detail in cost_details]
    df['standard_distance'] = [detail['standard_distance'] for detail in cost_details]
    df['basic_cost'] = [detail['basic_cost'] for detail in cost_details]
    df['overtime_cost'] = [detail['overtime_cost'] for detail in cost_details]
    df['over_km_cost'] = [detail['over_km_cost'] for detail in cost_details]
    
    # 添加现金清点详情
    df['counting_type'] = [detail.get('counting_type', '') for detail in counting_details]
    df['staff_count'] = [detail.get('staff_count', 0) for detail in counting_details]
    df['has_machine'] = [detail.get('has_machine', False) for detail in counting_details]
    
    # 基于市场场景和时段权重动态调整成本
    df['scenario_multiplier'] = df['market_scenario'].map({
        '正常': 1.0, '高需求期': 1.1, '紧急状况': 1.5, '节假日': 1.5
    })
    df['total_cost'] = (df['vehicle_cost'] + df['distance_km'] * 2.5) * df['scenario_multiplier'] * df['time_weight']
    df['cost_per_km'] = df['total_cost'] / df['distance_km']
    
    return df

# 添加历史数据生成函数
@st.cache_data(ttl=300)  # 缓存5分钟
def generate_historical_data(days=7):
    """生成历史数据用于趋势分析"""
    all_data = []
    business_types = ['金库运送', '上门收款', '金库调拨', '现金清点']
    business_probabilities = [0.50, 0.25, 0.0625, 0.1875]
    
    for day in range(days):
        date = datetime.now() - timedelta(days=day)
        daily_records = np.random.poisson(40)  # 每天平均40笔业务
        
        for _ in range(daily_records):
            record = {
                'date': date.date(),
                'business_type': np.random.choice(business_types, p=business_probabilities),
                'total_cost': np.random.gamma(2, 100),
                'efficiency_ratio': np.random.beta(3, 2),
                'is_anomaly': np.random.choice([True, False], p=[0.1, 0.9])
            }
            all_data.append(record)
    
    return pd.DataFrame(all_data)

# 成本优化分析函数
def analyze_cost_optimization(df):
    """成本分摊优化分析"""
    optimization_data = {
        'current_efficiency': df['efficiency_ratio'].mean(),
        'optimization_potential': 0.15 + np.random.uniform(0, 0.2),
        'cost_reduction_estimate': 0.08 + np.random.uniform(0, 0.17),
        'time_weights': {
            '早班(6-14)': 1.0, 
            '中班(14-22)': 1.0, 
            '晚班(22-6)': 1.3, 
            '节假日': 1.5
        }
    }
    return optimization_data

# 主标题 - 白底主题
st.markdown("""
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); border-radius: 15px; margin-bottom: 30px; border: 2px solid #007bff; box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);'>
    <h1 style='color: #007bff; font-size: 2.5rem; margin: 0; text-shadow: none;'>🏦 动态成本管理看板</h1>
    <p style='color: #6c757d; font-size: 1.2rem; margin: 10px 0 0 0; font-weight: 500;'>Dynamic Cost Management Dashboard | 实时监控 + 成本优化 + 趋势分析</p>
</div>
""", unsafe_allow_html=True)

# 生成数据
df = generate_sample_data()
historical_df = generate_historical_data(10)
cost_optimization = analyze_cost_optimization(df)

# 核心指标展示 - 第一行4个指标
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 总业务量",
        value=f"{len(df):,}",
        delta=f"+{np.random.randint(5, 25)}"
    )

with col2:
    total_cost = df['total_cost'].sum()
    st.metric(
        label="💰 总成本",
        value=f"¥{total_cost:,.0f}",
        delta=f"{np.random.uniform(-5, 15):+.1f}%"
    )

with col3:
    avg_efficiency = df['efficiency_ratio'].mean()
    st.metric(
        label="⚡ 运营效率",
        value=f"{avg_efficiency:.3f}",
        delta=f"{np.random.uniform(-2, 8):+.1f}%"
    )

with col4:
    anomaly_rate = df['is_anomaly'].mean() * 100
    st.metric(
        label="🚨 异常率",
        value=f"{anomaly_rate:.1f}%",
        delta=f"{np.random.uniform(-1, 3):+.1f}%"
    )

# 第二行 - 优化潜力指标，使用居中布局
st.markdown('<div style="margin: 20px 0;"></div>', unsafe_allow_html=True)

# 使用三列布局，中间列放置指标，实现居中效果
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    optimization_potential = cost_optimization['optimization_potential'] * 100
    
    # 使用HTML样式创建突出显示的优化潜力指标
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        color: white;
        box-shadow: 0 6px 20px rgba(40, 167, 69, 0.3);
        margin: 10px 0;
    '>
        <h3 style='margin: 0 0 10px 0; font-size: 1.2rem;'>🎯 优化潜力 & 成本节约预估</h3>
        <h1 style='margin: 0; font-size: 2.5rem; font-weight: bold;'>{optimization_potential:.1f}%</h1>
        <p style='margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;'>
            预计节约 ¥{total_cost * cost_optimization['cost_reduction_estimate']:,.0f}
        </p>
    </div>
    """, unsafe_allow_html=True)

# 图表展示区域
st.markdown("---")

# 控制面板
st.subheader("🎮 动态管理控制面板")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔄 实时刷新", type="primary"):
        st.cache_data.clear()
        st.rerun()

with col2:
    data_export = st.selectbox("数据导出", ["📊 Excel格式", "📄 CSV格式", "📋 PDF报告"], key="data_export_select")

with col3:
    analysis_mode = st.selectbox("分析模式", ["🔬 深度分析", "📊 标准分析", "⚡ 快速分析"], key="analysis_mode_select")

with col4:
    update_mode = st.selectbox("更新模式", ["🚀 实时模式", "⚡ 快速模式", "🔄 标准模式"], key="update_mode_select")

# 详细业务报告模块
st.markdown("---")
st.subheader("📊 详细业务报告与核心指标分析")

# 计算成本效率指标
cost_efficiency = df['total_cost'] / df['efficiency_ratio']
high_efficiency = df[df['efficiency_ratio'] > 0.7]
low_efficiency = df[df['efficiency_ratio'] <= 0.5]

col_d1, col_d2, col_d3 = st.columns(3)
with col_d1:
    st.markdown('<div class="big-font">📈 高效率业务</div>', unsafe_allow_html=True)
    st.metric("高效率业务占比", f"{len(high_efficiency)/len(df)*100:.1f}%")
with col_d2:
    st.markdown('<div class="big-font">📉 低效率业务</div>', unsafe_allow_html=True)
    st.metric("低效率业务占比", f"{len(low_efficiency)/len(df)*100:.1f}%")
with col_d3:
    st.markdown('<div class="big-font">⚖️ 成本效率</div>', unsafe_allow_html=True)
    st.metric("成本效率比", f"{cost_efficiency.mean():.0f}")

# 金库调拨专项分析
st.markdown('<h3 class="huge-font">📊 金库调拨专项分析</h3>', unsafe_allow_html=True)
vault_data = df[df['business_type'] == '金库调拨']
if len(vault_data) > 0:
    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        st.metric("调拨业务数量", len(vault_data))
        st.metric("平均调拨金额", f"¥{vault_data['amount'].mean():,.0f}")
    with col_v2:
        st.metric("固定距离", "15.0km")
        st.metric("平均运输时长", f"{vault_data['time_duration'].mean():.0f}分钟")
    with col_v3:
        st.metric("调拨总成本", f"¥{vault_data['total_cost'].sum():.0f}")
        st.metric("平均车辆成本", f"¥{vault_data['vehicle_cost'].mean():.0f}")
    
    # 显示成本构成详情
    st.markdown("#### 💰 运钞车成本构成分析")
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    
    with col_c1:
        hourly_rate = 75000 / 30 / 8
        st.metric("基础时成本", f"¥{hourly_rate:.1f}/小时")
        st.caption("75000元/月 ÷ 30天 ÷ 8小时")
    
    with col_c2:
        st.metric("超时费率", "¥300/小时")
        overtime_total = vault_data['overtime_cost'].sum() if 'overtime_cost' in vault_data.columns else 0
        st.caption(f"本批次超时费：¥{overtime_total:.0f}")
    
    with col_c3:
        st.metric("超公里费率", "¥12/公里")
        over_km_total = vault_data['over_km_cost'].sum() if 'over_km_cost' in vault_data.columns else 0
        st.caption(f"本批次超公里费：¥{over_km_total:.0f}")
    
    with col_c4:
        st.metric("标准公里数", "15km")
        st.caption("金库调拨统一标准")
    
    st.info("🚗 金库调拨业务：浦东新区 → 黄浦区，固定15km路线，统一标准公里数")
else:
    st.warning("当前时段无金库调拨业务")

# 现金清点专项分析
st.markdown('<h3 class="huge-font">💰 现金清点专项分析</h3>', unsafe_allow_html=True)
counting_data = df[df['business_type'] == '现金清点']
if len(counting_data) > 0:
    # 大笔和小笔清点分析
    large_counting = counting_data[counting_data['counting_type'] == '大笔清点']
    small_counting = counting_data[counting_data['counting_type'] == '小笔清点']
    
    col_c1, col_c2, col_c3 = st.columns(3)
    
    with col_c1:
        st.metric("清点业务总数", len(counting_data))
        st.metric("平均清点金额", f"¥{counting_data['amount'].mean():,.0f}")
    
    with col_c2:
        st.metric("大笔清点数量", len(large_counting))
        st.metric("小笔清点数量", len(small_counting))
    
    with col_c3:
        st.metric("清点总成本", f"¥{counting_data['total_cost'].sum():.0f}")
        st.metric("平均清点时长", f"{counting_data['time_duration'].mean():.0f}分钟")
    
    # 现金清点专用成本构成分析
    st.markdown("#### 💰 现金清点成本构成分析") 
    col_cost1, col_cost2, col_cost3, col_cost4 = st.columns(4)
    
    with col_cost1:
        if len(large_counting) > 0:
            st.metric("大笔清点人工成本", f"¥{large_counting['labor_cost'].mean():.0f}")
            st.caption("2人 × 15000元/月")
        else:
            st.metric("大笔清点人工成本", "¥0")
            st.caption("数据生成中...")
    
    with col_cost2:
        if len(large_counting) > 0:
            st.metric("机器折旧成本", f"¥{large_counting['equipment_cost'].mean():.0f}")
            st.caption("200万设备，30年折旧")
        else:
            st.metric("机器折旧成本", "¥0")
            st.caption("数据生成中...")
    
    with col_cost3:
        if len(small_counting) > 0:
            st.metric("小笔清点人工成本", f"¥{small_counting['labor_cost'].mean():.0f}")
            st.caption("8人 × 7000-8000元/月")
        else:
            st.metric("小笔清点人工成本", "¥0")
            st.caption("数据生成中...")
    
    with col_cost4:
        # ✅ 正确位置：现金清点效率指标
        if len(counting_data) > 0:
            # 计算现金清点专用效率：处理金额/(时长×人员数)
            counting_data_copy = counting_data.copy()
            counting_data_copy['counting_efficiency'] = (
                counting_data_copy['amount'] / 
                (counting_data_copy['time_duration'] * counting_data_copy['staff_count'])
            )
            avg_counting_efficiency = counting_data_copy['counting_efficiency'].mean()
            
            st.metric("清点效率", f"{avg_counting_efficiency:.0f}")
            st.caption("元/(分钟·人)")
        else:
            st.metric("清点效率", "0")
            st.caption("暂无清点数据")
    
    # 大笔vs小笔对比图表
    if len(large_counting) > 0 and len(small_counting) > 0:
        comparison_data = pd.DataFrame({
            '清点类型': ['大笔清点', '小笔清点'],
            '业务数量': [len(large_counting), len(small_counting)],
            '平均成本': [large_counting['total_cost'].mean(), small_counting['total_cost'].mean()],
            '平均时长': [large_counting['time_duration'].mean(), small_counting['time_duration'].mean()]
        })
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig_count = px.pie(
                comparison_data,
                values='业务数量',
                names='清点类型',
                title="大笔vs小笔清点业务占比",
                color_discrete_sequence=['#28a745', '#ffc107']
            )
            fig_count.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                font_color='black'
            )
            st.plotly_chart(fig_count, use_container_width=True)
        
        with col_chart2:
            fig_cost = px.bar(
                comparison_data,
                x='清点类型',
                y='平均成本',
                title="大笔vs小笔平均成本对比",
                color='清点类型',
                color_discrete_sequence=['#28a745', '#ffc107']
            )
            fig_cost.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                font_color='black'
            )
            st.plotly_chart(fig_cost, use_container_width=True)
    elif len(large_counting) > 0 or len(small_counting) > 0:
        st.info("📊 数据生成中，完整对比图表将在下次刷新时显示")
    
    # 业务分布说明
    large_rate = len(large_counting) / len(counting_data) * 100 if len(counting_data) > 0 else 0
    small_rate = len(small_counting) / len(counting_data) * 100 if len(counting_data) > 0 else 0
    
    st.info(f"💰 现金清点业务分布：大笔清点({large_rate:.1f}%) - 机器+2人 | 小笔清点({small_rate:.1f}%) - 8人手工")
else:
    st.warning("当前时段无现金清点业务")

# 风险预警分析
st.markdown('<h3 class="huge-font">🚨 风险预警分析</h3>', unsafe_allow_html=True)
high_cost_threshold = df['total_cost'].quantile(0.9)
high_cost_businesses = df[df['total_cost'] > high_cost_threshold]

if len(high_cost_businesses) > 0:
    st.markdown(f'<div class="big-font" style="color: #dc3545; padding: 15px; background: #f8d7da; border-radius: 10px; margin: 15px 0;">⚠️ 发现 {len(high_cost_businesses)} 笔高成本业务需要关注</div>', unsafe_allow_html=True)
    
    # 格式化显示数据，所有数值精确到个位数
    display_data = high_cost_businesses[['txn_id', 'business_type', 'region', 'total_cost', 'market_scenario', 'amount', 'distance_km', 'time_duration']].copy()
    display_data['total_cost'] = display_data['total_cost'].round(0).astype(int)
    display_data['amount'] = display_data['amount'].round(0).astype(int)  
    display_data['distance_km'] = display_data['distance_km'].round(0).astype(int)
    display_data['time_duration'] = display_data['time_duration'].round(0).astype(int)
    
    st.dataframe(display_data, use_container_width=True)
    
    # 风险业务统计
    col_risk1, col_risk2, col_risk3, col_risk4 = st.columns(4)
    with col_risk1:
        st.metric("高风险业务数", len(high_cost_businesses))
    with col_risk2:
        st.metric("平均风险成本", f"¥{high_cost_businesses['total_cost'].mean():.0f}")
    with col_risk3:
        st.metric("最高风险成本", f"¥{high_cost_businesses['total_cost'].max():.0f}")
    with col_risk4:
        risk_rate = len(high_cost_businesses) / len(df) * 100
        st.metric("风险业务占比", f"{risk_rate:.1f}%")
else:
    st.markdown('<div class="big-font" style="color: #28a745; padding: 15px; background: #d4edda; border-radius: 10px; margin: 15px 0;">✅ 当前所有业务成本均在正常范围内</div>', unsafe_allow_html=True)

# 市场冲击模拟与预警
st.markdown("---")
st.subheader("🌊 市场冲击模拟与多层次预警系统")

col1, col2 = st.columns([2, 1])

with col1:
    # 市场场景分布
    scenario_counts = df['market_scenario'].value_counts()
    fig_scenario = px.pie(
        values=scenario_counts.values,
        names=scenario_counts.index,
        title="当前市场场景分布",
        color_discrete_sequence=['#007bff', '#28a745', '#dc3545', '#17a2b8']
    )
    fig_scenario.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font_color='black'
    )
    st.plotly_chart(fig_scenario, use_container_width=True)

with col2:
    st.write("### 🚨 风险预警分析")
    high_cost_threshold = df['total_cost'].quantile(0.9)
    high_cost_businesses = df[df['total_cost'] > high_cost_threshold]
    
    if len(high_cost_businesses) > 0:
        st.markdown(f'<div class="big-font" style="color: #dc3545; padding: 15px; background: #f8d7da; border-radius: 10px; margin: 15px 0;">⚠️ 发现 {len(high_cost_businesses)} 笔高成本业务需要关注</div>', unsafe_allow_html=True)
        
        # 格式化显示数据，所有数值精确到个位数
        display_data = high_cost_businesses[['txn_id', 'business_type', 'region', 'total_cost', 'market_scenario', 'amount', 'distance_km', 'time_duration']].copy()
        display_data['total_cost'] = display_data['total_cost'].round(0).astype(int)
        display_data['amount'] = display_data['amount'].round(0).astype(int)  
        display_data['distance_km'] = display_data['distance_km'].round(0).astype(int)
        display_data['time_duration'] = display_data['time_duration'].round(0).astype(int)
        
        st.dataframe(display_data, use_container_width=True)
    else:
        st.markdown('<div class="big-font" style="color: #28a745; padding: 15px; background: #d4edda; border-radius: 10px; margin: 15px 0;">✅ 当前所有业务成本均在正常范围内</div>', unsafe_allow_html=True)

# 第一行图表
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 业务类型成本分布")
    business_costs = df.groupby('business_type')['total_cost'].sum().reset_index()
    
    # 为金库调拨添加特殊标注
    business_costs['display_name'] = business_costs['business_type'].apply(
        lambda x: f"{x} (浦东→浦西)" if x == '金库调拨' else x
    )
    
    fig_pie = px.pie(
        business_costs, 
        values='total_cost', 
        names='display_name',
        title="各业务类型成本占比 (金库调拨: 浦东→浦西专线)",
        color_discrete_sequence=['#007bff', '#28a745', '#ffc107', '#dc3545']
    )
    fig_pie.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font_color='black'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("🗺️ 上海16区成本分布")
    region_costs = df.groupby('region')['total_cost'].mean().reset_index()
    fig_bar = px.bar(
        region_costs, 
        x='region', 
        y='total_cost',
        title="各区平均成本",
        color='total_cost',
        color_continuous_scale='Viridis'
    )
    fig_bar.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font_color='black',
        xaxis_tickangle=45
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# 第二行图表
col1, col2 = st.columns(2)

with col1:
    st.subheader("⏰ 时段成本趋势")
    df['hour'] = df['start_time'].dt.hour
    hourly_costs = df.groupby('hour')['total_cost'].mean().reset_index()
    fig_line = px.line(
        hourly_costs, 
        x='hour', 
        y='total_cost',
        title="24小时成本变化趋势",
        markers=True
    )
    fig_line.update_traces(
        line_color='#007bff',
        marker_color='#0056b3',
        marker_size=8
    )
    fig_line.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font_color='black'
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    st.subheader("💡 效率 vs 成本分析")
    fig_scatter = px.scatter(
        df, 
        x='efficiency_ratio', 
        y='total_cost',
        color='is_anomaly',
        title="效率与成本关系散点图",
        color_discrete_map={True: '#dc3545', False: '#007bff'},
        labels={'is_anomaly': '是否异常'}
    )
    fig_scatter.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font_color='black'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# 成本分摊优化分析
st.markdown("---")
st.subheader("⚡ 动态数据驱动的成本分摊优化")

col1, col2 = st.columns(2)

with col1:
    # 时段成本权重动态调整
    time_weights = cost_optimization['time_weights']
    fig_weights = px.bar(
        x=list(time_weights.keys()),
        y=list(time_weights.values()),
        title="时段成本权重动态配置",
        color=list(time_weights.values()),
        color_continuous_scale='Viridis'
    )
    fig_weights.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font_color='black',
        xaxis_title="时段",
        yaxis_title="成本权重系数"
    )
    st.plotly_chart(fig_weights, use_container_width=True)

with col2:
    # 业务类型成本优化潜力
    business_optimization = df.groupby('business_type').agg({
        'total_cost': 'mean',
        'efficiency_ratio': 'mean'
    }).reset_index()
    business_optimization['optimization_score'] = (1 - business_optimization['efficiency_ratio']) * 100
    
    fig_opt = px.scatter(
        business_optimization,
        x='total_cost',
        y='optimization_score',
        size='efficiency_ratio',
        color='business_type',
        title="业务类型优化潜力分析",
        labels={'optimization_score': '优化潜力(%)', 'total_cost': '平均成本'}
    )
    fig_opt.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font_color='black'
    )
    st.plotly_chart(fig_opt, use_container_width=True)

# 历史趋势分析
st.markdown("---")
st.subheader("📈 历史数据趋势分析与预测")

# 历史数据聚合
daily_stats = historical_df.groupby('date').agg({
    'total_cost': 'sum',
    'business_type': 'count',
    'efficiency_ratio': 'mean',
    'is_anomaly': 'mean'
}).reset_index()
daily_stats.columns = ['date', 'total_cost', 'business_count', 'avg_efficiency', 'anomaly_rate']

col1, col2 = st.columns(2)

with col1:
    # 成本趋势
    fig_trend_cost = px.line(
        daily_stats,
        x='date',
        y='total_cost',
        title="每日总成本趋势",
        markers=True
    )
    fig_trend_cost.update_traces(line_color='#007bff', marker_color='#0056b3')
    fig_trend_cost.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font_color='black'
    )
    st.plotly_chart(fig_trend_cost, use_container_width=True)

with col2:
    # 效率趋势
    fig_trend_eff = px.line(
        daily_stats,
        x='date',
        y='avg_efficiency',
        title="每日平均效率趋势",
        markers=True
    )
    fig_trend_eff.update_traces(line_color='#28a745', marker_color='#1e7e34')
    fig_trend_eff.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font_color='black'
    )
    st.plotly_chart(fig_trend_eff, use_container_width=True)

# 详细数据表格
st.markdown("---")
st.subheader("📋 综合数据分析与异常检测")

# 数据格式化函数
def format_dataframe_for_display(df):
    """格式化数据框用于显示，数值精确到个位数"""
    display_df = df.copy()
    
    # 格式化数值列，精确到个位数
    if 'amount' in display_df.columns:
        display_df['amount'] = display_df['amount'].round(0).astype(int)
    if 'total_cost' in display_df.columns:
        display_df['total_cost'] = display_df['total_cost'].round(0).astype(int)
    if 'distance_km' in display_df.columns:
        display_df['distance_km'] = display_df['distance_km'].round(0).astype(int)
    if 'time_duration' in display_df.columns:
        display_df['time_duration'] = display_df['time_duration'].round(0).astype(int)
    if 'vehicle_cost' in display_df.columns:
        display_df['vehicle_cost'] = display_df['vehicle_cost'].round(0).astype(int)
    if 'labor_cost' in display_df.columns:
        display_df['labor_cost'] = display_df['labor_cost'].round(0).astype(int)
    if 'equipment_cost' in display_df.columns:
        display_df['equipment_cost'] = display_df['equipment_cost'].round(0).astype(int)
    
    return display_df

# 数据分类标签页
tab1, tab2, tab3 = st.tabs(["📊 正常业务数据", "⚠️ 异常业务数据", "🔍 异常特征分析"])

with tab1:
    normal_data = df[df['is_anomaly'] == False]
    st.write(f"正常业务数据 ({len(normal_data)} 条记录)")
    
    # 筛选控制
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_business = st.selectbox("业务类型", ['全部'] + list(df['business_type'].unique()), key="normal_business_select")
    with col2:
        selected_region = st.selectbox("区域", ['全部'] + list(df['region'].unique()), key="normal_region_select")
    with col3:
        selected_scenario = st.selectbox("市场场景", ['全部'] + list(df['market_scenario'].unique()), key="normal_scenario_select")
    
    # 应用筛选
    filtered_normal = normal_data.copy()
    if selected_business != '全部':
        filtered_normal = filtered_normal[filtered_normal['business_type'] == selected_business]
    if selected_region != '全部':
        filtered_normal = filtered_normal[filtered_normal['region'] == selected_region]
    if selected_scenario != '全部':
        filtered_normal = filtered_normal[filtered_normal['market_scenario'] == selected_scenario]
    
    # 显示列定义
    display_columns = ['txn_id', 'business_type', 'region', 'market_scenario', 'amount', 
                      'total_cost', 'efficiency_ratio', 'distance_km', 'time_duration']
    
    # 格式化数据并显示
    formatted_normal = format_dataframe_for_display(filtered_normal[display_columns])
    st.dataframe(formatted_normal.head(20), use_container_width=True)
    
    # 统计信息（格式化到个位数）
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("平均金额", f"¥{filtered_normal['amount'].mean():,.0f}")
    with col_s2:
        st.metric("平均成本", f"¥{filtered_normal['total_cost'].mean():,.0f}")
    with col_s3:
        st.metric("平均距离", f"{filtered_normal['distance_km'].mean():.0f}km")
    with col_s4:
        st.metric("平均时长", f"{filtered_normal['time_duration'].mean():.0f}分钟")

with tab2:
    anomaly_data = df[df['is_anomaly'] == True]
    st.write(f"异常业务数据 ({len(anomaly_data)} 条记录)")
    
    if len(anomaly_data) > 0:
        # 格式化异常数据并显示
        formatted_anomaly = format_dataframe_for_display(anomaly_data[display_columns])
        st.dataframe(formatted_anomaly, use_container_width=True)
        
        # 异常数据统计（格式化到个位数）
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("异常数据平均成本", f"¥{anomaly_data['total_cost'].mean():,.0f}")
        with col2:
            st.metric("异常数据最高成本", f"¥{anomaly_data['total_cost'].max():,.0f}")
        with col3:
            st.metric("异常数据平均距离", f"{anomaly_data['distance_km'].mean():.0f}km")
        with col4:
            st.metric("异常数据平均时长", f"{anomaly_data['time_duration'].mean():.0f}分钟")
    else:
        st.info("当前没有检测到异常数据")

with tab3:
    st.write("### 🔬 异常数据特征分析")
    
    if len(anomaly_data) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # 异常数据成本分布（使用格式化后的数据）
            fig_anomaly_dist = px.histogram(
                anomaly_data,
                x='total_cost',
                title="异常数据成本分布",
                color_discrete_sequence=['#ff6b6b'],
                nbins=20
            )
            fig_anomaly_dist.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                font_color='black',
                xaxis_title="总成本(元)",
                yaxis_title="频次"
            )
            st.plotly_chart(fig_anomaly_dist, use_container_width=True)
        
        with col2:
            # 异常数据业务类型分布
            anomaly_business = anomaly_data['business_type'].value_counts()
            fig_anomaly_business = px.bar(
                x=anomaly_business.index,
                y=anomaly_business.values,
                title="异常数据业务类型分布",
                color_discrete_sequence=['#ff6b6b']
            )
            fig_anomaly_business.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                font_color='black',
                xaxis_title="业务类型",
                yaxis_title="异常数量"
            )
            st.plotly_chart(fig_anomaly_business, use_container_width=True)
        
        # 异常数据关键指标（格式化到个位数）
        st.write("### 📊 异常数据关键指标统计")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("平均时长", f"{anomaly_data['time_duration'].mean():.0f}分钟")
        with col2:
            st.metric("平均距离", f"{anomaly_data['distance_km'].mean():.0f}km")
        with col3:
            st.metric("平均效率比", f"{anomaly_data['efficiency_ratio'].mean():.3f}")
        with col4:
            st.metric("异常率", f"{len(anomaly_data)/len(df)*100:.1f}%")
        
        # 异常数据详细特征分析
        st.write("### 🎯 异常数据成本构成分析")
        
        # 创建异常数据的成本构成分析
        if len(anomaly_data) > 0:
            # 按业务类型分组的异常数据统计
            anomaly_by_type = anomaly_data.groupby('business_type').agg({
                'total_cost': ['mean', 'max', 'count'],
                'distance_km': 'mean',
                'time_duration': 'mean',
                'amount': 'mean'
            }).round(0)
            
            # 扁平化列名
            anomaly_by_type.columns = ['平均成本', '最高成本', '异常数量', '平均距离', '平均时长', '平均金额']
            anomaly_by_type = anomaly_by_type.astype(int)
            
            st.dataframe(anomaly_by_type, use_container_width=True)
        
        # 异常数据的分布特征
        col_dist1, col_dist2 = st.columns(2)
        
        with col_dist1:
            # 异常数据距离分布
            fig_distance_dist = px.box(
                anomaly_data,
                y='distance_km',
                x='business_type',
                title="异常数据距离分布",
                color_discrete_sequence=['#ff6b6b']
            )
            fig_distance_dist.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                font_color='black',
                yaxis_title="距离(km)",
                xaxis_title="业务类型"
            )
            st.plotly_chart(fig_distance_dist, use_container_width=True)
        
        with col_dist2:
            # 异常数据时长分布
            fig_time_dist = px.box(
                anomaly_data,
                y='time_duration',
                x='business_type',
                title="异常数据时长分布",
                color_discrete_sequence=['#ff6b6b']
            )
            fig_time_dist.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                font_color='black',
                yaxis_title="时长(分钟)",
                xaxis_title="业务类型"
            )
            st.plotly_chart(fig_time_dist, use_container_width=True)
    else:
        st.info("当前没有异常数据用于分析")

# 实时更新按钮
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("🔄 数据刷新", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col2:
    if st.button("📈 导出报告", type="secondary", use_container_width=True):
        st.success("📊 报告导出功能开发中...")

with col3:
    if st.button("⚙️ 系统设置", type="secondary", use_container_width=True):
        st.info("🔧 系统设置功能开发中...")

# 页脚信息 - 白底主题
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #495057; border: 1px solid #007bff; border-radius: 10px; background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);'>
    <h4 style='color: #007bff; margin-bottom: 15px;'>🚀 动态成本管理看板系统 v3.0</h4>
    <p><strong style='color: #007bff;'>✨ 核心功能:</strong> 动态可视化监控 | 成本分摊优化 | 市场冲击分析 | 异常检测预警</p>
    <p><strong style='color: #28a745;'>📊 业务覆盖:</strong> 金库运送(50%) | 上门收款(25%) | 现金清点(18.75%) | 金库调拨(6.25%)</p>
    <p><strong style='color: #17a2b8;'>🎯 智能特性:</strong> 7-10天历史分析 | 实时预警系统 | 多维度成本优化 | 异常特征识别</p>
    <p style='color: #6c757d;'>💻 基于 Streamlit + Plotly 构建 | 🔄 实时数据更新 | 📱 响应式设计</p>
</div>
""", unsafe_allow_html=True)

# 自动刷新（可选）
# time.sleep(60)  # 60秒后自动刷新
# st.rerun()
