import streamlit as st
from streamlit import session_state as session
import utils as utils
import pandas as pd
import numpy as np
from datetime import date
import plotly.express as px
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go

#Наборы цветов
colors0 = ['#FF7C68','#FF9E8C','#FFBFB1','#FFDFD7','#F85546','#ED1C24',]
colors1 = ['#ED1C24','#F2595F','#C9A0DC','#F0DC82','#FFDAB9','#0ABCFF','#556832']
colors2 = px.colors.qualitative.Light24
colors3 = ['#ED1C24','#F2595F']
colors4 = ['#3A42FF','#FB832A','#D0455E','#82CD97','#45B0D0','#7A45D0','#88B1FF','#2227A7']
colors40 = ['#3A42FF','#45B0D0','#7A45D0','#88B1FF','#2227A7','#FB832A','#D0455E','#82CD97']
colors5 = ['#ED1C24','#F7A3A6']
test = ['#5E60CE','#5390D9','#4EA8DE','#48BFE3','#56CFE1','#64DFDF','#72EFDD','#80FFDB','#7400B8','#6930C3',]
colors6 = ['#FF5744','#F2595F','#C9A0DC','#F0DC82','#FFDAB9','#0ABCFF','#556832']

tr='rgba(0,0,0,0)'
colors = colors0
marker = colors[5]


font="Source Sans Pro"
config = {'staticPlot': False,'displayModeBar': False}

