import streamlit as st
import utils as utils
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pickle
import numpy as np

#Наборы цветов
color_themes = {
                'FESS'  : ['#ED1C24','#670004','#C53A40','#FCB6B9','#941B1E','#F85B61','#FFD5D7','#F78F92'],
                'ЦПР'    :['#3A42FF','#00046F','#2227A7','#88B1FF','#D3E2FF','#C0C0C0','#969696','#5B5B5B','#222222','#FFFFFF','#FB832A']
                }
tr='rgba(0,0,0,0)'
font="Source Sans Pro"
config = {'staticPlot': False,'displayModeBar': False}

def main():
    # load data
    with st.spinner('Читаем PMI и PMBOK...'):
        projects_df             = utils.load_projects()
    with st.spinner('Внедряем аджайл...'):
        students_in_projects_df     = utils.load_students_in_projects()
        moderators_in_projects_df   = students_in_projects_df.loc[students_in_projects_df['Модератор'] == 1]
        curators_in_projects_df     = students_in_projects_df.loc[students_in_projects_df['Куратор'] == 1]
        students_in_projects_df     = students_in_projects_df.loc[(students_in_projects_df['Куратор'] == 0) & (students_in_projects_df['Модератор'] == 0)]
        teachers_in_projects_df = utils.load_teachers_in_projects()
    with st.spinner('Изучаем требования стейкхолдеров...'):
        students_df             = utils.load_students()
    with st.spinner('Нежно обращаемся к базе данных...'):
        universities_df         = utils.load_universities()
    with st.spinner('Советуемся с ChatGPT...'):
        events_df               = utils.load_events()
        students_in_events_df   = utils.load_students_in_events()
    with st.spinner('Звоним представителям компаний...'):
        companies_df   = utils.load_companies()
    
    selection = st.sidebar.selectbox(options =color_themes.keys(),label='Выберите тему')
    colors = color_themes[selection]
    marker = colors[0]
    # Ряд метрик
    with st.container():
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        # Проекты в работы ( активно vs. завершено )
        col1.metric(
            label       = 'Проектов в работе',
            value       = projects_df[projects_df['Статус'] == 'Активен'].shape[0],
            delta       = '{} выполнено'.format(projects_df[projects_df['Статус'] == 'Завершен'].shape[0]),
            delta_color = 'normal')
        # Уникальных студентов ( активно vs. побывало )
        col2.metric(
            label       = 'Студентов активно',
            value       = students_in_projects_df['ID студента'].loc[students_in_projects_df['Статус'] == 'Активен'].nunique(),
            delta       = '{} за все время'.format(students_in_projects_df['ID студента'].nunique()),
            delta_color = 'normal')
        # Компаний партнеров ( всего vs. отрасли )
        ## Новых компаний в этом году:
        ## projects_df[['Дата начала','Название компании']].sort_values('Дата начала').drop_duplicates(subset='Название компании', keep='first').loc[projects_df['Дата начала'] >= date(date.today().year, 1, 1)].shape[0]
        col3.metric(
            label       = 'Компаний', 
            value       = projects_df['Название компании'].nunique(),
            delta       = 'из {} отраслей(-и)'.format(projects_df['Отрасль'].nunique()),
            delta_color = 'normal')
        # Университетов партнеров ( количество, регионы )
        col4.metric(
            label       = 'ВУЗов-партнёров',
            value       = universities_df.shape[0],
            delta       = 'из {} регионов(-а)'.format(universities_df['Регион'].nunique()),
            delta_color = 'normal')
        # Направления и сферы
        col5.metric(
            label       = 'Направлений',
            value       = projects_df['Микро-направление'].nunique(),
            delta       = 'из {} сфер(-ы)'.format(projects_df['Макро-направление'].nunique()),
            delta_color = 'normal')
        # Мероприятия
        col6.metric(
            label       = 'Мероприятий',
            value       = events_df.shape[0],
            delta       = '{} участников(-а)'.format(students_in_events_df.shape[0]),
            delta_color = 'normal')
    # Ряд графиков о проектах
    col1, col2,col3 = st.columns([1, 2,3])
    with col1:
        ## Распределение грейдов
        with st.container():
            st.markdown('<p class="tooltip"><strong>Грейды проектов</strong><span class="tooltiptext">Показывает чудеса грейдного членения</span></p>', unsafe_allow_html=True)
            k = projects_df['Грейд'].value_counts()
            utils.donut_chart(values=k.values, names=k.index, colors=colors)
    with col2:
        ## Число и темп прироста проектов
        with st.container():
            st.markdown('**Число и темп прироста проектов**')
            data                    = projects_df.groupby('Академический год')['ID проекта'].nunique().reset_index()
            data['Темп прироста']   = data['ID проекта'].pct_change().fillna(0)
            utils.two_axis_barchart(data.tail(5), marker, value_label='проектов', primary_col='ID проекта')

    with col3:
        ## Регионы мероприятий
        with st.container():
            st.markdown('**Распределение мероприятий по регионам**')
            events_regions_df = events_df['Регион'].value_counts()
            events_regions_df.name = 'cases'

            with open('counties.pkl', 'rb') as f:
                counties = pickle.load(f)
            
            region_id_list = []
            regions_list = []
            for k in range(len(counties['features'])):
                region_id_list.append(counties['features'][k]['id'])
                regions_list.append(counties['features'][k]['properties']['name'])
            df_regions = pd.DataFrame()
            df_regions['region_id'] = region_id_list
            df_regions['region_name'] = regions_list
            df_regions.set_index('region_name',inplace=True)
            df_regions = df_regions.merge(events_regions_df.to_frame(),left_index=True, right_index=True)

            if selection =='FESS':
                colors_map = ['#FFD5D7','#ED1C24']
            else:
                colors_map = ['#D6E4FF','#3A42FF']


            fig = go.Figure(go.Choroplethmapbox(geojson=counties,
                            locations=df_regions['region_id'],
                            z=df_regions['cases'],
                            text=df_regions.index.values,
                            colorscale = colors_map,
                            colorbar_thickness=5,
                            customdata=np.stack([df_regions['cases'],df_regions.index.values], axis=-1),
                            hovertemplate='<b>%{text}</b>'+ '<br>' +
                                            'Ивентов: %{z}' + '<br>',
                            hoverinfo='text, z',
                            
                            ))
            fig.update_traces(marker_line_width=1)
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                    mapbox_zoom=3.5, mapbox_center = {"lat": 55.75222, "lon": 37.61556},
                    mapbox_pitch=0,
                    mapbox_bearing=0,
                    height = 220,
                    mapbox_style="carto-positron",
                )
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': False,'displayModeBar': False})
    
    # Ряд логотипов
    col1, col2,col3,col4,col5,col6 = st.columns([1,1,1,1,1,1])
    with col1:
        with st.container():
            st.image(
                image = 'https://raw.githubusercontent.com/terrorChay/FESSBoard-images/main/logo/companies/sber_logo.png',
                use_column_width = 'auto',
            )
    with col2:
        with st.container():
            st.image(
                image = 'https://raw.githubusercontent.com/terrorChay/FESSBoard-images/main/logo/companies/mik_logo.png',
                use_column_width = 'auto',
            )
    with col3:
        with st.container():
            st.image(
                image = 'https://raw.githubusercontent.com/terrorChay/FESSBoard-images/main/logo/companies/segezha_logo.png',
                use_column_width = 'auto',
            )
    with col4:
        with st.container():
            st.image(
                image = 'https://raw.githubusercontent.com/terrorChay/FESSBoard-images/main/logo/companies/schneider_logo.png',
                use_column_width = 'auto',
            )
    with col5:
        with st.container():
            st.image(
                image = 'https://raw.githubusercontent.com/terrorChay/FESSBoard-images/main/logo/companies/xiaomi_logo.png',
                use_column_width = 'auto',
            )
    with col6:
        with st.container():
            st.image(
                image = 'https://raw.githubusercontent.com/terrorChay/FESSBoard-images/main/logo/companies/bosch_logo.png',
                use_column_width = 'auto',
            )
    # # Ряд Компаний-парнёров      
    col1, col2,col3,col4 = st.columns([1, 2,2,1])
    with col1:
        with st.container():
            st.markdown('**Топ заказчиков**')
            top_companies_df = projects_df[['Название компании','Тип компании']]
            top_companies_df = top_companies_df[top_companies_df['Тип компании']!='Частное лицо']
            top_companies_df = top_companies_df['Название компании'].value_counts().head(5)
            utils.donut_chart(values=top_companies_df.values, names=top_companies_df.index, colors=colors)
    with col2:
        with st.container():
            st.markdown('**Динамика вовлеченности компаний**')
            data                    = projects_df.groupby('Академический год')['ID компании'].nunique().reset_index()
            data['Темп прироста']   = data['ID компании'].pct_change().fillna(0)
            utils.two_axis_barchart(data.tail(5), marker, value_label='заказчиков', primary_col='ID компании')           
    with col3:
        with st.container():
            st.markdown('**Проекты по типу компании-заказчика**')
            data = projects_df['Тип компании'].value_counts()
            v=data.values
            n=data.index
            utils.donut_chart(v,n,colors,legend=True,textinfo='percent')
    with col4:
        with st.container():
            a = companies_df['Тип компании'].value_counts()
            st.metric('Российские', a['Крупный российский бизнес'] + a['Малый и средний российский бизнес'] + a['Государственная структура'])
            st.metric('Международные', a['Малый и средний международный бизнес'] + a['Крупный международный бизнес'])
            st.metric('Активные партнеры', projects_df[['Академический год', 'ID компании']].groupby('Академический год').nunique().iloc[-1])
    # Ряд студентов топ
    col1, col2,col3,col4 = st.columns([1, 2,2,1])
    with col1:
        with st.container():
            try:
                st.markdown('**Разделение по курсам**')
                courses_df = students_in_projects_df[['Статус','ID студента','Курс в моменте','Программа в моменте','ВУЗ в моменте']]
                courses_df = courses_df.loc[(courses_df['Статус'] == 'Активен')&(courses_df['ВУЗ в моменте'] == 'ФЭСН РАНХиГС')]
                courses_df['Курс'] = courses_df[['Курс в моменте','Программа в моменте']].agg(' '.join,axis=1).apply(lambda x:x[:5]+'.')
                courses_df = courses_df[['ID студента','Курс']].drop_duplicates(subset = ['ID студента','Курс'], keep=False)
                j = courses_df['Курс'].value_counts()
                utils.donut_chart(values=j.values, names=j.index, colors=colors, hovertemplate="<b>%{label}.</b> Участников: <b>%{value}.</b> <br><b>%{percent}</b> от общего количества")
            except:
                st.warning('Сейчас нет активных проектов :)')
                pass
    with col2:
        with st.container():
            st.markdown('**Динамика вовлеченности студентов**')
            data                    = students_in_projects_df.groupby('Академический год')['ID студента'].nunique().reset_index()
            data['Темп прироста']   = data['ID студента'].pct_change().fillna(0)
            utils.two_axis_barchart(data.tail(5), marker, value_label='студентов', primary_col='ID студента')

        
    with col3:
        with st.container():
            st.markdown('**Вовлечённость потока**')
            students_fesn = students_df.loc[(students_df['Программа'] == 'Бакалавриат') & (students_df['ВУЗ'] == 'ФЭСН РАНХиГС')]
            options = sorted(students_fesn['Поток'].unique(), reverse=True)
            year = st.selectbox(label='Выберите поток', options=options, index=3,label_visibility="collapsed")
            if year:
                # Айди студентов выбранного потока
                selected_students = students_fesn.loc[students_fesn['Поток'] == year]['ID студента']
                # Айди проектов, в которых они участвовали
                selected_students_in_projects = students_in_projects_df.loc[students_in_projects_df['ID студента'].isin(selected_students)]
                # Курс - Количество уникальных проектеров - Вовлеченность
                data = selected_students_in_projects.groupby('Курс в моменте')['ID студента'].nunique().reset_index(name='Количество')
                data['Вовлечённость'] = (data['Количество']/selected_students.nunique()) # Вовлеченность
                data = pd.DataFrame(index=['1','2','3','4']).merge(data.drop('Количество', axis=1).set_index('Курс в моменте'), how='left', left_index=True, right_index=True).fillna(0)
                # Отрисовка чарта
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
                    xaxis_visible   = True,
                    )
                fig.update_traces(hovertemplate = "<b>На %{label} курсе - %{value}</b>",cliponaxis    = False)
                st.plotly_chart(fig, use_container_width=True,config=config)
    
    with col4:
        with st.container():
            st.markdown('**Студенты 4 курса**')
            course_4_df = students_df.loc[(students_df['Курс'] == '4') & (students_df['Программа'] == 'Бакалавриат')&(students_df['ВУЗ']=='ФЭСН РАНХиГС'),'ID студента']
            merged_df = pd.merge(course_4_df, students_in_projects_df, on='ID студента', how='left')
            merged_df = merged_df[merged_df['ID проекта'].notna()]
            #Сколько людей принимали участие
            tp = merged_df['ID студента'].nunique()
            #Сколько людей не принимали участие
            dtp = course_4_df.count() - tp
            v=[tp,dtp]
            n=['Участвовали в проектах','Не участвовали в проектах']
            utils.donut_chart(v,n,colors, textinfo='value', hovertemplate="<b>%{label}.</b><br><b>%{percent}</b> от студентов 4 курса")
    #Ряд интерактивов
    col1, col2 = st.columns([2, 4])
    

    with col1:
        with st.container():
            st.markdown('**Направления проектов**')
            sunburst = colors

            # fields_df               = utils.query_data(query_dict['project_fields'])
            # fields_df['Количество'] = fields_df['Микро'].map(projects_df['Направление'].value_counts())
            # fields_df['Микро']      = fields_df['Микро'].str.replace(' ','<br>')
            # fields_df['Макро']      = '<b>'+fields_df['Макро'].astype(str)+'</b>'
            _fields_df = projects_df[['Макро-направление', 'Микро-направление']].copy()
            _fields_count = _fields_df['Микро-направление'].value_counts().reset_index()
            _fields_count.columns = ['Микро-направление', 'Количество']
            _fields_df = _fields_df.drop_duplicates(subset='Микро-направление')
            _fields_df['Макро-направление'] = _fields_df['Макро-направление'].apply(lambda x: f'<b>{x}</b>')
            _fields_df = _fields_df.merge(_fields_count, on='Микро-направление')
            fig = px.sunburst(_fields_df,
            path                    = ['Макро-направление', 'Микро-направление'],
            values                  = _fields_df['Количество'],
            branchvalues            = "total",
            color_discrete_sequence = sunburst
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
                sort                  = True,
                leaf = {'opacity':0.8}
                )

            st.plotly_chart(fig, use_container_width=True,config=config)
    with col2:
        with st.container():
            st.markdown('**Интерактивные рейтинги**')
            _col1, _col2, _col3 = st.columns(3)
            with _col1:
                rating_subject  = st.selectbox(label='Роль', options=['Участники', 'Кураторы', 'Модераторы', 'Преподаватели'],index=0)
            with _col3:
                sort_asc = st.selectbox(label='Сортировать', options=['Возрастание', 'Убывание'],index=1)
                sort_asc = True if sort_asc == 'Возрастание' else False
            with _col2:
                display_limit = st.selectbox(label='Топ', options=[5,10,15],index=1)
            # data selection
            if rating_subject == 'Преподаватели':
                data = teachers_in_projects_df.value_counts(subset='ФИО преподавателя', ascending=sort_asc)
            elif rating_subject == 'Участники':
                data = students_in_projects_df.value_counts(subset='ФИО студента', ascending=sort_asc)
            elif rating_subject == 'Кураторы':
                data = curators_in_projects_df.value_counts(subset='ФИО студента', ascending=sort_asc)
            elif rating_subject == 'Модераторы':
                data = moderators_in_projects_df.value_counts(subset='ФИО студента', ascending=sort_asc)
            data = data[data.index.str.contains("Типовой")==False ].iloc[:display_limit]
            # set up a plot
            fig = px.bar(data, orientation='h', color_discrete_sequence=colors,text_auto=True)
            fig.update_layout(
                yaxis=dict(autorange="reversed"),
                showlegend      = False,
                font_family     = font,
                plot_bgcolor    = tr,
                paper_bgcolor           = tr,
                font_size       = 15,
                xaxis_visible   = False,
                yaxis_title     = "",
                height          = 300,
                margin          = dict(t=0, b=0,l=0,r=0),
                # title = f'Топ {display_limit} {rating_subject}',
                )
            fig.update_traces(
                textposition  = 'outside')
            fig['data'][0].width=0.6
            # display the plot
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True,'displayModeBar': False})

 
if __name__ == "__main__":
    # page setup
    utils.page_config(layout='wide', title='FESSBoard', page_icon=':bar_chart:')
    # styles
    utils.remove_footer()
    utils.load_local_css('css/main.css')
    utils.set_logo()
    # main func
    main()