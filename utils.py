import streamlit as st
from connectdb import mysql_conn
import pandas as pd
from my_query import query_dict
from fpdf import FPDF
from datetime import date
from io import BytesIO
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

####################################################################################################################################
#                                                         STREAMLIT SETUP UTILS
####################################################################################################################################

# set page layout
def page_config(title, layout='wide', page_icon=None):
    try:
        st.set_page_config(layout=layout, page_title=title, page_icon=page_icon)
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
    logo_url = 'https://raw.githubusercontent.com/terrorChay/FESSBoard-images/main/logo/fessboard/logo_dark.png'
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

@st.cache_data(ttl=10800, show_spinner=False)
def load_projects_report_query():
    df = query_data(query_dict['projects_report_query'])
    df.dropna(axis=0, subset=['Команда', 'ID студента'], inplace=True)
    df['ID студента'] = df['ID студента'].astype(int)
    df['ID проекта'] = df['ID проекта'].astype(int)
    return df.dropna(subset=['Курс'])

@st.cache_data(ttl=10800, show_spinner=False)
def load_teachers_in_projects():
    return query_data(query_dict['teachers_in_projects'])

@st.cache_data(ttl=10800, show_spinner=False)
def load_teachers_in_events():
    return query_data(query_dict['teachers_in_events'])

@st.cache_data(ttl=10800, show_spinner=False)
def load_students_in_events():
    return query_data(query_dict['students_in_events'])

