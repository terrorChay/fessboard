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
            if is_numeric_dtype(df[column]):
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
            # use selectbox for instances where there are < 10 unique vals or where max len option is < 255
            elif is_categorical_dtype(df[column]) or df[column].nunique() < 10 or df[column].map(len).max() < 255:
                options = df[column].unique()
                user_cat_input = right.multiselect(
                    f"{column}",
                    options
                )
                if user_cat_input == []:
                    _cat_input = df[column].unique()
                else:
                    _cat_input = user_cat_input
                df = df[df[column].isin(_cat_input)]
            else:
                user_text_input = right.text_input(
                    f"{column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df

# Apply filters and return company name
def project_selection(df: pd.DataFrame):
    df = df[['ID проекта', 'Название проекта', 'Название компании', 'Грейд', 'Статус', 'Макро-направление', 'Микро-направление']].sort_values(by='ID проекта', ascending=False).copy()
    df.insert(0, 'Составной ключ', df['ID проекта'].astype('str') + ' - ' + df['Название проекта'])
    selected_project = False

    modification_container = st.container()
    with modification_container:
        col01, col02, col03 = st.columns(3)
        cols_list = [col01, col02, col03]
        # Filters for project selection
        ## df.columns[3:] so that the composite key, project id and project name are ignored
        for idx, column in enumerate(df.columns[3:]):
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

        # Household name selection
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
            #### На данной странице можно ознакомиться со всей информацией по выбранному проекту!
            ''')
    # user input
    selected_project = project_selection(projects_df)
    # Draw search filters and return filtered df
    if not selected_project:
        st.markdown(f"<h4 style='text-align: center;'>Выберите проект 😎</h4>", unsafe_allow_html=True)
    else:
        project_id = int(selected_project[:5].split(' - ')[0])
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
        st.markdown(f"<hr style='height:0.1rem; opacity: 0'/>", unsafe_allow_html=True)
        with st.container():
            left, right = st.columns(2)
            with left:
                # Managers
                st.markdown('**Модераторы проекта**')
                managers = output['Модераторы']
                if type(managers) != list:
                    st.warning('Данных нет, но вы держитесь...')
                else:
                    for i in managers:
                        st.text(f'🧑‍💼 {i}')
                
                # Curators
                st.markdown('**Кураторы проекта**')
                curators = output['Кураторы']
                if type(curators) != list:
                    st.warning('Данных нет, но вы держитесь...')
                else:
                    for i in managers:
                        st.text(f'🧑‍💼 {i}')
                
                # Teachers
                st.markdown('**Курирующие преподаватели**')
                teachers = output['Преподаватели']
                if type(teachers) != list:
                    st.warning('Данных нет, но вы держитесь...')
                else:
                    for i in teachers:
                        st.text(f'🧑‍🏫 {i}')
            with right:
                students_in_project = students_in_all_projects.loc[students_in_all_projects['ID проекта'] == project_id]
                unique_groups_idx = students_in_project['Команда'].unique()
                st.markdown('**Участники проекта**')
                if len(unique_groups_idx) > 0:
                    group_counter = 0
                    for group_idx in unique_groups_idx:
                        st.caption(f'Проектная команда {group_counter+1}')
                        students_in_the_group   = students_in_project[students_in_project['Команда'] == group_idx]
                        for i in students_in_the_group[['ФИО студента']].values:
                            st.text(f'🧑‍🎓 {i[0]}') 
                        group_counter += 1
                else:
                    st.warning('Данных нет, но вы держитесь...')


if __name__ == "__main__":
    utils.page_config(layout='wide', title='Поиск проектов')
    utils.load_local_css('css/project.css')
    utils.remove_footer()
    utils.set_logo()
    run()