import streamlit as st
import utils as utils
from my_query import query_dict
import pandas as pd
import re
from io import BytesIO
# from pyxlsb import open_workbook as open_xlsb
# import xlsxwriter
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import plotly.express as px

# Apply filters and return filtered dataset
def filter_dataframe(df: pd.DataFrame, cols_to_ignore=[]) -> pd.DataFrame:
    st.sidebar.write('Выводить столбцы')
    cols_in_df      = df.columns.values
    cols_dict       = {}
    for col_name in cols_in_df:
        cols_dict[col_name] = st.sidebar.checkbox(col_name, True, key=f"display_{col_name}")
    cols_to_display = [k for k, v in cols_dict.items() if v]
    df = df[cols_to_display].copy()
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
        to_filter_columns = st.multiselect("Параметры фильтрации", cols, key='select_filters')
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("└")
            # if any(map(df[column].name.__contains__, ['Модераторы', 'Преподаватели', 'Кураторы', 'Университеты'])):
            #     options = pd.Series([x for _list in df[column][df[column].notna()] for x in _list]).unique()
            #     user_cat_input = right.multiselect(
            #         f"{column}",
            #         options,
            #     )
            #     if user_cat_input:
            #         df = df[df[column].astype(str).str.contains('|'.join(user_cat_input))]
            # el
            if is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = 1.00
                user_num_input = right.slider(
                    f" {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                _min = df[column].min()
                _max = df[column].max()
                user_date_input = right.date_input(
                    f" {column}",
                    value=(
                        _min,
                        _max,
                    ),
                    max_value=_max,
                    min_value=_min,
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            elif is_categorical_dtype(df[column]) or any(map(df[column].name.__contains__, ['Курс', 'Поток', 'ВУЗ', 'Регион', 'Программа'])):
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
                    f"{column} содержит",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input, na=False, flags=re.IGNORECASE)]
    # Try to convert datetimes into displayable date formats
    for col in df.columns:
        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%d-%m-%Y')
    return df

def agg_students(students_df: pd.DataFrame, students_in_projects_df: pd.DataFrame):
    students = students_df.copy()
    participations = students_in_projects_df[['ID студента', 'Куратор', 'Модератор', 'Академический год']].copy()
    # date limitation on projects
    options = sorted(participations['Академический год'].unique())
    user_cat_input = st.multiselect(
        f"Учитывать проекты за периоды",
        options,
        default=options,
    )
    if user_cat_input:
        _cat_input = user_cat_input
        participations = participations[participations['Академический год'].isin(_cat_input)]
    #
    df_k = participations.groupby(['ID студента']).agg({'Куратор':'sum', 'Модератор':'sum'}).reset_index().rename(columns ={'Куратор':'Курировал (раз)', 'Модератор':'Модерировал (раз)'})
    df_j = participations.loc[(participations['Куратор'] == 0) & (participations['Модератор'] == 0)].value_counts('ID студента').reset_index().rename(columns ={0:'Участвовал (раз)'})
    agg_df = df_k.merge(df_j, how='inner', on='ID студента')
    agg_df = students.merge(agg_df, how='left', on='ID студента').fillna(0)
    return agg_df

# App launch
def run():
    # Load dataframe
    with st.spinner('Изучаем ведомости...'):
        students_in_projects_df = utils.load_students_in_projects()
    with st.spinner('Задействуем нетворкинг...'):
        students_df             = utils.load_students()
    st.title('Поиск студентов')
    st.write('''
            #### На данной странице можно составить выборку студентов по заданным параметрам!
            :art: __Параметры фильтрации__ выводят студентов, которые удовлетворяют заданным параметрам.\n
            :floppy_disk: Вы также можете скачать составленную выборку в формате Microsoft Excel.
            ''')
    # draw criteria filters and return filtered df
    students_pivot_df = agg_students(students_df, students_in_projects_df)
    df_filters_applied  = filter_dataframe(students_pivot_df)
    # if filters have results -> draw DF, download btn and analytics
    if 0 not in df_filters_applied.shape:
        tab1, tab2 = st.tabs(["Данные", "Аналитика"])
        with tab1:
            st.dataframe(df_filters_applied)
            col1, col2, _col3, _col4, _col5, _col6 = st.columns(6)
            col1.download_button('💾 CSV', data=utils.convert_df(students_pivot_df), file_name="fessboard_students_slice.csv", mime='text/csv', use_container_width=True)
            col2.download_button('💾 Excel', data=utils.convert_df(students_pivot_df, True), file_name="fessboard_students_slice.xlsx", use_container_width=True)
        with tab2:
            st.write('какая-то аналитика')
    else:
        # Technically only possible with long string criteria filters cuz they allow for any string input
        st.warning('Студенты не найдены')

if __name__ == "__main__":
    utils.page_config(layout='wide', title='Поиск проектов')
    utils.remove_footer()
    utils.set_logo()
    run()