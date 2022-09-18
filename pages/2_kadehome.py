import streamlit as st
import pandas as pd
import numpy as np
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

df_State = df_use.销售地区.value_counts().rename_axis('state').reset_index(name='counts')
fig1 = go.Figure(data=go.Choropleth(
    locations=df_State['state'], # Spatial coordinates
    z = df_State['counts'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "订单数量",
))

fig1.update_layout(
    title_text = '订单数量分布图',
    geo_scope='usa', # limite map scope to USA
)

fig2 = px.treemap(df_useful, path=[px.Constant("总计"),'分类', '供应商编码','唯非SKU'], values='总销售额',
                  color='总销售额', hover_data=['总销售额'],
                  color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(df_useful['总销售额'], weights=df_useful['销售数量']))
fig2.update_layout(margin = dict(t=50, l=25, r=25, b=25))

df1 = df_use.groupby(['订单时间'],as_index=False)['总销售额'].sum()
df1.head()
fig3 = px.line(df1, x="订单时间", y="总销售额", title='销售情况')

st.plotly_chart(fig1)
st.plotly_chart(fig2)
st.plotly_chart(fig3)
