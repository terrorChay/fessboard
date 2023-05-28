import streamlit as st
import utils as utils
from my_query import query_dict
import pandas as pd
import re
from io import BytesIO
# from pyxlsb import open_workbook as open_xlsb
# import xlsxwriter
from pandas.api.types import (
    is_bool_dtype,
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_list_like,
)
import plotly.express as px

# Apply search filters and return filtered dataset
def search_dataframe(df: pd.DataFrame, key="default") -> pd.DataFrame:

    df = df.copy()

    user_text_input = st.text_input(f"Поиск", placeholder='Введите текст', help='Укажите текст, который могут содержать интересующие Вас данные', key=f"{key}_searchfield")

    if user_text_input:
        _user_text_input = "".join([char for char in user_text_input if char.isalnum()])
        mask = df.apply(lambda x: x.astype(str).str.contains(_user_text_input, na=False, flags=re.IGNORECASE))
        df = df.loc[mask.any(axis=1)]

    return df

# TEST PENTAGON DANGER ZONE
def filter_df(df: pd.DataFrame, key="default", force_multiselect=[]) -> pd.DataFrame:
    # Copy df
    df = df.convert_dtypes().copy()
    # Чекбоксы столбцов на панели слева
    cols_in_df = df.columns.values
    with st.sidebar.expander(label=f'Столбцы {key}'):
        cols_dict = {}
        for col_name in cols_in_df:
            cols_dict[col_name] = st.checkbox(col_name, True, key=f"{key}_display_{col_name}")
    # Копируем датафрейм в переменную
    cols_to_display = [k for k, v in cols_dict.items() if v]
    df = df[cols_to_display]
    # Конвертируем в дату
    for col in df.columns:
        if 'дата' in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass
    # Контейнер фильтров
    modification_container = st.container()
    with modification_container:
        columns_to_filter = st.multiselect("Параметры фильтрации", cols_to_display, key=f'{key}_select_filters')
        for column in columns_to_filter:
            left, right = st.columns((1, 20))
            left.write("└")
            # Multiselect for lists
            if is_object_dtype(df[column]):
                select_col, operator_col = right.columns([8,2])
                options = pd.Series([x for _list in df[column][df[column].notna()] for x in _list]).unique()
                # input
                user_cat_input = select_col.multiselect(
                    f"{column}",
                    options,
                    key=f'{key}_{column}_input',
                )
                operator_to_use = operator_col.selectbox(
                    "Оператор",
                    ['или', 'и'],
                    key=f'{key}_{column}_operator',
                    label_visibility="hidden",
                )
                if user_cat_input:
                    if operator_to_use == 'или':
                        expr_str    = '|'.join([re.escape(m) for m in user_cat_input])
                    else:
                        base        = r'^{}'
                        expr        = '(?=.*{})'
                        expr_str    = base.format(''.join(expr.format(w) for w in [re.escape(m) for m in user_cat_input]))
                    df = df[df[column].astype(str).str.contains(expr_str)]
            # Multiselect Box
            elif any(map(df[column].name.__contains__, force_multiselect)):
                options = sorted(df[column].unique())
                # input
                user_cat_input = right.multiselect(
                    f"{column}",
                    options,
                    key=f'{key}_{column}_input',
                )
                if user_cat_input:
                    _cat_input = user_cat_input
                    df = df[df[column].isin(_cat_input)]
            # Slider
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = 1.00
                # input
                user_num_input = right.slider(
                    f" {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                    key=f'{key}_{column}_input',
                )
                df = df[df[column].between(*user_num_input)]
            # Dates
            elif is_datetime64_any_dtype(df[column]):
                _min = df[column].min()
                _max = df[column].max()
                # input
                user_date_input = right.date_input(
                    f" {column}",
                    value=(
                        _min,
                        _max,
                    ),
                    max_value=_max,
                    min_value=_min,
                    key=f'{key}_{column}_input',
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            # Text input
            else:
                user_text_input = right.text_input(
                    f"{column} содержит",
                    key=f'{key}_{column}_input',
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input, na=False, flags=re.IGNORECASE)]
    # Try to convert datetimes into displayable date formats
    for col in df.columns:
        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.date
    # result
    df = df.reset_index(drop=True)
    st.caption(f'Найдено записей: {df.shape[0]}')
    return df

