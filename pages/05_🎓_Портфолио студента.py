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
    with st.spinner('Принимаем сигналы из космоса...'):
        students_in_projects_df = utils.load_students_in_projects()
    with st.spinner('Еще чуть-чуть и прямо в рай...'):
        students_df             = utils.load_students()
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

    st.title('Портфолио студента')
    st.write('''
            #### На данной странице можно ознакомиться с портфелем проектов выбранного студента!
            :mag: У коровы нет других забот  
            :art: Ест траву  
            :male-student: И молоко дает\n

            :floppy_disk: ыы
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
    utils.page_config(layout='wide', title='Портфолио компании')
    utils.remove_footer()
    utils.set_logo()
    run()