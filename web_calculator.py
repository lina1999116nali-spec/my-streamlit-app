
import streamlit as st
import pandas as pd
import numpy_financial as npf
from io import BytesIO

st.set_page_config(
    page_title="智算中心融资测算平台",
    layout="wide"
)

st.title("🚀 智算中心融资测算平台 V5.0")

st.header("基础参数")

b300_num = st.number_input("B300数量", value=1024)
b300_rent = st.number_input("B300单卡月租金（元）", value=22500)
h200_num = st.number_input("H200数量", value=2048)
h200_rent = st.number_input("H200单卡月租金（元）", value=12000)

st.header("融资及财务参数")

total_investment = st.number_input("总投资（亿元）", value=20.0)
loan_amount = st.number_input("融资金额（亿元）", value=20.0)
interest_rate = st.slider("融资利率", 0.00, 0.15, 0.04)
depreciation_years = st.number_input("折旧年限", value=5)
tax_rate = st.slider("所得税率", 0.00, 0.50, 0.25)
opex_rate = st.slider("运营成本率", 0.00, 0.50, 0.16)
residual_rate = st.slider("第五年残值率", 0.00, 0.80, 0.40)

st.header("三档情景假设")

conservative = st.slider("保守出租率", 0.00, 1.00, 0.75)
base = st.slider("中性出租率", 0.00, 1.00, 0.85)
optimistic = st.slider("乐观出租率", 0.00, 1.00, 0.95)

scenarios = {
    "保守情景": conservative,
    "中性情景": base,
    "乐观情景": optimistic
}

results = []
cashflow_data = []

for name, occupancy in scenarios.items():
    b300_income = b300_num * b300_rent * 12 * occupancy / 100000000
    h200_income = h200_num * h200_rent * 12 * occupancy / 100000000
    total_income = b300_income + h200_income

    opex = total_income * opex_rate
    ebitda = total_income - opex

    depreciation = total_investment / depreciation_years
    interest = loan_amount * interest_rate

    profit_before_tax = ebitda - depreciation - interest

    if profit_before_tax > 0:
        income_tax = profit_before_tax * tax_rate
    else:
        income_tax = 0

    net_profit = profit_before_tax - income_tax
    operating_cashflow = net_profit + depreciation

    year_5_cashflow = operating_cashflow + total_investment * residual_rate

    cashflows = [
        -total_investment,
        operating_cashflow,
        operating_cashflow,
        operating_cashflow,
        operating_cashflow,
        year_5_cashflow
    ]

    irr = npf.irr(cashflows)

    if operating_cashflow > 0:
        payback_period = total_investment / operating_cashflow
    else:
        payback_period = None

    results.append({
        "情景": name,
        "出租率": f"{occupancy:.0%}",
        "总收入(亿元)": round(total_income, 2),
        "EBITDA(亿元)": round(ebitda, 2),
        "税前利润(亿元)": round(profit_before_tax, 2),
        "税后净利润(亿元)": round(net_profit, 2),
        "经营现金流(亿元)": round(operating_cashflow, 2),
        "项目IRR": f"{irr:.2%}",
        "投资回收期(年)": round(payback_period, 2) if payback_period else "无法回收"
    })

    for year in range(1, 6):
        if year == 5:
            cashflow = year_5_cashflow
        else:
            cashflow = operating_cashflow

        cashflow_data.append({
            "年份": f"第{year}年",
            "情景": name,
            "现金流(亿元)": round(cashflow, 2)
        })

result_df = pd.DataFrame(results)
cashflow_df = pd.DataFrame(cashflow_data)

st.header("📊 三档情景测算结果")
st.dataframe(result_df, width="stretch")

st.header("核心指标")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("中性情景总收入", f"{result_df.loc[1, '总收入(亿元)']}亿元")

with col2:
    st.metric("中性情景EBITDA", f"{result_df.loc[1, 'EBITDA(亿元)']}亿元")

with col3:
    st.metric("中性情景IRR", result_df.loc[1, "项目IRR"])

st.header("📈 图表分析")

st.subheader("收入对比")
st.bar_chart(result_df.set_index("情景")["总收入(亿元)"])

st.subheader("EBITDA对比")
st.bar_chart(result_df.set_index("情景")["EBITDA(亿元)"])

st.subheader("税后净利润对比")
st.bar_chart(result_df.set_index("情景")["税后净利润(亿元)"])

st.header("📈 5年现金流趋势分析")
st.dataframe(cashflow_df, width="stretch")

cashflow_pivot = cashflow_df.pivot(
    index="年份",
    columns="情景",
    values="现金流(亿元)"
)

st.line_chart(cashflow_pivot)

st.header("📊 出租率敏感性分析")

sensitivity_data = []

for occ in [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
    b300_income = b300_num * b300_rent * 12 * occ / 100000000
    h200_income = h200_num * h200_rent * 12 * occ / 100000000
    total_income = b300_income + h200_income

    opex = total_income * opex_rate
    ebitda = total_income - opex

    depreciation = total_investment / depreciation_years
    interest = loan_amount * interest_rate

    profit_before_tax = ebitda - depreciation - interest

    if profit_before_tax > 0:
        income_tax = profit_before_tax * tax_rate
    else:
        income_tax = 0

    net_profit = profit_before_tax - income_tax

    sensitivity_data.append({
        "出租率": f"{occ:.0%}",
        "总收入(亿元)": round(total_income, 2),
        "EBITDA(亿元)": round(ebitda, 2),
        "税后净利润(亿元)": round(net_profit, 2)
    })

sensitivity_df = pd.DataFrame(sensitivity_data)

st.dataframe(sensitivity_df, width="stretch")

st.subheader("出租率-EBITDA敏感性图")
st.line_chart(
    sensitivity_df.set_index("出租率")["EBITDA(亿元)"]
)

st.subheader("出租率-税后净利润敏感性图")
st.line_chart(
    sensitivity_df.set_index("出租率")["税后净利润(亿元)"]
)

st.header("📥 导出结果")

excel_buffer = BytesIO()

with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    result_df.to_excel(writer, index=False, sheet_name="三档情景测算")
    cashflow_df.to_excel(writer, index=False, sheet_name="5年现金流")
    sensitivity_df.to_excel(writer, index=False, sheet_name="出租率敏感性")

excel_data = excel_buffer.getvalue()

st.download_button(
    label="📥 下载Excel测算表",
    data=excel_data,
    file_name="智算中心融资测算结果.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
