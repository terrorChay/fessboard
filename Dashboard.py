import streamlit as st
from streamlit import session_state as session
import utils as utils
from my_query import query_dict
import pandas as pd
import numpy as np
import plotly.express as px
from connectdb import mysql_conn
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go

#Наборы цветов
colors = ['#ED1C24','#F85546','#FF7C68','#FF9E8C','#FFBFB1','#FFDFD7']
colors1 = ['#ED1C24','#F2595F','#C9A0DC','#F0DC82','#FFDAB9','#0ABCFF','#556832']
colors2 = px.colors.qualitative.Dark24
colors3 = ['#ED1C24','#F2595F']
tr='rgba(0,0,0,0)'

font="Source Sans Pro"
config = {'staticPlot': False,'displayModeBar': False}

@st.experimental_memo(ttl=600, show_spinner=False)
def query_data(query):
    with mysql_conn() as conn:
        df = pd.read_sql(query, conn)
    return df

@st.experimental_memo(show_spinner=False)
def load_projects():
    # Load data from database
    projects_df = query_data(query_dict['projects'])
    managers_df = query_data(query_dict['managers_in_projects']).merge(query_data(query_dict['students']), on='ID студента', how='left')
    teachers_df = query_data(query_dict['teachers_in_projects']).merge(query_data(query_dict['teachers']), on='ID преподавателя', how='left')

    # Join multiple managers and teachers into list values
    managers_df = managers_df.groupby(['ID проекта'])['ФИО студента'].apply(list).reset_index()
    teachers_df = teachers_df.groupby(['ID проекта'])['ФИО преподавателя'].apply(list).reset_index()

    # Left join dataframes to create consolidated one
    projects_df = projects_df.merge(managers_df, on='ID проекта', how='left')
    projects_df = projects_df.merge(teachers_df, on='ID проекта', how='left')

    # Set project ID as dataframe index
    projects_df.set_index('ID проекта', drop=True, inplace=True)
    projects_df.rename(columns={'ФИО студента':'Менеджеры', 'ФИО преподавателя':'Преподаватели'}, inplace=True)
    return projects_df

@st.experimental_memo(show_spinner=False)
def load_people_in_projects(teachers=False):
    if teachers:
        a = 'teachers_in_projects'
        b = 'teachers'
        c = 'ID преподавателя'
    else:
        a = 'students_in_projects'
        b = 'students'
        c = 'ID студента'  
    df = query_data(query_dict[a]).merge(query_data(query_dict[b]), on=c, how='left')
    # df.dropna(axis=0, subset=['Команда'], inplace=True)
    df.set_index('ID проекта', drop=True, inplace=True)
    return df

@st.experimental_memo(show_spinner=False)
def load_students():
    return query_data(query_dict['students'])

