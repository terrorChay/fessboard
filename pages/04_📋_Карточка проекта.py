import streamlit as st
from streamlit import session_state as session
import utils as utils
from my_query import query_dict
import pandas as pd
import numpy as np
import re
from io import BytesIO
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import plotly.express as px
from connectdb import mysql_conn
from datetime import date

# Apply search filters and return filtered dataset
def search_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    user_text_input = st.text_input(f"Поиск по проектам", help='Укажите текст, который могут содержать интересующие Вас проекты')

    if user_text_input:
        _user_text_input = "".join([char for char in user_text_input if char.isalnum()])
        mask = df.apply(lambda x: x.astype(str).str.contains(_user_text_input, na=False, flags=re.IGNORECASE))
        df = df.loc[mask.any(axis=1)]

    return df

# Apply filters and return project name
def project_selection(df: pd.DataFrame):
    df = df[['ID проекта', 'Название проекта', 'Название компании', 'Грейд', 'Статус', 'Макро-направление', 'Микро-направление', 'Академический год']].sort_values(by='ID проекта', ascending=False).copy()
    df.insert(0, 'Составной ключ', df['ID проекта'].astype('str') + ' - ' + df['Название проекта'])
    selected_project = False

    modification_container = st.container()
    with modification_container:
        col01, col02, col03 = st.columns(3)
        cols_list = [col01, col02, col03]
        # Filters for project selection
        ## df.columns[3:] so that the composite key, project id and project name are ignored
        for idx, column in enumerate(['Академический год', 'Название компании',  'Макро-направление', 'Грейд', 'Статус', 'Микро-направление']):
            options = df[column].unique()
            ### preselection tweak to preserve selected filter values in case related filters get adjusted
            cached_value_key = column+'-input'
            preselection = []
            if cached_value_key in session:
                for i in session[cached_value_key]:
                    try:
                        if i in options:
                            preselection.append(i)
                    except:
                        pass
            ### display every other input field on the right column, all the rest - on the left column
            col = cols_list[idx] if idx < 3 else cols_list[idx-3]
            user_cat_input = col.multiselect(
                f"{column}",
                options,
                default=preselection,
                key=cached_value_key,
            )
            if user_cat_input:
                df = df[df[column].isin(user_cat_input)]
        options = np.insert(df['Составной ключ'].unique(), 0, 'Не выбрано', axis=0)

        # Project name selection
        ## preselection tweak once again to preserve selected company in case related filters get adjusted
        preselection = 0
        if 'project_selectbox' in session:
            try:
                preselection = int(np.where(options == session['project_selectbox'])[0][0])
            except:
                pass
        
        user_cat_input = st.selectbox(
            ":heavy_exclamation_mark: **Выберите проект**",
            options,
            index=preselection,
            key='project_selectbox',
        )
        if user_cat_input and user_cat_input != 'Не выбрано':
            selected_project = user_cat_input

    return selected_project

