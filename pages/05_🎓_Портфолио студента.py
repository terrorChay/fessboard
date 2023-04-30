import streamlit as st
from streamlit import session_state as session
import utils as utils
import pandas as pd
import numpy as np
import re
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_float_dtype,
)
import plotly.express as px
from connectdb import mysql_conn
from datetime import date
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Наборы цветов
color_themes = {
                'FESS'  : ['#ED1C24','#670004','#C53A40','#FCB6B9','#941B1E','#F85B61','#FFD5D7','#F78F92'],
                'ЦПР'    :['#3A42FF','#00046F','#2227A7','#88B1FF','#D3E2FF','#C0C0C0','#969696','#5B5B5B','#222222','#FFFFFF','#FB832A']
                }
tr='rgba(0,0,0,0)'




font="Source Sans Pro"
config = {'staticPlot': False,'displayModeBar': False}

# Apply search filters and return filtered dataset
def search_dataframe(df: pd.DataFrame, label='Поиск') -> pd.DataFrame:

    df = df.copy()

    user_text_input = st.text_input(label, placeholder='Введите текст', help='Укажите текст, который могут содержать интересующие Вас проекты')

    if user_text_input:
        _user_text_input = "".join([char for char in user_text_input if char.isalnum()])
        mask = df.apply(lambda x: x.astype(str).str.contains(_user_text_input, na=False, flags=re.IGNORECASE))
        df = df.loc[mask.any(axis=1)]

    return df

