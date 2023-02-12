import streamlit as st
from connectdb import mysql_conn
import pandas as pd
from my_query import query_dict
from io import BytesIO

####################################################################################################################################
#                                                         STREAMLIT SETUP UTILS
####################################################################################################################################

# set page layout
def page_config(title, layout='wide'):
    try:
        st.set_page_config(layout=layout, page_title=title)
    except st.errors.StreamlitAPIException as e:
        if "can only be called once per app" in e.__str__():
            return
        raise e

# load css with local source
def load_local_css(file_name):
    try: # Local launch
        with open(f'/app/fessboard/{file_name}', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError: # Streamlit Cloud
        with open(f'{file_name}', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# remove streamlit logo footer
def remove_footer():
    st.markdown('''
                <style>
                footer {
                    visibility: hidden;
                }
                </style>
                ''', unsafe_allow_html=True)

# remove table indice col
def remove_table_indice():
    st.markdown("""
                <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
                </style>
                """, unsafe_allow_html=True)

# set logo
def set_logo():
    logo_url = 'https://github.com/terrorChay/FESSBoard/blob/master/img/logo_dark.png?raw=true'
    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url({logo_url});
                background-size: 200px;
                background-repeat: no-repeat;
                background-position: 20px 50px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# load css with external source
def load_remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)

# set material ui icon
def set_MU_icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)

####################################################################################################################################
#                                                            DATABASE QUERIES
####################################################################################################################################

# Database Query
@st.cache_data(ttl=600, show_spinner=False)
def query_data(query):
    with mysql_conn() as conn:
        df = pd.read_sql(query, conn)
    return df

@st.cache_data(show_spinner=False)
def load_students():
    return query_data(query_dict['students']).sort_values(by=['ФИО студента'])

@st.cache_data(show_spinner=False)
def load_companies():
    df = query_data(query_dict['companies'])
    return df

@st.cache_data(show_spinner=False)
def load_students_in_projects():
    df = query_data(query_dict['students_in_projects'])
    df.dropna(axis=0, subset=['Команда', 'ID студента'], inplace=True)
    df['ID студента'] = df['ID студента'].astype(int)
    df['ID проекта'] = df['ID проекта'].astype(int)
    return df

# @st.cache_data(show_spinner=False)
# def load_students_in_project(project_id):
#     df = query_data(query_dict['students_in_projects']).merge(query_data(query_dict['students']), on='ID студента', how='left')
#     df.dropna(axis=0, subset=['Команда', 'ID студента'], inplace=True)
#     df = df.loc[df['ID проекта'] == project_id]
#     return df

@st.cache_data(show_spinner=False)
def load_teachers_in_projects():
    return query_data(query_dict['teachers_in_projects'])

@st.cache_data(show_spinner=False)
def load_students_in_events():
    return query_data(query_dict['students_in_events'])

@st.cache_data(show_spinner=False)
def load_events():
    return query_data(query_dict['events'])

@st.cache_data(show_spinner=False)
def load_universities():
    return query_data(query_dict['universities'])

@st.cache_data(show_spinner=False)
def load_fields():
    return query_data(query_dict['project_fields'])

# Load projects dataset
@st.cache_data(show_spinner=False)
def load_projects():
    # Load projects
    projects_df = query_data(query_dict['projects'])

    # Load people
    students_df = load_students_in_projects()
    moderators_df = students_df.loc[students_df['Модератор'] == 1]
    curators_df = students_df.loc[students_df['Куратор'] == 1]
    teachers_df = load_teachers_in_projects()

    # Join multiple managers and teachers into list values
    moderators_df = moderators_df.groupby(['ID проекта'])['ФИО студента'].apply(list).reset_index().rename(columns={'ФИО студента':'Модераторы'})
    curators_df = curators_df.groupby(['ID проекта'])['ФИО студента'].apply(list).reset_index().rename(columns={'ФИО студента':'Кураторы'})
    teachers_df = teachers_df.groupby(['ID проекта'])['ФИО преподавателя'].apply(list).reset_index().rename(columns={'ФИО преподавателя':'Преподаватели'})

    # Left join dataframes to create consolidated one
    projects_df = projects_df.merge(moderators_df, on='ID проекта', how='left')
    projects_df = projects_df.merge(curators_df, on='ID проекта', how='left')
    projects_df = projects_df.merge(teachers_df, on='ID проекта', how='left')

    return projects_df
####################################################################################################################################
#                                                        DATAFRAME DOWNLOAD UTILS
####################################################################################################################################

@st.cache_data(show_spinner=False)
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