def main():
    # load data
    with st.spinner('Читаем PMI и PMBOK...'):
        projects_df             = utils.load_projects()
    with st.spinner('Происходит аджайл...'):
        students_in_projects_df = utils.load_students_in_projects()
    with st.spinner('Изучаем требования стейкхолдеров...'):
        teachers_in_projects_df = utils.load_teachers_in_projects()
    with st.spinner('Еще чуть-чуть и прямо в рай...'):
        students_df             = utils.load_students()
    with st.spinner('Нежно обращаемся к базе данных...'):
        universities_df         = utils.load_universities()
    with st.spinner('Собираем встречу выпускников...'):
        events_df               = utils.load_events()
    with st.spinner('Советуемся с ChatGPT...'):
        students_in_events_df   = utils.load_students_in_events()
    # Ряд метрик
    with st.container():
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        # Проекты в работы ( активно vs. завершено )
        col1.metric(
            label       = 'Проектов в работе',
            value       = projects_df[projects_df['Статус'] == 'Активен'].shape[0],
            delta       = '{} за все время'.format(projects_df[projects_df['Статус'] == 'Завершен'].shape[0]),
            delta_color = 'normal')
        # Уникальных студентов ( активно vs. побывало )
        col2.metric(
            label       = 'Студентов задействовано',
            value       = students_in_projects_df['ID студента'].loc[students_in_projects_df['Статус'] == 'Активен'].nunique(),
            delta       = '{} за все время'.format(students_in_projects_df['ID студента'].nunique()),
            delta_color = 'normal')
        # Компаний партнеров ( всего vs. отрасли )
        ## Новых компаний в этом году:
        ## projects_df[['Дата начала','Название компании']].sort_values('Дата начала').drop_duplicates(subset='Название компании', keep='first').loc[projects_df['Дата начала'] >= date(date.today().year, 1, 1)].shape[0]
        col3.metric(
            label       = 'Компаний-партнёров', 
            value       = projects_df['Название компании'].nunique(),
            delta       = 'из {} отраслей(-и)'.format(projects_df['Отрасль'].nunique()),
            delta_color = 'normal')
        # Университетов партнеров ( количество, регионы )
        col4.metric(
            label       = 'Университетов-партнёров',
            value       = universities_df.shape[0],
            delta       = 'из {} регионов(-а)'.format(universities_df['Регион'].nunique()),
            delta_color = 'normal')
        # Направления и сферы
        col5.metric(
            label       = 'Уникальных направлений',
            value       = projects_df['Микро-направление'].nunique(),
            delta       = 'из {} сфер(-ы)'.format(projects_df['Макро-направление'].nunique()),
            delta_color = 'normal')
        # Мероприятия
        col6.metric(
            label       = 'Мероприятий проведено',
            value       = events_df.shape[0],
            delta       = '{} участников(-а)'.format(students_in_events_df.shape[0]),
            delta_color = 'normal')
    # Ряд графиков о проектах
    col1, col2,col3,col5 = st.columns([1, 2,2,1])
    with col1:
        ## Распределение грейдов
        with st.container():
            st.markdown('<p class="tooltip"><strong>Грейды проектов</strong><span class="tooltiptext">Показывает чудеса грейдного членения</span></p>', unsafe_allow_html=True)
            a   = projects_df['Грейд']

            fig = px.pie(a,
            values                  = a.value_counts(),
            names                   = a.value_counts().index,
            color_discrete_sequence = colors,
            hole                    = .4
            )

            fig.update_traces(
                textposition  = 'inside',
                textinfo      = 'label',
                hovertemplate = "<b>%{label}.</b> Проектов: <b>%{value}.</b> <br><b>%{percent}</b> от общего количества",
                textfont_size = 14
                
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
                height                  = 220,
                margin                  = dict(t=0, l=0, r=0, b=0),
                #legend=dict(orientation="h",yanchor="bottom",y=-0.4,xanchor="center",x=0,itemwidth=70,bgcolor = 'yellow')
                )

            st.plotly_chart(fig,use_container_width=True,config={'staticPlot': False,'displayModeBar': False})
    with col2:
        ## Число и темп прироста проектов
        with st.container():
            st.markdown('**Число и темп прироста проектов**')
            df = projects_df[['Академический год']].copy()
            df.dropna(inplace=True)
            df = df.sort_values('Академический год').value_counts(sort=False).reset_index(name='Количество')
            df['Темп прироста'] = df['Количество'].pct_change().fillna(0)
            test_df = df.iloc[-5:]

            # Figure with two Y axes
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # bar plot (secondary_y = False)
            fig.add_trace(go.Bar(
                    x                   = test_df['Академический год'],
                    y                   = test_df['Количество'],
                    width               = 0.7,
                    name                = 'Проектов',
                    marker_color        = marker,
                    opacity             = 1,
                    marker_line_width   = 2,
                    text                = list(test_df['Количество']),
                    ),
                secondary_y = False)
            fig.update_layout(
                 font_family    = font,
                 font_size      = 13,
                 paper_bgcolor  = tr,
                 plot_bgcolor   = tr,
                 margin         = dict(t=0, l=0, r=0, b=0),
                 yaxis_title    = "",
                 xaxis_title    = "",
                 width          = 10,
                 height         = 220,
                 xaxis_visible  = True,
                 yaxis_visible  = True,
                 xaxis          = dict(showgrid=False), 
                 yaxis          = dict(showgrid=False),
                 showlegend     = False
                 )
            fig.update_traces(
                textfont_size   = 14,
                 textangle      = 0,
                 textposition   = "auto",
                 cliponaxis     = False,
                 )
            # fig['data'][0].width=0.7
            # scatter plot (secondary_y = True)
            fig.add_trace(go.Scatter(
                    x       = test_df['Академический год'],
                    y       = test_df['Темп прироста'],
                    line    = dict(color='#07C607'),
                    name    = 'Темп прироста',
                    ),
                secondary_y = True)
            fig.update_yaxes(
                hoverformat = ',.0%',
                tickformat  = ',.0%',
                secondary_y = True
            )

            st.plotly_chart(fig,use_container_width=True,config=config)
    with col3:
        ## Число проектных групп в год
        with st.container():
            st.markdown('**Число проектных групп в год**')  
            data    = {'Год': ['2018-2019', '2019-2020', '2020-2021','2021-2022','2022-2023'],'Количество': [17, 28, 42,50,70],'Прирост':
            [17,11,14,8,20]}
            test_df = pd.DataFrame(data)
            fig = make_subplots(1,1)

# add first bar trace at row = 1, col = 1
            fig.add_trace(go.Bar(x=test_df['Год'], y=test_df['Количество'],
                     name='Групп',
                     marker_color = marker,
                     opacity=1,
                     marker_line_width=2,
                     text=list(test_df['Количество']),
                     hovertext= ''
                     
),
              row = 1, col = 1)
            fig.update_layout(
                 font_family   = font,
                 font_size     = 13,
                 paper_bgcolor = tr,
                 plot_bgcolor  = tr,
                 margin        = dict(t=0, l=0, r=0, b=0),
                 yaxis_title     = "",
                 xaxis_title     = "",
                 width = 10,
                 height = 220,
                 xaxis_visible   = True,
                 yaxis_visible   = True,
                 xaxis=dict(showgrid=False), 
                 yaxis=dict(showgrid=False),
                 showlegend       = False,
                 
                 )
            fig.update_traces(
                textfont_size = 14,
                 textangle     = 0,
                 textposition  = "inside",
                 cliponaxis    = False,
                 )
            fig['data'][0].width=0.7
