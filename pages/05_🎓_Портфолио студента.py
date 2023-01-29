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
    df = df[['ID студента', 'ФИО студента']].copy().dropna().drop_duplicates()
    df.insert(0, 'Составной ключ', df['ID студента'].astype('str') + ' - ' + df['ФИО студента'])
    student_id = False
    selected_student = st.selectbox(label='Студент', options=df['Составной ключ'])
    if selected_student:
        student_id = int(selected_student.split(' - ')[0])

    return student_id


# App launch
def run():
    # Load data
    with st.spinner('Масштабируем Agile...'):
        projects_df             = utils.load_projects()
    with st.spinner('Принимаем сигналы из космоса...'):
        students_in_projects_df = utils.load_students_in_projects()
    with st.spinner('Еще чуть-чуть и прямо в рай...'):
        students_df             = utils.load_students()

    st.title('Портфолио студента')
    st.write('''
            #### На данной странице можно ознакомиться с портфелем проектов выбранного студента!
            ''')

    student_id = select_student(students_df)
    if student_id:
        projects_with_student_df = students_in_projects_df.loc[students_in_projects_df['ID студента'] == student_id]
        if projects_with_student_df.shape[0] > 0:
            tab1, tab2 = st.tabs(['Участник', 'Куратор'])
            # Display projects 
            regular_ids = projects_with_student_df.loc[projects_with_student_df['Куратор'] == 0]['ID проекта']
            if regular_ids.shape[0] > 0:
                regular_projects_df = projects_df.loc[projects_df['ID проекта'].isin(regular_ids)]
                tab1.dataframe(regular_projects_df)
            # Display curated projects
            curated_ids = projects_with_student_df.loc[projects_with_student_df['Куратор'] == 1]['ID проекта']
            if curated_ids.shape[0] > 0:
                curated_projects_df = projects_df.loc[projects_df['ID проекта'].isin(curated_ids)]
                tab2.dataframe(curated_projects_df)
        else:
            st.warning('Проекты не найдены')
    else:
        st.markdown(f"<h4 style='text-align: center;'>Выберите студента 😎</h4>", unsafe_allow_html=True)
    
if __name__ == "__main__":
    utils.page_config(layout='centered', title='Портфолио компании')
    utils.remove_footer()
    utils.set_logo()
    run()