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
def set_logo(dark=False):
    if dark:
        logo_url = 'https://github.com/terrorChay/FESSBoard/blob/master/img/logo_dark.png?raw=true'
    else:
        logo_url = 'https://github.com/terrorChay/FESSBoard/blob/master/img/logo_light.png?raw=true'

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
@st.experimental_memo(ttl=600, show_spinner=False)
def query_data(query):
    with mysql_conn() as conn:
        df = pd.read_sql(query, conn)
    return df

# Load projects dataset
@st.experimental_memo(show_spinner=False)
def load_projects():
    # Load data from database
    projects_df = query_data(query_dict['projects'])
    managers_df = query_data(query_dict['managers_in_projects']).merge(query_data(query_dict['students']), on='ID студента', how='left')
    teachers_df = query_data(query_dict['teachers_in_projects']).merge(query_data(query_dict['teachers']), on='ID преподавателя', how='left')

    # Join multiple managers and teachers into list values
    managers_df = managers_df.groupby(['ID проекта'])['ФИО студента'].apply(list).reset_index()
    teachers_df = teachers_df.groupby(['ID проекта'])['ФИО преподавателя'].apply(list).reset_index()

    # Left join dataframes to create consolidated one
    projects_df = projects_df.merge(managers_df, on='ID проекта', how='left')
    projects_df = projects_df.merge(teachers_df, on='ID проекта', how='left')

    # Set project ID as dataframe index
    # projects_df.set_index('ID проекта', drop=True, inplace=True)
    projects_df.rename(columns={'ФИО студента':'Менеджеры', 'ФИО преподавателя':'Преподаватели'}, inplace=True)
    return projects_df

@st.experimental_memo(show_spinner=False)
def load_students():
    return query_data(query_dict['students'])

@st.experimental_memo(show_spinner=False)
def load_universities():
    return query_data(query_dict['universities'])

@st.experimental_memo(show_spinner=False)
def load_companies():
    df = query_data(query_dict['companies'])
    return df

@st.experimental_memo(show_spinner=False)
def load_students_in_projects(all=True, selected_projects: list = False):
    df = query_data(query_dict['students_in_projects']).merge(query_data(query_dict['students']), on='ID студента', how='left')
    if selected_projects:
        df = df.loc[df['ID проекта'].isin(selected_projects)]
    return df

@st.experimental_memo(show_spinner=False)
def load_students_in_project(project_id):
    df = query_data(query_dict['students_in_projects']).merge(query_data(query_dict['students']), on='ID студента', how='left')
    df.dropna(axis=0, subset=['Команда', 'ID студента'], inplace=True)
    df = df.loc[df['ID проекта'] == project_id]
    return df

@st.experimental_memo(show_spinner=False)
def load_people_in_projects(teachers=False):
    if teachers:
        a = 'teachers_in_projects'
        b = 'teachers'
        c = 'ID преподавателя'
    else:
        a = 'students_in_projects'
        b = 'students'
        c = 'ID студента'  
    df = query_data(query_dict[a]).merge(query_data(query_dict[b]), on=c, how='left')
    return df
    
####################################################################################################################################
#                                                        DATAFRAME DOWNLOAD UTILS
####################################################################################################################################

@st.experimental_memo(show_spinner=False)
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