# add first scatter trace at row = 1, col = 1
            fig.add_trace(go.Scatter(x=test_df['Год'], y=test_df['Прирост'], line=dict(color='#07C607'), name='Прирост'),
              row = 1, col = 1)
            st.plotly_chart(fig,use_container_width=True,config=config)
    with col5:
        ## Регионы мероприятий
        with st.container():
            st.markdown('**Регионы мероприятий**')
            data    = {'Регион': ['Москва', 'Нижний Новгород', 'Казань','Калининград','Сарапул'],'Количество': [10, 3, 1,3,1]}
            events_regions_df = pd.DataFrame(data)

            fig = px.pie(events_regions_df,
            values                  = events_regions_df['Количество'],
            names                   = events_regions_df['Регион'],
            color_discrete_sequence = colors,
            hole                    = .4
            )

            fig.update_traces(
                textposition  = 'inside',
                textinfo      = 'label',
                hovertemplate = "<b>%{label}.</b> Мероприятий: <b>%{value}.</b> <br><b>%{percent}</b> от общего количества",
                textfont_size = 14
                
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
                height                  = 220,
                margin                  = dict(t=0, l=0, r=0, b=0),
                #legend=dict(orientation="h",yanchor="bottom",y=-0.4,xanchor="center",x=0,itemwidth=70,bgcolor = 'yellow')
                )

            st.plotly_chart(fig,use_container_width=True,config={'staticPlot': False,'displayModeBar': False})
    # Ряд логотипов
    col1, col2,col3,col4,col5,col6 = st.columns([1,1,1,1,1,1])
    with col1:
        with st.container():
            st.image(
                image = 'https://github.com/terrorChay/FESSBoard/blob/master/img/sber_logo.png?raw=true',
                use_column_width = 'auto',
            )
    with col2:
        with st.container():
            st.image(
                image = 'https://github.com/terrorChay/FESSBoard/blob/master/img/mik_logo.png?raw=true',
                use_column_width = 'auto',
            )
    with col3:
        with st.container():
            st.image(
                image = 'https://github.com/terrorChay/FESSBoard/blob/master/img/segezha_logo.png?raw=true',
                use_column_width = 'auto',
            )
    with col4:
        with st.container():
            st.image(
                image = 'https://github.com/terrorChay/FESSBoard/blob/master/img/schneider_logo.png?raw=true',
                use_column_width = 'auto',
            )
    with col5:
        with st.container():
            st.image(
                image = 'https://github.com/terrorChay/FESSBoard/blob/master/img/xiaomi_logo.png?raw=true',
                use_column_width = 'auto',
            )
    with col6:
        with st.container():
            st.image(
                image = 'https://github.com/terrorChay/FESSBoard/blob/master/img/bosch_logo.png?raw=true',
                use_column_width = 'auto',
            )
    # # Ряд Компаний-парнёров      
    col1, col2,col3,col4 = st.columns([1, 2,2,1])
    with col1:
        with st.container():
            st.markdown('**Количество повторных обращений (топ заказчиков)**')
    with col2:
        with st.container():
            st.markdown('**Рост количества компаний-партнёров (накопительным итогом)**')
              
            
    with col3:
        with st.container():
            st.markdown('**Проекты по типу компании-заказчика**')
            data = projects_df['Тип компании']

            fig = px.pie(data,
            values                  = data.value_counts(),
            names                   = data.value_counts().index,
            color_discrete_sequence = colors,
            hole                    = .4
            )

            fig.update_traces(
                textposition  = 'inside',
                textinfo      = 'percent',
                hovertemplate = "<b>%{label}.</b> Проектов: <b>%{value}.</b> <br><b>%{percent}</b> от общего количества",
                textfont_size = 14
                
                )

            fig.update_layout(
                # annotations           = [dict(text=projects_df.shape[0], x=0.5, y=0.5, font_size=40, showarrow=False, font=dict(family=font,color="white"))],
                plot_bgcolor            = tr,
                paper_bgcolor           = tr,
                legend                  = dict(orientation="v",itemwidth=30,yanchor="top", y=0.7,xanchor="left",x=1),
                showlegend              = True,
                font_family             = font,
                title_font_family       = font,
                title_font_color        = "white",
                legend_title_font_color = "white",
                height                  = 220,
                margin                  = dict(t=0, l=0, r=200, b=0),
                #legend=dict(orientation="h",yanchor="bottom",y=-0.4,xanchor="center",x=0,itemwidth=70,bgcolor = 'yellow')
                )

            st.plotly_chart(fig,use_container_width=True,config={'staticPlot': False,'displayModeBar': False}) 
    with col4:
        with st.container():
            st.markdown('**Международных компаний**')
            st.metric(
            label       = 'Проектов в работе',
            value       = int(projects_df.loc[projects_df['Статус'] == 'Активен']['Статус'].value_counts().sum()))
            st.markdown('**российских компаний**')
            st.metric(
            label       = 'Проектов в работе',
            value       = 10)
    
