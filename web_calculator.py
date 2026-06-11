import streamlit as st
import pandas as pd
import numpy_financial as npf

st.set_page_config(page_title="智算中心融资测算平台", layout="wide")
st.title("🚀 智算中心融资测算平台 V3.0")

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

result_df = pd.DataFrame(results)

st.header("📊 三档情景测算结果")
st.dataframe(result_df, use_container_width=True)

st.header("核心指标对比")

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

st.header("导出结果")

if st.button("生成Excel测算表"):
    output_path = "智算中心三档情景测算结果.xlsx"
    result_df.to_excel(output_path, index=False)
    st.success("Excel测算表已生成，请在本地文件夹中查看。")