# App launch
def run():
    # Load dataframe
    with st.spinner('Читаем НИР...'):
        projects_df = utils.load_projects()
    with st.spinner('Заглядываем во все 6 шляп...'):
        students_in_all_projects = utils.load_students_in_projects()

    st.title('Карточка проекта')
    st.write('''
            #### На данной странице можно ознакомиться с карточкой выбранного проекта!
            :art: Используйте фильтры, чтобы быстрее найти нужный проект.  
            ''')
    # user input
    selected_project = project_selection(projects_df)
    # Draw search filters and return filtered df
    if not selected_project:
        st.markdown(f"<h4 style='text-align: center;'>Выберите проект 😎</h4>", unsafe_allow_html=True)
    else:
        project_id = int(selected_project.split(' - ')[0])
        output = projects_df.loc[projects_df['ID проекта'] == project_id].to_dict('records')[0]
        # Convert dates to day.month.Year or ... if error (nan or null or else)
        try:
            start_date = output['Дата начала'].strftime('%d.%m.%Y')
        except:
            start_date = "..."
        try:
            end_date = output['Дата окончания'].strftime('%d.%m.%Y')
        except:
            end_date = "..."
        # Company name, project name and grade
        # st.subheader(output['Название проекта'])
        st.markdown(f"<hr style='height:0.1rem;'/>", unsafe_allow_html=True)
        left, center, right = st.columns([1,2,1])
        with left:
            st.markdown(f"<i><p style='text-align: left;'>{output['Название компании']}<br>{output['Тип компании']}</p></i>", unsafe_allow_html=True)
        with center:
            st.markdown(f"<h2 style='text-align: center;'>{output['Название проекта']}</h2>", unsafe_allow_html=True)
        with right:
            st.markdown(f"<i><p style='text-align: right;'>{output['Микро-направление']}<br>{output['Грейд']}</p></i>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{start_date} — {end_date}<br>{output['Статус']}</p>", unsafe_allow_html=True)
        st.markdown(f"<hr style='height:0.1rem;'/>", unsafe_allow_html=True)
        # Project goals and result
        with st.container():
            left, right = st.columns(2)
            with left:
                # with st.expander('Задача проекта', True):
                st.markdown('**Поставленная задача**')
                res = output['Описание']
                if res != '':
                    st.caption(res)
                else:
                    st.warning('Данных нет, но вы держитесь...')
            with right:
                # with st.expander('Результат проекта', True):
                st.markdown('**Достижения**')
                res = output['Результат']
                if res != '':
                    st.caption(res)
                else:
                    st.warning('Данных нет, но вы держитесь...')
        # Project team and affiliated ppl
        with st.container():
            left, right = st.columns(2)
            with left:
                # Managers
                managers = output['Модераторы']
                st.markdown(f'**Модераторы проекта** ({len(managers) if type(managers) != float else 0} чел.)')
                if type(managers) != list:
                    st.warning('Данных нет, но вы держитесь...')
                else:
                    for i in managers:
                        st.text(i)
                
                # Curators
                curators = output['Кураторы']
                st.markdown(f'**Кураторы проекта** ({len(curators) if type(curators) != float else 0} чел.)')
                if type(curators) != list:
                    st.warning('Данных нет, но вы держитесь...')
                else:
                    for i in curators:
                        st.text(i)
                
                # Teachers
                teachers = output['Преподаватели']
                st.markdown(f'**Курирующие преподаватели** ({len(teachers) if type(teachers) != float else 0} чел.)')
                if type(teachers) != list:
                    st.warning('Данных нет, но вы держитесь...')
                else:
                    for i in teachers:
                        st.text(i)
            with right:
                students_in_project = students_in_all_projects.loc[(students_in_all_projects['ID проекта'] == project_id)&(students_in_all_projects['Куратор'] == 0)&(students_in_all_projects['Модератор'] == 0)]
                unique_groups_idx = students_in_project['Команда'].unique()
                st.markdown(f'**Участники проекта** ({students_in_project.shape[0]} чел.)')
                if len(unique_groups_idx) > 0:
                    group_counter = 0
                    for group_idx in unique_groups_idx:
                        students_in_the_group   = students_in_project[students_in_project['Команда'] == group_idx]
                        st.caption(f'🧑‍🎓 Проектная команда {group_counter+1} ({students_in_the_group.shape[0]} чел.)')
                        for i in students_in_the_group[['ФИО студента']].values:
                            st.text(i[0]) 
                        group_counter += 1
                else:
                    st.warning('Данных нет, но вы держитесь...')
        # st.download_button('💾 PDF', data=utils.project_to_pdf(output), file_name=f"{output['Название проекта']}.pdf", mime="application/pdf",)

if __name__ == "__main__":
    utils.page_config(layout='wide', title='Поиск проектов', page_icon=':bar_chart:')
    utils.load_local_css('css/project.css')
    utils.remove_footer()
    utils.set_logo()
    run()