#     with col5:
#         with st.container():
#             st.markdown('**Наши партнёры**')  
#             st.image(
#                 image = r'img\sber_logo.png',
#                 use_column_width = 'auto',
#             )
#             st.write('СБЕР Агентство Инноваций Москвы (Московский инновационный кластер) BMW (?)\nBOSCH\
# Segezha Xiaomi Schneider Студия имени горького')
    
    # Ряд студентов
    col1, col2,col3,col4,col5 = st.columns([1, 2,1,1,1])
    with col1:
        with st.container():
            st.markdown('**Участников в проектах**')

            data    = {'Год': ['2020-2021','2021-2022','2022-2023'],'Количество': [370,450,630],'Прирост':
            [130,80,180]}
            test_df = pd.DataFrame(data)		
            fig = make_subplots(1,1)

# add first bar trace at row = 1, col = 1
            fig.add_trace(go.Bar(x=test_df['Год'], y=test_df['Количество'],
                     name='Участников',
                     marker_color = marker,
                     opacity=1,
                     marker_line_width=2,
                     text=list(test_df['Количество']),
                     hovertext= ''
                     
),
              row = 1, col = 1)
            fig.update_layout(
                 font_family   = font,
                 font_size     = 13,
                 paper_bgcolor = tr,
                 plot_bgcolor  = tr,
                 margin        = dict(t=0, l=0, r=0, b=0),
                 yaxis_title     = "",
                 xaxis_title     = "",
                 width = 10,
                 height = 220,
                 xaxis_visible   = True,
                 showlegend       = False,
                 yaxis_visible   = False,
                 xaxis=dict(showgrid=False), 
                 yaxis=dict(showgrid=False),
                 
                 )
            fig.update_traces(
                 textfont_size = 14,
                 textangle     = 0,
                 textposition  = "inside",
                 cliponaxis    = False,
                 )
            fig['data'][0].width=0.7