# Apply filters and return filtered dataset
def filter_dataframe(df: pd.DataFrame, cols_to_ignore: list) -> pd.DataFrame:

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)
    
    modification_container = st.container()

    with modification_container:
        cols = [col for col in df.columns if col not in cols_to_ignore]
        to_filter_columns = st.multiselect("Параметры фильтрации", cols)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("└")
            if 'Менеджер' in df[column].name or 'Курирующий' in df[column].name:
                options = pd.Series([x for _list in df[column][df[column].notna()] for x in _list]).unique()
                user_cat_input = right.multiselect(
                    f"{column}",
                    options,
                )
                if user_cat_input:
                    df = df[df[column].astype(str).str.contains('|'.join(user_cat_input))]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f" {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f" {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            elif (is_categorical_dtype(df[column]) or df[column].nunique() < 10 or df[column].map(len).max() < 255) and ('Название проекта' not in df[column].name):
                options = df[column].unique()
                user_cat_input = right.multiselect(
                    f"{column}",
                    options,
                )
                if user_cat_input:
                    _cat_input = user_cat_input
                    df = df[df[column].isin(_cat_input)]
            else:
                user_text_input = right.text_input(
                    f"{column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input, na=False, flags=re.IGNORECASE)]

    # Try to convert datetimes into displayable date formats
    for col in df.columns:
        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%d-%m-%Y')

    return df

# Apply filters and return company name
def select_student(df: pd.DataFrame):
    student_id = False
    df = df[['ID студента', 'ФИО студента']].copy().dropna().drop_duplicates()
    df.insert(0, 'Составной ключ', df['ID студента'].astype('str') + ' - ' + df['ФИО студента'])
    options = np.insert(df['Составной ключ'].unique(), 0, 'Не выбрано', axis=0)

    ## preselection tweak once again to preserve selected company in case related filters get adjusted
    preselection = 0
    if 'student_selectbox' in session:
        try:
            preselection = int(np.where(options == session['student_selectbox'])[0][0])
        except:
            pass

    selected_student = st.selectbox("Студент", options, index=preselection,key='student_selectbox', )
    if selected_student and selected_student != 'Не выбрано':
        student_id = int(selected_student.split(' - ')[0])

    return student_id

# App launch
def run():
    # Load data
    with st.spinner('Масштабируем Agile...'):
        projects_df             = utils.load_projects()
        students_in_projects_df = utils.load_students_in_projects()
    with st.spinner('Еще чуть-чуть и прямо в рай...'):
        students_df             = utils.load_students()
    with st.spinner('Звоним в деканат...'):
        fields_df               = utils.load_fields()
    with st.spinner('Поднимаем архивы...'):
        events_df               = utils.load_events()
        students_in_events_df   = utils.load_students_in_events()
    selection = st.sidebar.selectbox(options =color_themes.keys(),label='Выберите тему')
    colors = color_themes[selection]
    marker = colors[0]
    st.title('Портфолио студента')
    st.write('''
            #### На данной странице можно ознакомиться с портфелем проектов выбранного студента!
            :sparkles: Раздел **Сводная** содержит общую информацию о выбранном студенте.  
            :performing_arts: Разделы **Проектерство**, **Кураторство** и **Модераторство** содержат информацию о проектах, в которых студент выступал в соответствующей роли.  
            :world_map: Раздел **Мероприятия** содержит перечень выездных и местных мероприятий, в которых участвовал студент.\n

            :floppy_disk: Вы также можете скачать портфолио студента в формате PDF.
            ''')

    student_id = select_student(students_df)
    if student_id:
        student_info = students_df.loc[students_df['ID студента'] == student_id]
        projects_with_student_df = students_in_projects_df.loc[students_in_projects_df['ID студента'] == student_id]
        if projects_with_student_df.shape[0] > 0:
            # Calculate activity
            regular_projects_idx = projects_with_student_df.loc[(projects_with_student_df['Куратор'] == 0) & (projects_with_student_df['Модератор'] == 0)]['ID проекта']
            regular_projects_df = projects_df.loc[projects_df['ID проекта'].isin(regular_projects_idx)]
            #
            curated_projects_idx = projects_with_student_df.loc[projects_with_student_df['Куратор'] == 1]['ID проекта']
            curated_projects_df = projects_df.loc[projects_df['ID проекта'].isin(curated_projects_idx)]
            #
            moderated_projects_idx = projects_with_student_df.loc[projects_with_student_df['Модератор'] == 1]['ID проекта']
            moderated_projects_df = projects_df.loc[projects_df['ID проекта'].isin(moderated_projects_idx)]
            #
            events_participated_idx = students_in_events_df.loc[students_in_events_df['ID студента'] == student_id]['ID мероприятия']
            events_participated_df = events_df.loc[events_df['ID мероприятия'].isin(events_participated_idx)]
            #
            tab1, tab2, tab3, tab4, tab5 = st.tabs(['Сводная', 'Проектерство', 'Кураторство', 'Модераторство', 'Мероприятия'])
            # Analytics tab
            with tab1:
                student_fullname = student_info['ФИО студента'].values[0]
                st.subheader(student_fullname)
                st.markdown(f"""
                            **Университет:** {student_info['ВУЗ'].values[0]}  
                            **Курс:** {student_info['Курс'].values[0]}, {student_info['Программа'].values[0]}  
                            **Поток:** {student_info['Поток'].values[0]}
                            """)
                #
                projects_summary = {
                    'Выполнено проектов'    : projects_with_student_df.loc[(projects_with_student_df['Статус'] == 'Завершен')|(projects_with_student_df['Статус'] == 'Заморожен')].shape[0],
                    'Проектов в работе'     : projects_with_student_df.loc[projects_with_student_df['Статус'] == 'Активен'].shape[0],
                    'Любимая компания'      : projects_df.loc[projects_df['ID проекта'].isin(projects_with_student_df['ID проекта'])]['Название компании'].mode()[0],
                    'В проектах'            : f"c {projects_with_student_df.sort_values(by='Академический год').iloc[0]['Курс в моменте']} курса",
                }
                #
                total_activity = {
                    "Участник команды"      : regular_projects_df,
                    "Куратор проекта"       : curated_projects_df,
                    "Модератор проекта"     : moderated_projects_df
                }
                st.download_button(label='💾 Скачать портфолио', data=utils.student_to_pdf(student_info, projects_summary, total_activity, events_participated_df), file_name=f"{student_fullname}.pdf", mime="application/pdf",)
                # Project summary metrics
                cols = st.columns(4)
                for idx, key in enumerate(list(projects_summary)):
                    cols[idx].metric(key, projects_summary[key])
                # Project summary visualization
                col1, col2, col3,col4 = st.columns(4)
                # График распределения проектов студента по макронаправлениям
                with col1:
                    st.markdown('**Распределение проектов студента по макронаправлениям**')
                    data = projects_df.loc[projects_df['ID проекта'].isin(projects_with_student_df['ID проекта'])]['Макро-направление'].value_counts().reset_index(name='Количество')
                    data = data.rename(columns={'index':'Макро'})
                    data = data.drop_duplicates().merge(fields_df['Макро'].drop_duplicates(), on='Макро', how='right').fillna(0).sort_values(by='Количество')
                    fig = px.line_polar(data,r='Количество',theta='Макро',line_close=True,color_discrete_sequence=colors)
                    fig.update_traces(fill='toself',mode='lines+markers',cliponaxis=False)
                    fig.update_layout(
                        font_family=font,
                        font_size = 10,
                        paper_bgcolor = tr,
                        plot_bgcolor  = tr,
                        height = 220,
                        yaxis_visible   = False,
                        margin                  = dict(t=35, l=0, r=0, b=35))
                    fig.update_layout(polar = dict(radialaxis = dict(showticklabels = False,tick0=0,dtick=1)))
                    st.plotly_chart(fig,use_container_width=True,config={'staticPlot': False,'displayModeBar': False})
                # График распределения проектов студента по грейдам
                with col3:
                    st.markdown('**Распределение проектов студента по<br>грейдам**',unsafe_allow_html=True)
                    data = projects_df.loc[projects_df['ID проекта'].isin(projects_with_student_df['ID проекта'])]['Грейд'].value_counts().reset_index(name='Количество')
                    data = data.rename(columns={'index':'Грейд'})
                    v = data['Количество']
                    n = data['Грейд']
                    utils.donut_chart(v,n,colors)     
                # График вовлеченности студента в проекты по курсам
                with col4:
                    st.markdown('**Вовлеченность студента в проекты<br>по курсам**',unsafe_allow_html=True)
                    projects_by_year_df = projects_with_student_df
                    projects_by_year_df['Курс'] = projects_with_student_df[['Курс в моменте','Программа в моменте']].agg(' '.join,axis=1).map(lambda x:x[:5]+'.')
                    projects_by_year_df = projects_by_year_df[['Курс']].copy().sort_values('Курс').value_counts(sort=True).reset_index(name='Количество')
                    df = pd.DataFrame(data=['1 Бак.','2 Бак.','3 Бак.','4 Бак.','1 Маг.','2 Маг.'],columns=['Курс'])
                    df = df.merge(projects_by_year_df,how='left',on='Курс')
                    df['Количество'] = df['Количество'].fillna(0).map(lambda x:int(x))
                    fig = go.Figure()

                    fig.add_trace(go.Bar(
                            x                   = df['Курс'],
                            y                   = df['Количество'],
                            width               = 0.7,
                            name                = 'Проектов',
                            marker_color        = marker,
                            opacity             = 1,
                            marker_line_width   = 0,
                            text                = list(df['Количество']),
                            ))
                        
                    fig.update_layout(
                        font_family    = font,
                        font_size      = 13,
                        paper_bgcolor  = tr,
                        plot_bgcolor   = tr,
                        margin         = dict(t=0, l=0, r=0, b=0),
                        yaxis_title    = "",
                        xaxis_title    = "",
                        width          = 10,
                        height         = 230,
                        xaxis_visible  = True,
                        yaxis_visible  = True,
                        xaxis          = dict(showgrid=False), 
                        yaxis          = dict(showgrid=True),
                        showlegend     = False
                        )
                    fig.update_traces(
                        textfont_size   = 14,
                        textangle      = 0,
                        textposition   = "auto",
                        cliponaxis     = False,
                        )
                    
                    st.plotly_chart(fig,use_container_width=True,config={'staticPlot': True,'displayModeBar': False})
                # Распределение проектов студента по микронаправлениям
                with col2:
                    data = projects_df.loc[projects_df['ID проекта'].isin(projects_with_student_df['ID проекта'])]['Микро-направление'].value_counts().reset_index(name='Количество')
                    data = data.rename(columns={'index':'Микро'})
                    st.markdown('**Распределение проектов студента по микронаправлениям**')
                    v = data['Количество']
                    n = data['Микро']
                    utils.donut_chart(v,n,colors,textinfo='value')
            # Display regular projects 
            with tab2:
                if regular_projects_df.shape[0] > 0:
                    st.info("В данной выборке представлены только те проекты, в которых студент выступал(-а) в роли участника.", icon="ℹ️")
                    st.dataframe(regular_projects_df)
                else:
                    st.warning('Студент пока не участвовал в проектах.')
            # Display curated projects
            with tab3:
                if curated_projects_df.shape[0] > 0:
                    st.info("В данной выборке представлены только те проекты, в которых студент выступал(-а) в роли куратора.", icon="ℹ️")
                    st.dataframe(curated_projects_df)
                else:
                    st.warning('Студент пока не выступал в роли куратора.')
            # Display moderated projects
            with tab4:
                if moderated_projects_df.shape[0] > 0:
                    st.info("В данной выборке представлены только те проекты, в которых студент выступал(-а) в роли модератора.", icon="ℹ️")
                    st.dataframe(moderated_projects_df)
                else:
                    st.warning('Студент пока не выступал в роли модератора.')
            # Display events participated
            with tab5:
                if events_participated_df.shape[0] > 0:
                    st.info("В данной выборке представлены только эвенты, хакатоны и прочие мероприятия.", icon="ℹ️")
                    st.dataframe(events_participated_df)
                else:
                    st.warning('Студент пока не участвовал в мероприятиях.')
            
        else:
            st.warning('Проекты не найдены')
    else:
        st.markdown(f"<h4 style='text-align: center;'>Выберите студента 😎</h4>", unsafe_allow_html=True)
    
if __name__ == "__main__":
    utils.page_config(layout='wide', title='Портфолио компании', page_icon=':bar_chart:')
    utils.load_local_css('css/student.css')
    utils.remove_footer()
    utils.set_logo()
    run()