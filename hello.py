import streamlit as st
import ssl
import gspread
from google.oauth2 import service_account
import json
import pandas as pd
import pandas_bokeh
import plotly.express as px

ssl._create_default_https_context = ssl._create_unverified_context


# 上传后台导出的Kadehom店铺数据（用于云端）
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # Can be used wherever a "file-like" object is accepted:
    df_order = pd.read_csv(uploaded_file)
    st.write(df_order.head())

# # 直接加载本地数据（用于开发过程之中）
# Path1 = 'D:/Jupyter/Plotly绘图/原始数据/订单数据.csv'
# df_order = pd.read_csv(Path1)

# 加载谷歌表格中的Kadehome店铺数据
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = service_account.Credentials.from_service_account_info(
                st.secrets["database"], scopes = scope)

gc = gspread.authorize(credentials)
sh = gc.open_by_url(st.secrets["gsheets"])
worksheet1 = sh.worksheet("Sheet1")
df_items = pd.DataFrame(worksheet1.get_all_records())
worksheet2 = sh.worksheet("Sheet2")
df_Statename = pd.DataFrame(worksheet2.get_all_records())

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
             'Ship To State':'state'}
    )
df_useful = df_use.dropna()


### 制作表盘数据  # print('%.2f' %a) ### 为了更细致，应该先剔除Cancelled，再进行分析。有时间的话重新改一下DF的获取方式
df_orderstatus = df_use['订单状态'].value_counts().rename_axis('status').reset_index(name='counts')
df_ordernotcancelled =  df_orderstatus.drop(
    index = df_orderstatus[(df_orderstatus.status == 'Cancelled')].index.tolist()
    ) # 删除Cancelled订单
ordersum = df_ordernotcancelled['counts'].sum()
salesum = df_useful['总销售额'].sum()


### 绘制地图
file = open('data/features.geojson','r',encoding='utf-8')
counties = json.load(file)
df_State = df_useful.state.value_counts().rename_axis('state').reset_index(name='counts')
df_State_useful = pd.merge(df_State, df_Statename, on="state", how="left")
px.set_mapbox_access_token(token=st.secrets["token"])
fig_map = px.choropleth_mapbox(df_State_useful, geojson=counties, locations='statename', color='counts',
                           color_continuous_scale="Viridis",
                           range_color=(0, 200),
                           mapbox_style="streets",
                           zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                           opacity=0.5,
                          )
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})



### 绘制折线图
pandas_bokeh.output_notebook()
df_line = df_use.groupby(['订单时间'],as_index=False)['总销售额'].sum()
fig_line = df_line.plot_bokeh.line(
    title="销售情况",
    x = '订单时间',
    y = '总销售额',
    xlabel="Date",
    ylabel="price [$]",
    yticks=[0, 5000],
    ylim=(0, 5000),
    colormap=["blue"],
    rangetool=True,
    marker="asterisk")

### 绘制商品图
fig_item = px.treemap(df_useful, path=[px.Constant("总计"),'分类', '供应商编码','唯非SKU'], values='总销售额',
                  color='总销售额', hover_data=['总销售额'],
                  color_continuous_scale='RdBu',
                  color_continuous_midpoint=2)
fig_item.update_layout(margin = dict(t=50, l=25, r=25, b=25))


### 开始页面布局




###仪表盘部分
col1, col2, col3 = st.columns(3)
col1.metric("销售金额", '%.2f' %salesum)
col2.metric("订单数量", ordersum)
# col3.metric("TOP5SKU", "86%", "4%")

###销售地图部分
st.plotly_chart(fig_map)


###折线图部分
st.bokeh_chart(fig_line)

###商品细分展示部分
st.plotly_chart(fig_item)










###带复选的折线图等