def main():
    # load data
    with st.spinner('Читаем PMI и PMBOK...'):
        projects_df = load_projects()
    with st.spinner('Происходит аджайл...'):
        students_in_projects_df = load_people_in_projects()
    with st.spinner('Изучаем требования стейкхолдеров...'):
        teachers_in_projects_df = load_people_in_projects(teachers=True)
    with st.spinner('Изучаем требования стейкхолдеров...'):
        students_df = load_students()
    # metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    total = projects_df['Статус'].value_counts().sum() 

    col1.metric('Проектов в работе',
    int(projects_df.loc[projects_df['Статус'] == 'Активен']['Статус'].value_counts().sum()),
    delta=f'{total} завершено',
    delta_color = 'normal')

    col2.metric('Студентов задействовано',  students_df.shape[0])
    col3.metric('Уникальных направлений', projects_df['Направление'].nunique())
    col4.metric('Уникальных партнеров', projects_df['Название компании'].nunique())
    col5.metric('Уникальных направлений', projects_df['Направление'].nunique())
    col6.metric('Уникальных партнеров', projects_df['Название компании'].nunique())

    # row 1
    
    col1, col2,col3,col4,col5 = st.columns([1, 1,1,1,2])
    with col1:
        with st.container():
            st.markdown('**Распределение проектов по вузам-партнёрам**')
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
                textfont_size = 12
                
                )

            fig.update_layout(
                # annotations           = [dict(text=projects_df.shape[0], x=0.5, y=0.5, font_size=40, showarrow=False, font=dict(family=font,color="white"))],
                plot_bgcolor            = tr,
                paper_bgcolor           = tr,
                #legend                 = dict(yanchor="bottom",y=0.1,xanchor="left",x=0.5),
                showlegend              = False,
                font_family             = font,
                title_font_family       = font,
                title_font_color        = "white",
                legend_title_font_color = "white",
                height                  = 150,
                margin                  = dict(t=0, l=0, r=0, b=0),
                #legend=dict(orientation="h",yanchor="bottom",y=-0.4,xanchor="center",x=0,itemwidth=70,bgcolor = 'yellow')
                )

            st.plotly_chart(fig,use_container_width=True,config={'staticPlot': False,'displayModeBar': False})
            # st.plotly_chart(fig,use_container_width=True,config={'staticPlot': False,'displayModeBar': False})
    with col2:
        with st.container():
            st.markdown('**Барчарт по числу проектов в год**')

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
                font_size     = 8,
                paper_bgcolor = tr,
                plot_bgcolor  = tr,
                margin        = dict(t=0, l=0, r=0, b=0),
                yaxis_title     = "",
                xaxis_title     = "",
                width = 10,
                height = 200,
                xaxis_visible   = True,
                )
            
            fig.update_traces(
                textfont_size = 14,
                textangle     = 0,
                textposition  = "inside",
                cliponaxis    = False
                )
            fig['data'][0].width=0.7
            st.plotly_chart(fig,use_container_width=True,config=config)
    with col3:
        with st.container():
            st.markdown('**Динамика вовлеченности потока**')
            options = sorted(students_df.loc[(students_df['Бакалавриат'] == 'ФЭСН РАНХиГС')]['Бак. год'].unique(), reverse=True)
            options = list(map(lambda x: f'{x} - {x+4}', options))
            year = st.selectbox(label='Выберите потоd', options=options, index=0,label_visibility="collapsed")
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
                    # font_size        = 7,
                    height = 100,
                    margin           = dict(t=0, l=0, r=0, b=0),
                    xaxis_visible   = False,
                    )
                
                fig.update_traces(hovertemplate = "<b>%{label}.</b> Вовлечённость: <b>%{value}</b>",cliponaxis    = False)
        
                st.plotly_chart(fig, use_container_width=True,config=config)
    with col4:
        with st.container():
            st.markdown('**Направления проектов**')

            fields_df               = query_data(query_dict['project_fields'])
            fields_df['Количество'] = fields_df['Микро'].map(projects_df['Направление'].value_counts())
            fields_df['Микро']      = fields_df['Микро'].str.replace(' ','<br>')
            fields_df['Макро']      = '<b>'+fields_df['Макро'].astype(str)+'</b>'

            fig = px.sunburst(fields_df,
            path                    = ['Макро', 'Микро'],
            values                  = 'Количество',
            branchvalues            = "total",
            color_discrete_sequence = colors
            )

            fig.update_layout(
                margin        = dict(t=0, l=0, r=0, b=0),
                paper_bgcolor = tr,
                font_family   = font,
                height = 200,
                )
    
            fig.update_traces(
                hovertemplate         = "Направление <b>%{parent}</b><br><b>%{label}.</b> Проектов: <b>%{value}</b>",
                insidetextorientation = 'auto',
                opacity               = 1,
                sort                  = True
                )

            st.plotly_chart(fig, use_container_width=True,config=config)
    
    
    with col5:
        with st.container():
            st.markdown('**Интерактивные рейтинги**')
            rating_subject  = st.selectbox(label='Показывать топ', options=['Преподавателей', 'Студентов'], index=0, label_visibility="collapsed")
            sort_asc = False
            chart_container = st.container()
            display_limit   = st.slider(label='Ограничить вывод', min_value=1, max_value=10, value=3, label_visibility="collapsed")
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
                # font_size       = 13,
                xaxis_visible   = False,
                yaxis_title     = "",
                height          = 100,
                margin          = dict(t=0, b=0,l=0,r=0),
                # title = f'Топ {display_limit} {rating_subject}',
                )
            fig.update_traces(
                textposition  = "inside",)
            fig['data'][0].width=0.4
            # display the plot
            chart_container.plotly_chart(fig, use_container_width=True, config=config)
    col1, col2,col3,col4 = st.columns([1, 2,2,1])
    col1, col2, col3 = st.columns([2, 3, 1])

    with col1:
        with st.container():
            
            frozen = projects_df.loc[projects_df['Статус'] == 'Заморожен']['Статус'].value_counts().sum()
            active = projects_df.loc[projects_df['Статус'] == 'Активен']['Статус'].value_counts().sum()
            total = active + frozen
            st.subheader(f'{active}/{total}')
            df = pd.DataFrame({'names' : ['progress',' '],'values' :  [frozen, total - frozen]})

            fig = px.pie(df, 
            values ='values', 
            names = 'names', 
            hole = 0.8,
            color_discrete_sequence = ['#3DD56D', '#ED1C24']
            )

            fig.update_traces(
                textposition  = 'inside',
                textinfo      = 'percent',
                hovertemplate = "Проектов: <b>%{value}.</b> <br><b>%{percent}</b> от проектов в работе",
                # textfont_size = 18
                
                )

            fig.update_layout(
                plot_bgcolor            = tr,
                paper_bgcolor           = tr,
                showlegend              = False,
                font_family             = font,
                title_font_family       = font,
                title_font_color        = "white",
                legend_title_font_color = "white",
                height                  = 300,
                margin                  = dict(t=0, l=0, r=0, b=0),
                )

            fig.data[0].textfont.color = 'white'
            st.plotly_chart(fig, use_container_width=True,config=config)

                 
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
                margin        = dict(t=0, l=0, r=0, b=0),
                yaxis_title     = "",
                xaxis_title     = "",
                width = 10,
                height = 300
                )
            
            fig.update_traces(
                textfont_size = 18,
                textangle     = 0,
                textposition  = "inside",
                cliponaxis    = False
                )
            fig['data'][0].width=0.7
            st.plotly_chart(fig,use_container_width=True,config=config)


    with col3:
        st.subheader('Пайчарт')
        with st.container():

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
                title_font_family       = font,
                title_font_color        = "white",
                legend_title_font_color = "white",
                height                  = 300,
                margin                  = dict(t=0, l=0, r=0, b=0),
                #legend=dict(orientation="h",yanchor="bottom",y=-0.4,xanchor="center",x=0,itemwidth=70,bgcolor = 'yellow')
                )

            st.plotly_chart(fig,use_container_width=True,config={'staticPlot': False,'displayModeBar': False})
    
    # row 2

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        with st.container():
            st.subheader('Барчарт по числу партнёров по годам')
    with col2:
        with st.container():
            st.subheader('Распределение проектов по типам компаний-заказчиков')
            data = projects_df['Тип компании']
            data1 = projects_df['Отрасль']
            fig = make_subplots(1,2,specs=[[{'type':'domain'}, {'type':'domain'}]],
                    )
            fig.add_trace(go.Pie(values= data.value_counts(),labels= data.value_counts().index, marker_colors=colors),1,1)
            fig.add_trace(go.Pie(values= data1.value_counts(),labels= data1.value_counts().index, marker_colors=colors),1,2)
            fig.update_layout(
                plot_bgcolor            = tr,
                paper_bgcolor           = tr,
                #legend                 = dict(yanchor="bottom",y=0.1,xanchor="left",x=0.5),
                showlegend              = False,
                font_family             = font,
                title_font_family       = font,
                legend_title_font_color = "white",
                height                  = 300,
                font_size     = 18,
                margin                  = dict(t=0, l=0, r=0, b=0),
                #legend=dict(orientation="h",yanchor="bottom",y=-0.4,xanchor="center",x=0,itemwidth=70,bgcolor = 'yellow')
                )
            fig.update_traces(
                textposition  = 'inside',
                textinfo      = 'percent',
                hovertemplate = "Проектов: <b>%{value}.</b> <br><b>%{percent}</b> от проектов в работе",
                textfont_size = 18
                
                )

            st.plotly_chart(fig,use_container_width=True,config={'staticPlot': False,'displayModeBar': False})
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
                
                fig.update_traces(hovertemplate = "<b>%{label}.</b> Вовлечённость: <b>%{value}</b>",cliponaxis    = False)
        
                st.plotly_chart(fig, use_container_width=True,config=config)

    with col3:
        with st.container():
            st.subheader('Доля студентов в активных проектах по курсам')
    
    # row 4

    col1, col2,col3 = st.columns([2,3, 1])
    with col1:
        with st.container():
            st.subheader('Барчарт по числу проектов в год ПО ВЫБРАННОМУ НАПРАВЛЕНИЮ ')
    with col2:
        with st.container():
            st.subheader('Направления проектов')

            fields_df               = query_data(query_dict['project_fields'])
            fields_df['Количество'] = fields_df['Микро'].map(projects_df['Направление'].value_counts())
            fields_df['Микро']      = fields_df['Микро'].str.replace(' ','<br>')
            fields_df['Макро']      = '<b>'+fields_df['Макро'].astype(str)+'</b>'

            fig = px.sunburst(fields_df,
            path                    = ['Макро', 'Микро'],
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

    with col3:
        with st.container():
            st.subheader('Барчарт по числу проектов в год ПО ВЫБРАННОМУ НАПРАВЛЕНИЮ ')
    
    # row 5

    col1, col2 = st.columns([2, 2])
    


if __name__ == "__main__":
    # page setup
    utils.page_config(layout='wide', title='FESSBoard')
    # styles
    utils.remove_footer()
    utils.load_local_css('css/main.css')
    utils.set_logo()
    # main func
    main()