@st.cache_data(ttl=10800, show_spinner=False)
def load_events():
    # Load events
    events_df = query_data(query_dict['events'])

    # Load people
    students_df     = load_students_in_events()
    moderators_df   = students_df.loc[students_df['Модератор'] == 1]
    teachers_df     = load_teachers_in_events()
    universities_df = query_data(query_dict['universities_in_events'])

    # Join multiple managers and teachers into list values
    moderators_df   = moderators_df.groupby(['ID мероприятия'])['ФИО студента'].apply(list).reset_index().rename(columns={'ФИО студента':'Модераторы'})
    teachers_df     = teachers_df.groupby(['ID мероприятия'])['ФИО преподавателя'].apply(list).reset_index().rename(columns={'ФИО преподавателя':'Преподаватели'})
    universities_df = universities_df.groupby(['ID мероприятия'])['Университет'].apply(list).reset_index().rename(columns={'Университет':'Университеты'})

    # Left join dataframes to create consolidated one
    events_df = events_df.merge(moderators_df, on='ID мероприятия', how='left')
    events_df = events_df.merge(teachers_df, on='ID мероприятия', how='left')
    events_df = events_df.merge(universities_df, on= 'ID мероприятия', how='left')

    return events_df

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

    # Load people & universiies
    students_df         = load_students_in_projects()
    moderators_df       = students_df.loc[students_df['Модератор'] == 1]
    curators_df         = students_df.loc[students_df['Куратор'] == 1]
    teachers_df         = load_teachers_in_projects()
    universities_df     = query_data(query_dict['universities_in_projects'])

    # Join multiple managers and teachers into list values
    moderators_df   = moderators_df.groupby(['ID проекта'])['ФИО студента'].apply(list).reset_index().rename(columns={'ФИО студента':'Модераторы'})
    curators_df     = curators_df.groupby(['ID проекта'])['ФИО студента'].apply(list).reset_index().rename(columns={'ФИО студента':'Кураторы'})
    teachers_df     = teachers_df.groupby(['ID проекта'])['ФИО преподавателя'].apply(list).reset_index().rename(columns={'ФИО преподавателя':'Преподаватели'})
    universities_df = universities_df.groupby(['ID проекта'])['Университет'].apply(list).reset_index().rename(columns={'Университет':'Университеты'})

    # Left join dataframes to create consolidated one
    projects_df = projects_df.merge(moderators_df, on='ID проекта', how='left')
    projects_df = projects_df.merge(curators_df, on='ID проекта', how='left')
    projects_df = projects_df.merge(teachers_df, on='ID проекта', how='left')
    projects_df = projects_df.merge(universities_df, on= 'ID проекта', how='left')

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
        self.image("https://raw.githubusercontent.com/terrorChay/FESSBoard-images/main/logo/fessboard/logo_dark.png", 10, 8, w=self.epw/3)
        # Printing date
        self.cell(0, align="R", txt=date.today().strftime("%d/%m/%Y"), ln=1)
        # Performing a line break
        self.ln(20)
    
    def footer(self):
        self.set_y(-10)
        self.set_font("DejaVu", "", 8)
        self.cell(w=self.epw, txt="Информационно-аналитическая система FESSBoard", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(w=self.epw, txt="ФЭСН, РАНХиГС", align="C")

def student_to_pdf(student_info, projects_summary, total_activity, events_df):
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
    pdf.cell(txt="Портфолио проектера", new_x="LMARGIN", new_y="NEXT")
    ## Padding
    pdf.cell(0, 8, new_x="LMARGIN", new_y="NEXT")
    # Write project activity
    for key, df in total_activity.items():
        if df.shape[0] > 0:
            df.sort_values(by="Академический год", inplace=True)
            pdf.set_font("DejaVu", "B", 12)
            pdf.cell(None, 8, txt=key, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("DejaVu", "", 12)
            for idx, row in df.iterrows():
                project_name = row['Название проекта']
                project_name = f"{project_name[:50]}..." if len(project_name) >= 50 else project_name
                pdf.cell(pdf.epw*0.7, 8, txt=project_name)
                pdf.cell(pdf.epw*0.2, 8, txt=row['Академический год'])
                pdf.cell(pdf.epw*0.1, 8, txt=row['Грейд'], new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 8, new_x="LMARGIN", new_y="NEXT")
    # Write event activity
    if events_df.shape[0] > 0:
        events_df.sort_values(by="Дата начала", inplace=True)
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(None, 8, txt="Участие в мероприятиях и хакатонах", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "", 12)
        for idx, row in events_df.iterrows():
            event_name = row['Название']
            event_name = f"{event_name[:50]}..." if len(event_name) >= 50 else event_name
            pdf.cell(pdf.epw*0.7, 8, txt=event_name)
            pdf.cell(pdf.epw*0.3, 8, txt=row['Регион'], new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())

##################
##  Plot utils  ##
##################
def two_axis_barchart(data: pd.DataFrame, marker, value_label='шт.', group_col='Академический год', primary_col='Количество', secondary_col='Темп прироста'):
    # figure with 2 axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # bar plot (secondary_y = False)
    fig.add_trace(go.Bar(
            x                   = data[group_col],
            y                   = data[primary_col],
            width               = 0.7,
            name                = value_label,
            marker_color        = marker,
            opacity             = 1,
            marker_line_width   = 0,
            text                = list(data[primary_col]),
            ),
        secondary_y = False)
    fig.update_layout(
            font_family    = "Source Sans Pro",
            font_size      = 13,
            paper_bgcolor  = 'rgba(0,0,0,0)',
            plot_bgcolor   = 'rgba(0,0,0,0)',
            margin         = dict(t=0, l=0, r=0, b=0),
            yaxis_title    = "",
            xaxis_title    = "",
            width          = 10,
            height         = 220,
            xaxis_visible  = True,
            yaxis_visible  = True,
            xaxis          = dict(showgrid=False), 
            yaxis          = dict(showgrid=False),
            showlegend     = False
            )
    fig.update_traces(
        textfont_size   = 14,
            textangle      = 0,
            textposition   = "auto",
            cliponaxis     = False,
            )
    # fig['data'][0].width=0.7
    # scatter plot (secondary_y = True)
    fig.add_trace(go.Scatter(
            x       = data[group_col].iloc[1:],
            y       = data[secondary_col].iloc[1:],
            line    = dict(color='#07C607'),
            name    = secondary_col,
            ),
        secondary_y = True)
    fig.update_yaxes(
        hoverformat = ',.0%',
        tickformat  = ',.0%',
        secondary_y = True
    )
    st.plotly_chart(fig,use_container_width=True,config={'staticPlot': False,'displayModeBar': False})

def donut_chart(values, names, colors, legend=False, textinfo='label', hovertemplate="<b>%{label}.</b> Проектов: <b>%{value}.</b> <br><b>%{percent}</b> от общего количества"):
    fig = px.pie(
        values                  = values,
        names                   = names,
        color_discrete_sequence = colors,
        hole                    = .6
    )

    fig.update_traces(
        textposition  = 'inside',
        textinfo      = textinfo,
        hovertemplate = hovertemplate,
        textfont_size = 14
        
        )

    fig.update_layout(
        plot_bgcolor            = 'rgba(0,0,0,0)',
        paper_bgcolor           = 'rgba(0,0,0,0)',
        showlegend              = legend,
        legend                  = dict(orientation="v",itemwidth=30,yanchor="top", y=0.8,xanchor="left",x=1),
        font_family             = "Source Sans Pro",
        title_font_family       = "Source Sans Pro",
        title_font_color        = "white",
        legend_title_font_color = "white",
        height                  = 220,
        margin                  = dict(t=0, l=0, r=0, b=0),
        )
    st.plotly_chart(fig,use_container_width=True,config={'staticPlot': False,'displayModeBar': False})


