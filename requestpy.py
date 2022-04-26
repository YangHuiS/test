
import requests

import os
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
import re


@st.cache
def craw(kw='python', page=3):
    # if os.path.exists('job_info.csv'):
    #     os.remove('job_info.csv')
    # print('本地文件已删除')
    # 伪装浏览器
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'}
    for i in range(1,page+1):
        print('正在爬取第{}页'.format(i))
        url ='https://search.51job.com/list/000000,000000,0000,00,9,99,{},2,{}.html'.format(kw,i)
        res = requests.get(url, headers=headers)
        text = re.sub(r'\\','',res.text)
        # 岗位名
        job_name = re.findall('job_name":"(.{1,100})","job_title', text)
        # 公司名
        company_name = re.findall('company_name":"(.{1,100})","providesalary_text', text)
        # 工作地点
        address = re.findall('workarea_text":"(.{1,100})","updatedate', text)
        # 工资待遇
        saraly = re.findall('providesalary_text":"(.{1,20})","workarea', text)
        # 发布时间
        release_time = re.findall('updatedate":"(.{1,30})","iscommunicate', text)
        # 网址明细
        href =  re.findall('job_href":"(.{1,300})","job_name', text)
        # 福利待遇
        jobdes = re.findall('jobwelf":"(.{0,200})","jobwelf_list', text)
        # 福利待遇，公司类型，公司人数规模，所属行业
        # 公司类型
        company_type = re.findall('companytype_text":"(.{0,50})","degreefrom', text)
        # 规模
        number_staff = re.findall('companysize_text":"(.{0,50})","companyind_text', text)
        # 所属行业
        industry = re.findall('companyind_text":"(.{0,50})","adid', text)
        # 整理成表格
        data = pd.DataFrame({'岗位名':job_name,
                     '公司名':company_name,
                      '工作地点':address,
                      '工资待遇':saraly,
                      '发布时间':release_time,
                      '福利待遇':jobdes,
                      '公司类型':company_type,
                      '人数':number_staff,
                      '所属行业':industry,
                      '关键字':kw
                     })
        data.to_csv('job_info_new.csv', header=None, mode='a+',index=None,encoding='gbk')
    print('爬取完毕~')

# 数据读取
# @st.cache
def load_data(cla):
    datas = pd.read_csv('job_info_new.csv', header=None, encoding='GBK')
    datas = datas.drop_duplicates()
    datas.index = range(len(datas))
    datas.columns = ['岗位名', '公司名', '工作地点', '工资', '发布日期', '福利待遇', '公司类型', '公司规模', '行业', '关键字']
    data_seletct = datas.loc[datas['关键字']==cla,:]
    return data_seletct


def data_pro(data):

    '''
    ====================================================================================================
    岗位名数据处理
    =====================================================================================================
    '''
    # 1、岗位名探索
    data['岗位名'] = data['岗位名'].str.strip().astype(str).apply(lambda x: x.lower())
    data['岗位名'].value_counts()
    # 2、岗位太多太杂，我们需要筛选出待分析岗位数据
    target_job = ['算法', '分析', '工程师', '开发', '数据', '运营', '运维']    # 目标岗位
    index = [data['岗位名'].str.count(i) for i in target_job]
    index = np.array(index).sum(axis=0) > 0
    job_info = data[index]


    # 3、将岗位名称标准化：目前岗位名称太多太杂，需要统一
    job_list = ['数据分析', '数据挖掘', '算法', '大数据',
                '开发工程师', '运营', '软件工程', '前端开发',
                '深度学习', 'AI', '数据库', '数据库', '数据产品',
                '客服', 'java', '.net', 'andrio', '人工智能', 'c++',
                '数据管理']

    job_list = np.array(job_list)


    def rename(x=None, name_list=job_list):
        index = [i in x for i in name_list]
        if sum(index) > 0:
            return name_list[index][0]
        else:
            return x


    job_info['岗位名'] = job_info['岗位名'].apply(rename)

    '''
    ====================================================================================================
    工资数据处理
    目前工资是一个范围（如1.5-2.5万/月），现需取出每个岗位的最低工资与最高工资，单位为“元/月”
    若招聘信息中无工资数据则无需处理。（如2-2.5万/月，则最低工资为20000，最高工资为25000。）
    =====================================================================================================
    '''
    index1 = job_info['工资'].str[-1].apply(lambda x: x in ['年', '月'])
    index2 = job_info['工资'].str[-3].apply(lambda x: x in ['万', '千'])
    job_info = job_info[index1 & index2]


    def get_max_min(x=None):
        try:
            if x[-3] == '万':
                a = [float(i)*10000 for i in re.findall('\d+\.?\d*', x)]
            elif x[-3] == '千':
                a = [float(i)*1000 for i in re.findall('\d+\.?\d*', x)]
            if x[-1] == '年':
                a = [i/12 for i in a]
            return a
        except:
            return x


    salary = job_info['工资'].apply(get_max_min)
    job_info['最低工资'] = salary.str[0]
    job_info['最高工资'] = salary.str[1]
    job_info['工资水平'] = job_info[['最低工资', '最高工资']].mean(axis=1)

    '''
    ====================================================================================================
    工作地点处理
    =====================================================================================================
    '''

    # 1、工作地点统一命名
    address_list = ['北京', '上海', '广州', '深圳', '杭州', '苏州', '长沙',
                    '武汉', '天津', '成都', '西安', '东莞', '合肥', '佛山',
                    '宁波', '南京', '重庆', '长春', '郑州', '常州', '福州',
                    '沈阳', '济南', '宁波', '厦门', '贵州', '珠海', '青岛',
                    '无锡', '大连']
    address_list = np.array(address_list)


    def rename(x=None, name_list=address_list):
        index = [i in x for i in name_list]
        if sum(index) > 0:
            return name_list[index][0]
        else:
            return x


    job_info['工作地点'] = job_info['工作地点'].apply(rename)


    '''
    ====================================================================================================
    公司人数进行处理
    =====================================================================================================
    '''

    def get_number_staff(x=None):
        try:
            a = [int(i) for i in re.findall('\d+', x)]
            if len(a) == 1:
                n = a[0]
            elif len(a) == 2:
                n = np.mean(a)
            return n
        except:
            return np.nan


    job_info['公司规模'] = job_info['公司规模'].apply(get_number_staff)

    '''
    ===============
    构造新数据
    ===============
    '''
    features = ['岗位名', '公司名', '工作地点', '公司类型', '公司规模', '行业', '工资水平', '发布日期', '福利待遇','关键字']
    data_new = job_info[features]   # 清洗干净后的数据
    data_new.to_csv('job_info_new1.csv', encoding='GBK', index=None)

    return data_new