# Aggregate students' activity
def agg_students(students_df: pd.DataFrame, students_in_projects_df: pd.DataFrame):
    students = students_df.copy()
    participations = students_in_projects_df[['ID студента', 'Куратор', 'Модератор', 'Академический год']].copy()
    # date limitation on projects
    options = sorted(participations['Академический год'].unique())
    user_cat_input = st.multiselect(
        f"Периоды для подсчета проектов",
        options,
        default=options,
    )
    if user_cat_input:
        _cat_input = user_cat_input
        participations = participations[participations['Академический год'].isin(_cat_input)]
    #
    df_k = participations.groupby(['ID студента']).agg({'Куратор':'sum', 'Модератор':'sum'}).reset_index().rename(columns ={'Куратор':'Курировал (раз)', 'Модератор':'Модерировал (раз)'})
    df_j = participations.loc[(participations['Куратор'] == 0) & (participations['Модератор'] == 0)].value_counts('ID студента').reset_index().rename(columns ={0:'Участвовал (раз)'})
    agg_df = (df_k.merge(df_j, how='inner', on='ID студента'))
    agg_df = students.merge(agg_df, how='left', on='ID студента').fillna(0)
    agg_df['Всего проектов']        = agg_df['Курировал (раз)'] + agg_df['Модерировал (раз)'] + agg_df['Участвовал (раз)']
    agg_df['Опыт модератора'].loc[agg_df['Опыт модератора'] == 0] = "Нет"
    agg_df['Опыт модератора'].loc[agg_df['Опыт модератора'] == 1] = "Есть"
    agg_df['Опыт куратора'].loc[agg_df['Опыт куратора'] == 0] = "Нет"
    agg_df['Опыт куратора'].loc[agg_df['Опыт куратора'] == 1] = "Есть"
    agg_df['Отстранен'].loc[agg_df['Отстранен'] == 0] = "Нет"
    agg_df['Отстранен'].loc[agg_df['Отстранен'] == 1] = "Есть"
    return agg_df

