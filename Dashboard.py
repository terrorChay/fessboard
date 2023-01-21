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
        students_in_projects_df = utils.load_people_in_projects()
    with st.spinner('Изучаем требования стейкхолдеров...'):
        teachers_in_projects_df = utils.load_people_in_projects(teachers=True)
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
    # Ряд проектов
    col1, col2,col3,col5 = st.columns([1, 2,2,1])
    with col1:
        with st.container():
            st.markdown('**Грейды проектов**')
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
        with st.container():
            st.markdown('**Число проектов в год**')
            df = projects_df[['Академический год']].copy()
            df.dropna(inplace=True)
            df = df.sort_values('Академический год').value_counts(sort=False).reset_index(name='Количество')
            df['Темп прироста'] = df['Количество'].pct_change().fillna(0)
            test_df = df
            # data    = {'Год': ['2018-2019', '2019-2020', '2020-2021','2021-2022','2022-2023'],'Количество': [16, 24, 37,45,63],'Прирост':
            # [16,8,13,8,18]}
            # test_df = pd.DataFrame(data)

            fig = make_subplots(1,1)

# add first bar trace at row = 1, col = 1
            fig.add_trace(go.Bar(x=test_df['Академический год'], y=test_df['Количество'],
                     name='Проектов',
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
            fig.add_trace(go.Scatter(x=test_df['Академический год'], y=test_df['Темп прироста'], line=dict(color='#07C607'), name='Темп прироста'),
              row = 1, col = 1)
            st.plotly_chart(fig,use_container_width=True,config=config)
    with col3:
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
    #Ряд логотипов
    col1, col2,col3,col4,col5,col6 = st.columns([1, 1,1,1,1,1])

    with col1:
        with st.container():
            st.image(
                image = r'img\sber_logo.png',
                use_column_width = 'auto',
            )
    with col2:
        with st.container():
            st.image(
                image = r'img\mik_logo.png',
                use_column_width = 'auto',
            )
    with col3:
        with st.container():
            st.image(
                image = r'img\bosch_logo.png',
                use_column_width = 'auto',
            )
    with col4:
        with st.container():
            st.image(
                image = r'img\schneider_logo.png',
                use_column_width = 'auto',
            )
    with col5:
        with st.container():
            st.image(
                image = r'img\xiaomi_logo.png',
                use_column_width = 'auto',
            )
    with col6:
        with st.container():
            st.image(
                image = r'img\segezha_logo.png',
                use_column_width = 'auto',
            )
    # Ряд Компаний-парнёров      
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
                legend                  = dict(orientation="v",itemwidth=70,yanchor="bottom", y=1.02,xanchor="right",x=1),
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
            st.markdown('**Число участников проектной деятельности в год**')

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
                    # font_size        = 7,
                    height = 220,
                    margin           = dict(t=0, l=0, r=0, b=0),
                    xaxis_visible   = False,
                    )
                
                fig.update_traces(hovertemplate = "<b>%{label}.</b> Вовлечённость: <b>%{value}</b>",cliponaxis    = False)
        
                st.plotly_chart(fig, use_container_width=True,config=config)
    with col3:
        with st.container():
            st.markdown('**Разделение по курсам**')   
    with col4:
        with st.container():
            st.markdown('**Доля студентов 4 курса кто хотя бы раз учавствовал в проектах**')
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

    col1, col2 = st.columns([1,1])
    with col1:
        with st.container():
            data = projects_df['Тип компании']
            data1 = projects_df['Отрасль']
            fig = make_subplots(1,2,specs=[[{'type':'domain'}, {'type':'domain'}]],
                    )
            fig.add_trace(go.Pie(values= data.value_counts(),labels= data.value_counts().index, marker_colors=colors,hole=.4),1,1)
            fig.add_trace(go.Pie(values= data1.value_counts(),labels= data1.value_counts().index, marker_colors=colors,hole=.4),1,2)
            fig.update_layout(
                plot_bgcolor            = tr,
                paper_bgcolor           = tr,
                #legend                 = dict(yanchor="bottom",y=0.1,xanchor="left",x=0.5),
                showlegend              = False,
                font_family             = font,
                title_font_family       = font,
                legend_title_font_color = "white",
                height                  = 220,
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


if __name__ == "__main__":
    # page setup
    utils.page_config(layout='wide', title='FESSBoard')
    # styles
    utils.remove_footer()
    utils.load_local_css('css/main.css')
    utils.set_logo()
    # main func
    main()