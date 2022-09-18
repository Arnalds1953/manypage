import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

### 文件路径H:/Python/GitHub/manypage/data/订单数据.csv
Path1 = 'H:/Python/GitHub/manypage/data/订单数据.csv'
Path2 = 'H:/Python/GitHub/manypage/data/Kadehome商品总表.xlsx'

### 读取店铺数据到Dataframe
df_order = pd.read_csv(Path1)
df_items = pd.read_excel(Path2)

### 合并处理数据，并转换时间序列
df_merge = pd.merge(df_order, df_items, on="Item Number", how="left")
df_merge['总销售额'] = df_merge['Quantity']*df_merge['Wholesale Price']
df_merge['订单时间'] = pd.to_datetime(df_merge['PO Date'],format='%m/%d/%Y')

### 导出标准化Dataframe
df_sel = df_merge[
    ['PO Number', '订单时间', 'Order Status','分类','Item Number', '唯非SKU','供应商SKU','供应商编码','Wholesale Price',
     'Quantity','总销售额', 'Ship To State']
    ] 
df_use = df_sel.rename(
    columns={'PO Number':'订单号',
             'Order Status':'订单状态',
             'Item Number':'平台SKU',
             'Wholesale Price':'销售价格',
             'Quantity':'销售数量',
             'Ship To State':'销售地区'}
    )
df_useful = df_use.dropna()
st.write(df_useful)

df_State1 = df_use.销售地区.value_counts().rename_axis('state').reset_index(name='counts')
fig1 = go.Figure(data=go.Choropleth(
    locations=df_State1['state'], # Spatial coordinates
    z = df_State1['counts'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "订单数量",
))

fig1.update_layout(
    title_text = '订单数量分布图',
    geo_scope='usa', # limite map scope to USA
)
# df_selection.groupby(["平台SKU"],as_index=False)["总销售额"].sum()
# df_State = df_use.销售地区.value_counts().rename_axis('state').reset_index(name='counts')

df_State2 = df_useful.groupby(["销售地区"],as_index=False)["总销售额"].sum()
fig2 = go.Figure(data=go.Choropleth(
    locations=df_State2['销售地区'], # Spatial coordinates
    z = df_State2['总销售额'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "销售金额",
))

fig2.update_layout(
    title_text = '销售金额分布图',
    geo_scope='usa', # limite map scope to USA
)
### 开始布局
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("A")
    st.write(df_State1.head())
with col2:
    st.subheader("A")
    st.write(df_State2.head())

with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("这是第一个")
        st.plotly_chart(fig1)
    with col2:
        tab1, tab2 = st.tabs(["订单数量", "销售金额"])
        with tab1:
            st.subheader("订单数量")
            st.plotly_chart(fig1)
        with tab2:    
            st.subheader("销售金额")
            st.plotly_chart(fig2)
    with col3:
        st.subheader("这是第三个")
        st.plotly_chart(fig1)
        