# App launch
def run():
    # Load dataframe
    with st.spinner('Поднимаем тайные архивы...'):
        projects_df = utils.load_projects()
    with st.spinner('Посылаем сигналы в космос...'):
        events_df = utils.load_events()
    with st.spinner('Изучаем ведомости...'):
        students_in_projects_df = utils.load_students_in_projects()
    with st.spinner('Задействуем нетворкинг...'):
        students_df         = utils.load_students()
        students_df['Курс'] = students_df['Курс'] + ' ' + students_df['Программа']
        students_df.drop('Программа', inplace=True, axis=1)
    with st.spinner('Готовим отчетные формы'):
        projects_report_query_df = utils.load_projects_report_query()

    st.title('Умные выборки')
    st.write('''
            #### На данной странице можно составить выборку данных по заданным параметрам! 
            :mag: __Поиск__ позволяет составлять выборку по совпадениям с введенным текстом.  
            :art: __Параметры фильтрации__ позволяют выбирать конкретные критерии для составления выборки.\n
            :sunglasses: Поиск и фильтры можно использовать вместе!  
            :floppy_disk: Вы также можете скачать составленную выборку в формате Microsoft Excel.
            ''')
    tab1, tab2, tab3, tab4 = st.tabs(["Проекты", "Мероприятия", "Студенты", "Отчетная форма №1"])
    #PROJECTS
    with tab1:
        # Draw search filters and return filtered df
        df_search_applied   = search_dataframe(projects_df, key='tab1')
        # if search has results -> draw criteria filters and return filtered df
        if df_search_applied.shape[0]:
            df_filters_applied  = filter_df(df_search_applied, key='проектов', force_multiselect=['Название компании', 'направление', 'отрасль', 'Тип', 'Статус', 'Грейд', 'год', 'Отрасль'])
            # if filters have results -> draw DF, download btn and analytics
            if 0 not in df_filters_applied.shape:
                st.dataframe(df_filters_applied)
                col1, col2, _col3, _col4, _col5, _col6 = st.columns(6)
                col1.download_button('💾 CSV', data=utils.convert_df(df_filters_applied), file_name="fessboard_projects_slice.csv", mime='text/csv', use_container_width=True)
                col2.download_button('💾 Excel', data=utils.convert_df(df_filters_applied, True), file_name="fessboard_projects_slice.xlsx", use_container_width=True)
            else:
                # Technically only possible with long string criteria filters cuz they allow for any string input
                st.warning('Таких проектов пока нет')
        else:
            st.warning('Таких проектов пока нет')
    #EVENTS
    with tab2:
        # Draw search filters and return filtered df
        df_search_applied   = search_dataframe(events_df, key='tab2')
        # if search has results -> draw criteria filters and return filtered df
        if df_search_applied.shape[0]:
            df_filters_applied  = filter_df(df_search_applied, key='мероприятий', force_multiselect=['год', 'Регион', 'Статус'])
            # if filters have results -> draw DF, download btn and analytics
            if 0 not in df_filters_applied.shape:
                st.dataframe(df_filters_applied)
                col1, col2, _col3, _col4, _col5, _col6 = st.columns(6)
                col1.download_button('💾 CSV', data=utils.convert_df(df_filters_applied), file_name="fessboard_events_slice.csv", mime='text/csv', use_container_width=True)
                col2.download_button('💾 Excel', data=utils.convert_df(df_filters_applied, True), file_name="fessboard_events_slice.xlsx", use_container_width=True)
            else:
                # Technically only possible with long string criteria filters cuz they allow for any string input
                st.warning('Мероприятия не найдены')
        else:
            st.warning('Мероприятия не найдены')
    #STUDENTS
    with tab3:
        # Choose which projects (by year) to use in calculated columns
        students_pivot_df = agg_students(students_df, students_in_projects_df)
        # Draw search filters and return filtered df
        df_search_applied   = search_dataframe(students_pivot_df, 'tab3')
        # if search has results -> draw criteria filters and return filtered df
        if df_search_applied.shape[0]:
            df_filters_applied  = filter_df(df_search_applied, key='студентов', force_multiselect=['Курс', 'Поток', 'ВУЗ', 'Регион', 'Программа', 'Опыт', 'Отстранен'])
            # if filters have results -> draw DF, download btn and analytics
            if 0 not in df_filters_applied.shape:
                st.dataframe(df_filters_applied)
                col1, col2, _col3, _col4, _col5, _col6 = st.columns(6)
                col1.download_button('💾 CSV', data=utils.convert_df(df_filters_applied), file_name="fessboard_students_slice.csv", mime='text/csv', use_container_width=True)
                col2.download_button('💾 Excel', data=utils.convert_df(df_filters_applied, True), file_name="fessboard_students_slice.xlsx", use_container_width=True)
            else:
                # Technically only possible with long string criteria filters cuz they allow for any string input
                st.warning('Студенты не найдены')
        else:
            st.warning('Студенты не найдены')
    # ОФ №1
    with tab4:
        # Draw search filters and return filtered df
        df_search_applied   = search_dataframe(projects_report_query_df, 'tab4-1')
        # if search has results -> draw criteria filters and return filtered df
        if df_search_applied.shape[0]:
            df_filters_applied  = filter_df(df_search_applied, key='ОФ №1', force_multiselect=['Название проекта', 'Название компании', 'ФИО студента', 'ВУЗ', 'Курс', 'Академический год', 'Программа'])
            # if filters have results -> draw DF, download btn and analytics
            if 0 not in df_filters_applied.shape:
                st.info("""Поля **ВУЗ** и **Курс** содержат значения во время выполнения проекта, а не текущие!  
                        Поля **Куратор** и **Модератор** являются бинарными: 1 означает *Да*, 0 означает *Нет*.""")
                st.dataframe(df_filters_applied)
                col1, col2, _col3, _col4, _col5, _col6 = st.columns(6)
                col1.download_button('💾 CSV', data=utils.convert_df(df_filters_applied), file_name="fessboard_report.csv", mime='text/csv', use_container_width=True)
                col2.download_button('💾 Excel', data=utils.convert_df(df_filters_applied, True), file_name="fessboard_report.xlsx", use_container_width=True)
            else:
                # Technically only possible with long string criteria filters cuz they allow for any string input
                st.warning('Студенты не найдены')
        else:
            st.warning('Студенты не найдены')
if __name__ == "__main__":
    utils.page_config(layout='wide', title='Поиск проектов', page_icon=':bar_chart:')
    utils.remove_footer()
    utils.set_logo()
    run()