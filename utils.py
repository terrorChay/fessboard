import streamlit as st
from connectdb import mysql_conn
import pandas as pd
from my_query import query_dict
from fpdf import FPDF
from datetime import date
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
@st.cache_data(ttl=10800, show_spinner=False)
def query_data(query):
    with mysql_conn() as conn:
        df = pd.read_sql(query, conn)
    return df

@st.cache_data(ttl=10800, show_spinner=False)
def load_students():
    return query_data(query_dict['students']).sort_values(by=['ФИО студента'])

@st.cache_data(ttl=10800, show_spinner=False)
def load_companies():
    df = query_data(query_dict['companies'])
    return df

@st.cache_data(ttl=10800, show_spinner=False)
def load_students_in_projects():
    df = query_data(query_dict['students_in_projects'])
    df.dropna(axis=0, subset=['Команда', 'ID студента'], inplace=True)
    df['ID студента'] = df['ID студента'].astype(int)
    df['ID проекта'] = df['ID проекта'].astype(int)
    return df.dropna(subset=['Курс в моменте'])

# @st.cache_data(show_spinner=False)
# def load_students_in_project(project_id):
#     df = query_data(query_dict['students_in_projects']).merge(query_data(query_dict['students']), on='ID студента', how='left')
#     df.dropna(axis=0, subset=['Команда', 'ID студента'], inplace=True)
#     df = df.loc[df['ID проекта'] == project_id]
#     return df

@st.cache_data(ttl=10800, show_spinner=False)
def load_teachers_in_projects():
    return query_data(query_dict['teachers_in_projects'])

@st.cache_data(ttl=10800, show_spinner=False)
def load_students_in_events():
    return query_data(query_dict['students_in_events'])

@st.cache_data(ttl=10800, show_spinner=False)
def load_events():
    return query_data(query_dict['events'])

@st.cache_data(ttl=10800, show_spinner=False)
def load_universities():
    return query_data(query_dict['universities'])

@st.cache_data(ttl=10800, show_spinner=False)
def load_fields():
    return query_data(query_dict['project_fields'])

# Load projects dataset
@st.cache_data(ttl=10800, show_spinner=False)
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

####################################################################################################################################
#                                                        PDF GENRATION AND DOWNLOAD
####################################################################################################################################

class FESSBoard_PDF(FPDF):
    def header(self):
        # Setting font
        self.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
        self.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf", uni=True)
        self.set_font("DejaVu", "", 12)
        # Rendering logo:
        self.image("https://github.com/terrorChay/FESSBoard/blob/master/img/logo_dark.png?raw=true", 10, 8, w=self.epw/3)
        # Printing date
        self.cell(0, align="R", txt=date.today().strftime("%d/%m/%Y"), ln=1)
        # Performing a line break
        self.ln(20)
    
    def footer(self):
        self.set_y(-10)
        self.set_font("DejaVu", "", 8)
        self.cell(w=self.epw, txt="Информационно-аналитическая система FESSBoard", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(w=self.epw, txt="ФЭСН, РАНХиГС", align="C")

def student_to_pdf(student_info, projects_summary, projects_summary_df):
    pdf = FESSBoard_PDF(orientation="P", unit="mm", format="Legal")
    pdf.add_page()
    # Student name
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(txt=student_info['ФИО студента'].values[0], new_x="LMARGIN", new_y="NEXT")
    # Padding
    pdf.cell(0, 8, new_x="LMARGIN", new_y="NEXT")
    # Student university
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(None, 5, txt="Университет: ")
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(None, 5, txt=student_info['ВУЗ'].values[0], new_x="LMARGIN", new_y="NEXT")
    # Student faculty
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(None, 5, txt="Курс: ")
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(None, 5, txt=f"{student_info['Курс'].values[0]}, {student_info['Программа'].values[0]}", new_x="LMARGIN", new_y="NEXT")
    # Student year
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(None, 5, txt="Поток: ")
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(None, 5, txt=student_info['Поток'].values[0], new_x="LMARGIN", new_y="NEXT")
    # Padding
    pdf.cell(0, 8, new_x="LMARGIN", new_y="NEXT")
    # Projects summary
    for key, value in projects_summary.items():
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(None, 5, txt=f"{key}: ")
        pdf.set_font("DejaVu", "", 12)
        pdf.cell(None, 5, txt=str(value), new_x="LMARGIN", new_y="NEXT")
    # Padding
    pdf.cell(0, 8, new_x="LMARGIN", new_y="NEXT")
    # Projects data
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(txt="Портфолио проектов", new_x="LMARGIN", new_y="NEXT")
    ## Padding
    pdf.cell(0, 8, new_x="LMARGIN", new_y="NEXT")
    ## Projects as teammate
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(None, 8, txt="В роли участника", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 12)
    for idx, row in projects_summary_df.loc[(projects_summary_df['Куратор'] == 0) & (projects_summary_df['Модератор'] == 0)].iterrows():
        pdf.cell(pdf.epw*0.05, 8, txt=f"{idx})")
        project_name = f"{row['Название проекта'][:30]}..." if len(row['Название проекта']) >= 30 else row['Название проекта']
        pdf.cell(pdf.epw*0.45, 8, txt=project_name)
        pdf.cell(pdf.epw*0.4, 8, txt=row['Микро-направление'])
        pdf.cell(pdf.epw*0.1, 8, txt=row['Грейд'], new_x="LMARGIN", new_y="NEXT")

    ## Curator
    k = projects_summary_df.loc[projects_summary_df['Куратор'] == 1]
    if k.shape[0] > 0:
        ## Padding
        pdf.cell(0, 8, new_x="LMARGIN", new_y="NEXT")
        ## Projects as curator
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(None, 8, txt="В роли куратора", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "", 12)
        for idx, row in k.iterrows():
            pdf.cell(pdf.epw*0.05, 8, txt=f"{idx})")
            project_name = f"{row['Название проекта'][:30]}..." if len(row['Название проекта']) >= 30 else row['Название проекта']
            pdf.cell(pdf.epw*0.45, 8, txt=project_name)
            pdf.cell(pdf.epw*0.4, 8, txt=row['Микро-направление'])
            pdf.cell(pdf.epw*0.1, 8, txt=row['Грейд'], new_x="LMARGIN", new_y="NEXT")

    ## Moderator
    j = projects_summary_df.loc[projects_summary_df['Модератор'] == 1]
    if j.shape[0] > 0:
        ## Padding
        pdf.cell(0, 8, new_x="LMARGIN", new_y="NEXT")
        ## Projects as curator
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(None, 8, txt="В роли куратора", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "", 12)
        for idx, row in j.iterrows():
            pdf.cell(pdf.epw*0.05, 8, txt=f"{idx})")
            project_name = f"{row['Название проекта'][:30]}..." if len(row['Название проекта']) >= 30 else row['Название проекта']
            pdf.cell(pdf.epw*0.45, 8, txt=project_name)
            pdf.cell(pdf.epw*0.4, 8, txt=row['Микро-направление'])
            pdf.cell(pdf.epw*0.1, 8, txt=row['Грейд'], new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())