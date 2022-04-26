
import streamlit as st
from requestpy import craw,load_data,data_pro
import plotly.express as px
import pandas as pd

# ----------网页设置----------
st.set_page_config(page_title="爬虫展示",
                   layout='wide') # 居中显示"centered" or "wide"

# ----------标题----------
st.title('网页爬虫示例APP')

# ----------参数面板----------
st.write('## 请选择参数')
kws = st.selectbox('选择爬取的关键字：👇',['python','数据分析','数据挖掘','人工智能',
                                       '深度学习','Java','数据库','可视化'])

# 设置爬取页数
# nums = st.slider('选择爬取的页数：',min_value=1, max_value=500)
nums = int(st.number_input('输入爬取的页数：'))

# ----------任务控制----------
if st.button('开始爬取'):
    # 爬取数据
    craw(kw=kws, page=nums)
    # 爬虫任务的提示
    col1, col2 = st.beta_columns(2)
    with col1:
        st.success('数据爬取完毕~')

    # 数据展示
    data = load_data(kws)
    with col2:
        st.success('爬取到{}页，{}条数据！'.format(nums, data.shape[0]))

    # 数据处理
    data_info = data_pro(data)
    # 数据分析展示
    raw1_1, raw1_2 = st.beta_columns(2)
    with raw1_1:
        # 热门岗位
        a1 = data_info['岗位名'].value_counts()[:10].reset_index()
        fig1 = px.bar(a1, x='index', y='岗位名',title='热门岗位',
        height = 400, width = 600)
        st.plotly_chart(fig1)
    with raw1_2:
        # 热门行业
        a2 = data_info['行业'].value_counts()[:10].reset_index()
        fig2 = px.pie(a2,names='index',values='行业',title='热门行业',
                      height = 400, width = 600)
        st.plotly_chart(fig2)
    raw2_1, raw2_2 = st.beta_columns(2)
    with raw2_1:
        # 热门城市的招聘分布
        a3 = data_info.groupby('工作地点').agg({'工资水平': 'mean', '公司名': 'count'}).sort_values('公司名', ascending=False).reset_index()
        fig3 = px.pie(a3.head(10),names='工作地点',values='公司名',title='热门地点',
                      height = 400, width = 600)
        st.plotly_chart(fig3)
    with raw2_2:
        # 工资水平分布
        saraly = pd.DataFrame(data_info['工资水平'])
        saraly['id'] = range(0,len(saraly))
        fig4 = px.line(saraly,x='id',y='工资水平',title='薪资分布',
                      height = 400, width = 600)
        st.plotly_chart(fig4)

    with st.beta_expander('是否查看数据？'):
        st.dataframe(data)
        # st.dataframe(data_info)
