import streamlit as st
from streamlit import session_state as session
# import streamlit_setup as setup
import utils as utils
import pandas as pd
import numpy as np
import re
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import xlsxwriter
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import plotly.express as px
from connectdb import mysql_conn
from datetime import date

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


 # Database Query
@st.experimental_memo(ttl=600)
def query_data(query):
    with mysql_conn() as conn:
        df = pd.read_sql(query, conn)
    return df

# Load projects dataset
@st.experimental_memo
def load_projects():
    query   =   """
                SELECT
                    projects.project_id 'ID',
                    companies.company_name 'Заказчик',
                    company_types.company_type 'Тип компании',
                    projects.project_name 'Название',
                    projects.project_description 'Описание',
                    projects.project_result 'Результат',
                    projects.project_start_date 'Дата начала',
                    projects.project_end_date 'Дата окончания',
                    project_grades.grade 'Грейд',
                    project_fields.field 'Направление',
                    projects.is_frozen 'Заморожен'
                FROM projects 
                LEFT JOIN project_grades
                    ON projects.project_grade   = project_grades.grade_id
                LEFT JOIN project_fields
                    ON projects.project_field   = project_fields.field_id
                LEFT JOIN (companies
                            LEFT JOIN company_types
                                ON companies.company_type = company_types.company_type_id)
                    ON projects.project_company = companies.company_id;
                """
    projects_df = query_data(query)
    projects_df['Дата окончания']   = pd.to_datetime(projects_df['Дата окончания'], format='%Y-%m-%d')
    projects_df['Дата начала']      = pd.to_datetime(projects_df['Дата начала'], format='%Y-%m-%d')
    projects_df['ID']               = pd.to_numeric(projects_df['ID'])
    return projects_df

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

@st.experimental_memo
def convert_df(df: pd.DataFrame, to_excel=False):
    if to_excel:
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='FESSBoard')
        workbook = writer.book
        worksheet = writer.sheets['FESSBoard']
        format1 = workbook.add_format({'num_format': '0.00'}) 
        worksheet.set_column('A:A', None, format1)  
        workbook.close()
        processed_data = output.getvalue()
    else:
        processed_data = df.to_csv().encode('utf-8')
    return processed_data

# App launch
def run():
    # Load dataframe
    # projects_df = load_projects()
    st.title('Карточка студента')
    st.write('''
            #### На данной странице можно ознакомиться со всей информацией по выбранному студенту!
            ''')
    # Draw search filters and return filtered df
    st.error('В разработке...')
    with st.container():
        col1, col2 = st.columns([1,2])
        with col1:
            with st.container():
                st.markdown('**Распределение проектов студента по макронаправлениям**')
                data = {'sphere' : ['HR','Data Science','Management','Marketing','Development','Design','Banking&Finance'],
            'number' : [1,2,1,2,1,0,0]}
                df = pd.DataFrame(data)
                fig = px.line_polar(df,r='number',theta='sphere',line_close=True,color_discrete_sequence=colors)
                fig.update_traces(fill='toself',mode='lines+markers',cliponaxis=False)
                fig.update_layout(
                    font_family=font,
                    font_size = 10,
                    paper_bgcolor=tr,
                    plot_bgcolor = tr,
                    height = 320,
                    yaxis_visible   = False,)
                st.plotly_chart(fig,use_container_width=True,config={'staticPlot': False,'displayModeBar': False})   

if __name__ == "__main__":
    utils.page_config(layout='centered', title='Поиск проектов')
    utils.remove_footer()
    run()