# add first scatter trace at row = 1, col = 1
            fig.add_trace(go.Scatter(x=test_df['Год'], y=test_df['Прирост'], line=dict(color='#07C607'), name='Прирост'),
              row = 1, col = 1)
            st.plotly_chart(fig,use_container_width=True,config=config)

        
    with col2:
        with st.container():
            st.markdown('**Вовлечённость потока**')
            students_fesn = students_df.loc[(students_df['Программа'] == 'Бакалавриат') & (students_df['ВУЗ'] == 'ФЭСН РАНХиГС')]
            options = sorted(students_fesn['Поток'].unique(), reverse=True)
            # options = sorted(students_df.loc[(students_df['Бакалавриат'] == 'ФЭСН РАНХиГС')]['Бак. год'].unique(), reverse=True)
            # options = list(map(lambda x: f'{x} - {x+4}', options))
            year = st.selectbox(label='Выберите поток', options=options, index=0,label_visibility="collapsed")
            # year = int(year[:4])
            if year:
                # Айди студентов выбранного потока
                selected_students = students_fesn.loc[students_fesn['Поток'] == year]['ID студента']
                # Айди проектов, в которых они участвовали
                selected_students_in_projects = students_in_projects_df.loc[students_in_projects_df['ID студента'].isin(selected_students)]
                # Курс - Количество уникальных проектеров - Вовлеченность
                data = selected_students_in_projects.groupby('Курс в моменте')['ID студента'].nunique().reset_index(name='Количество')
                data['Вовлечённость'] = (data['Количество']/selected_students.nunique()) # Вовлеченность
                data = pd.DataFrame(index=['1','2','3','4']).merge(data.drop('Количество', axis=1).set_index('Курс в моменте'), how='left', left_index=True, right_index=True).fillna(0)
                
                fig = px.bar(data, color_discrete_sequence=colors,)
                fig.update_yaxes(range = [0,1])
                
                fig.update_layout(
                    yaxis_tickformat = ".0%",
                    showlegend       = False,
                    xaxis_title      = "Курс в моменте",
                    yaxis_title      = "Вовлечённость",
                    font_family      = font,
                    plot_bgcolor     = tr,
                    paper_bgcolor           = tr,                    
                    # font_size        = 7,
                    height = 160,
                    margin           = dict(t=0, l=0, r=0, b=0),
                    xaxis_visible   = False,
                    )
                
                fig.update_traces(hovertemplate = "<b>На %{label} курсе - %{value}</b>",cliponaxis    = False)
        
                st.plotly_chart(fig, use_container_width=True,config=config)
    with col3:
        with st.container():
            st.markdown('**Разделение по курсам**')
            data = {'Курс':['1 курс','2 курс','3 курс','4 курс','1 курс маг','2 курс маг'],
                    'Количество' : [60,80,70,40,10,5]}
            a = pd.DataFrame(data)
            fig = px.pie(a,
            values                  = a['Количество'],
            names                   = a['Курс'],
            color_discrete_sequence = colors,
            hole                    = .4
            )

            fig.update_traces(
                textposition  = 'inside',
                textinfo      = 'label',
                hovertemplate = "<b>%{label}.</b> Участников: <b>%{value}.</b> <br><b>%{percent}</b> от общего количества",
                textfont_size = 14
                
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
                height                  = 220,
                margin                  = dict(t=0, l=0, r=0, b=0),
                #legend=dict(orientation="h",yanchor="bottom",y=-0.4,xanchor="center",x=0,itemwidth=70,bgcolor = 'yellow')
                )

            st.plotly_chart(fig,use_container_width=True,config={'staticPlot': False,'displayModeBar': False})  
    with col4:
        with st.container():
            st.markdown('**Доля студентов 4 курса**')
            fig = px.pie(
            values                  = [94,27],
            names                   = ['Участвовали в проектах','Не участвовали в проектах'],
            color_discrete_sequence = colors,
            hole                    = .6
            )

            fig.update_traces(
                textposition  = 'inside',
                textinfo      = 'percent',
                hovertemplate = "<b>%{label}.</b><br><b>%{percent}</b> от студентов 4 курса",
                textfont_size = 14
                
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
                height                  = 220,
                margin                  = dict(t=0, l=0, r=0, b=0),
                #legend=dict(orientation="h",yanchor="bottom",y=-0.4,xanchor="center",x=0,itemwidth=70,bgcolor = 'yellow')
                )

            st.plotly_chart(fig,use_container_width=True,config={'staticPlot': False,'displayModeBar': False})
    with col5:
        with st.container():
            st.markdown('**Наши партнёры (ВУЗы)**')
    #Ряд интерактивов
    col1, col2 = st.columns([2, 4])
    

    with col1:
        with st.container():
            st.markdown('**Направления проектов**')

            # fields_df               = utils.query_data(query_dict['project_fields'])
            # fields_df['Количество'] = fields_df['Микро'].map(projects_df['Направление'].value_counts())
            # fields_df['Микро']      = fields_df['Микро'].str.replace(' ','<br>')
            # fields_df['Макро']      = '<b>'+fields_df['Макро'].astype(str)+'</b>'
            _fields_df = projects_df[['Макро-направление', 'Микро-направление']].copy()
            _fields_count = _fields_df['Микро-направление'].value_counts().reset_index(name='Количество')
            _fields_df = _fields_df.drop_duplicates(subset='Микро-направление')
            _fields_df['Макро-направление'] = _fields_df['Макро-направление'].apply(lambda x: f'<b>{x}</b>')
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
                font_family   = font,
                height = 400,
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
            st.markdown('**Интерактивные рейтинги**')
            rating_subject  = st.selectbox(label='Показывать топ', options=['Студентов','Преподавателей', ], index=0, label_visibility="collapsed")
            sort_asc = st.checkbox('По возрастанию',False,'sort_cb')
            chart_container = st.container()
            display_limit   = st.slider(label='Ограничить вывод', min_value=1, max_value=15, value=10, label_visibility="collapsed")
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
                paper_bgcolor           = tr,
                font_size       = 15,
                xaxis_visible   = False,
                yaxis_title     = "",
                height          = 250,
                margin          = dict(t=0, b=0,l=0,r=0),
                # title = f'Топ {display_limit} {rating_subject}',
                )
            fig.update_traces(
                textposition  = "inside",)
            fig['data'][0].width=0.4
            # display the plot
            chart_container.plotly_chart(fig, use_container_width=True, config=config)

if __name__ == "__main__":
    # page setup
    utils.page_config(layout='wide', title='FESSBoard')
    # styles
    utils.remove_footer()
    utils.load_local_css('css/main.css')
    utils.set_logo()
    # main func
    main()