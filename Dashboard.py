import streamlit as st
from streamlit import session_state as session
import utils as utils
from my_query import query_dict
import pandas as pd
import numpy as np
import plotly.express as px
from connectdb import mysql_conn
from datetime import datetime

#Наборы цветов
colors = ['#ED1C24','#F85546','#FF7C68','#FF9E8C','#FFBFB1','#FFDFD7']
colors1 = ['#ED1C24','#F2595F','#C9A0DC','#F0DC82','#FFDAB9','#0ABCFF','#556832']
colors2 = px.colors.qualitative.Dark24
colors3 = ['#ED1C24','#F2595F']
tr='rgba(0,0,0,0)'

font="Source Sans Pro"
config = {'staticPlot': True,'displayModeBar': False}

def main():
    # load data
    with st.spinner('Читаем PMI и PMBOK...'):
        projects_df = utils.load_projects()
    with st.spinner('Происходит аджайл...'):
        students_in_projects_df = utils.load_people_in_projects()
    with st.spinner('Изучаем требования стейкхолдеров...'):
        teachers_in_projects_df = utils.load_people_in_projects(teachers=True)
    with st.spinner('Изучаем требования стейкхолдеров...'):
        students_df = utils.load_students()
    # metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Всего проектов',   projects_df.shape[0])
    col2.metric('Всего студентов',  students_df.shape[0])
    col3.metric('Уникальных направлений', projects_df['Микро-направление'].nunique())
    col4.metric('Уникальных партнеров', projects_df['Название компании'].nunique())
    
    # row 1

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        with st.container():
            st.subheader('Разделение проектов по грейдам')
            a   = projects_df['Грейд']
            
            fig = px.pie(
            a,
            values                  = a.value_counts(),
            names                   = a.value_counts().index,
            color_discrete_sequence = colors,
            hole                    = .4
            )

            fig.update_traces(
                textposition  = 'inside',
                textinfo      = 'label+value',
                hovertemplate = "<b>%{label}.</b> Проектов: <b>%{value}.</b> <br><b>%{percent}</b> от общего количества",
                textfont_size = 18
                )

            fig.update_layout(
                plot_bgcolor            = tr,
                paper_bgcolor           = tr,
                showlegend              = False,
                font_family             = font,
                font_color              = "white",
                title_font_family       = font,
                title_font_color        = "white",
                legend_title_font_color = "white",
                height                  = 300,
                margin                  = dict(t=0, l=0, r=0, b=0)
                )

            st.plotly_chart(fig,use_container_width=True,config=config)

    with col2:
        with st.container():
            st.subheader('Барчарт по числу проектов в год ')

            data    = {'Год': ['2018-2019', '2019-2020', '2020-2021','2021-2022','2022-2023'],'Количество': [16, 24, 37,45,63]}
            test_df = pd.DataFrame(data)

            fig = px.bar(test_df, 
                x                       = 'Год',
                y                       = 'Количество',
                color_discrete_sequence = colors,
                text_auto               = True
                )
            
            fig.update_layout(
                font_family   = font,
                font_size     = 18,
                paper_bgcolor = tr,
                plot_bgcolor  = tr,
                margin        = dict(t=0, l=0, r=20, b=0)
                )
            
            fig.update_traces(
                textfont_size = 18,
                textangle     = 0,
                textposition  = "outside",
                cliponaxis    = False
                )

            st.plotly_chart(fig,use_container_width=True,config=config)


    with col3:

        with st.container():
            st.subheader('Разделение проектов по грейдам')
            a   = projects_df['Грейд']

            fig = px.pie(a,
            values                  = a.value_counts(),
            names                   = a.value_counts().index,
            color_discrete_sequence = colors,
            hole                    = .4
            )

            fig.update_traces(
                textposition  = 'inside',
                textinfo      = 'label+value',
                hovertemplate = "<b>%{label}.</b> Проектов: <b>%{value}.</b> <br><b>%{percent}</b> от общего количества",
                textfont_size = 18
                )

            fig.update_layout(
                # annotations           = [dict(text=projects_df.shape[0], x=0.5, y=0.5, font_size=40, showarrow=False, font=dict(family=font,color="white"))],
                plot_bgcolor            = tr,
                paper_bgcolor           = tr,
                #legend                 = dict(yanchor="bottom",y=0.1,xanchor="left",x=0.5),
                showlegend              = False,
                font_family             = font,
                font_color              = "white",
                title_font_family       = font,
                title_font_color        = "white",
                legend_title_font_color = "white",
                height                  = 300,
                margin                  = dict(t=0, l=0, r=0, b=0)
                )

            st.plotly_chart(fig,use_container_width=True,config=config)
    
    # row 2

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        with st.container():
            st.subheader('Барчарт по числу партнёров по годам')
    with col2:
        with st.container():
            st.subheader('Распределение проектов по типам компаний-заказчиков')
    with col3:
        with st.container():
            st.subheader('Логотипы компаний')
    
    # row 3

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        with st.container():
            st.subheader('Доля вовлеченных студентов')

    with col2:
        with st.container():
            st.subheader('Динамика вовлеченности потока')
            options = sorted(students_df.loc[(students_df['Бакалавриат'] == 'ФЭСН РАНХиГС')]['Бак. год'].unique(), reverse=True)
            options = list(map(lambda x: f'{x} - {x+4}', options))
            year = st.selectbox(label='Выберите поток', options=options, index=0,label_visibility="collapsed")
            year = int(year[:4])
            if year:
                m = students_df.loc[(students_df['Бак. год'] == year) & (students_df['Бакалавриат'] == 'ФЭСН РАНХиГС')]['ID студента'].nunique()
                l = []
                for i in range(0, 4):
                    e = students_in_projects_df.loc[
                            (students_in_projects_df['Бак. год'] == year)
                        &   (students_in_projects_df['Бакалавриат'] == 'ФЭСН РАНХиГС')
                        &   (students_in_projects_df['Дата окончания'].between(datetime.strptime(f'{year+i}-09-01', '%Y-%m-%d').date(), datetime.strptime(f'{year+i+1}-09-01', '%Y-%m-%d').date()))
                        ]['ID студента'].nunique()
                    # e - Кол-во уникальных студентов с потока N, приниваших участие в проектах за 1 курс
                    l.append(e/m)
                data = pd.Series(l, (f'1 курс ({year}-{year+1})',f'2 курс ({year+1}-{year+2})',f'3 курс ({year+2}-{year+3})',f'4 курс ({year+3}-{year+4})'))
                
                fig = px.bar(data,color_discrete_sequence=colors,)
                fig.update_yaxes(range = [0,1])
                
                fig.update_layout(
                    yaxis_tickformat = ".0%",
                    showlegend       = False,
                    xaxis_title      = "Курс",
                    yaxis_title      = "Вовлечённость",
                    font_family      = font,
                    plot_bgcolor     = tr,
                    font_size        = 13,
                    margin           = dict(t=0, l=0, r=0, b=0),
                    )
                
                fig.update_traces(hovertemplate = "<b>%{label}.</b> Вовлечённость: <b>%{value}</b>")
        
                st.plotly_chart(fig, use_container_width=True,config=config)

    with col3:
        with st.container():
            st.subheader('Доля студентов в активных проектах по курсам')
    
    # row 4

    col1, col2 = st.columns([2, 2])
    with col1:
        with st.container():
            st.subheader('Направления проектов')

            # fields_df               = utils.query_data(query_dict['project_fields'])
            # fields_df['Количество'] = fields_df['Микро'].map(projects_df['Микро-направление'].value_counts())
            # fields_df['Микро']      = fields_df['Микро'].str.replace(' ','<br>')
            # fields_df['Макро']      = '<b>'+fields_df['Макро'].astype(str)+'</b>'
            _fields_df = projects_df[['Макро-направление', 'Микро-направление']].copy()
            _fields_count = _fields_df['Микро-направление'].value_counts().reset_index(name='Количество')
            _fields_df = _fields_df.drop_duplicates(subset='Микро-направление')
            _fields_df = _fields_df.merge(_fields_count, left_on='Микро-направление', right_on='index').drop(labels='index', axis=1)
            fig = px.sunburst(_fields_df,
            path                    = ['Макро-направление', 'Микро-направление'],
            values                  = 'Количество',
            branchvalues            = "total",
            color_discrete_sequence = colors
            )

            fig.update_layout(
                margin        = dict(t=0, l=0, r=0, b=0),
                paper_bgcolor = tr,
                font_family   = font
                )
    
            fig.update_traces(
                hovertemplate         = "Направление <b>%{parent}</b><br><b>%{label}.</b> Проектов: <b>%{value}</b>",
                insidetextorientation = 'auto',
                opacity               = 1,
                sort                  = True
                )

            st.plotly_chart(fig, use_container_width=True,config=config)

    with col2:
        with st.container():
            st.subheader('Барчарт по числу проектов в год ПО ВЫБРАННОМУ НАПРАВЛЕНИЮ ')
    
    # row 5

    col1, col2 = st.columns([2, 2])
    with col1:
        with st.container():
            # plot controls
            st.subheader('Интерактивные рейтинги')
            rating_subject  = st.selectbox(label='Показывать топ', options=['Преподавателей', 'Студентов'], index=0, label_visibility="collapsed")
            sort_asc        = st.checkbox('По возрастанию', value=False)
            chart_container = st.container()
            display_limit   = st.slider(label='Ограничить вывод', min_value=1, max_value=15, value=10)
            # data selection
            if rating_subject == 'Преподавателей':
                data = teachers_in_projects_df.value_counts(subset='ФИО преподавателя', ascending=sort_asc).iloc[:display_limit]
            else:
                data = students_in_projects_df.value_counts(subset='ФИО студента', ascending=sort_asc).iloc[:display_limit]
            # set up a plot
            fig = px.bar(data, orientation='h', color_discrete_sequence=colors)
            fig.update_layout(
                yaxis=dict(autorange="reversed"),
                showlegend      = False,
                font_family     = font,
                plot_bgcolor    = tr,
                font_size       = 13,
                xaxis_visible   = False,
                yaxis_title     = "",
                height          = 350,
                margin          = dict(t=0, b=0),
                )
            # display the plot
            chart_container.plotly_chart(fig, use_container_width=True, config=config)
    
    with col2:
        with st.container():
            st.subheader('Распределение проектов по вузам-партнёрам')


if __name__ == "__main__":
    # page setup
    utils.page_config(layout='wide', title='FESSBoard')
    # styles
    utils.remove_footer()
    utils.load_local_css('css/main.css')
    utils.set_logo()
    # main func
    main()