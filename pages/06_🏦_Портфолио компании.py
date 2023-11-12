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
import plotly.graph_objects as go
#Наборы цветов
color_themes = {
                'FESS'  : ['#ED1C24','#670004','#C53A40','#FCB6B9','#941B1E','#F85B61','#FFD5D7','#F78F92'],
                'ЦПР'    :['#3A42FF','#00046F','#2227A7','#88B1FF','#D3E2FF','#C0C0C0','#969696','#5B5B5B','#222222','#FFFFFF','#FB832A']
                }
tr='rgba(0,0,0,0)'
font="Source Sans Pro"
config = {'staticPlot': False,'displayModeBar': False}

# Apply search filters and return filtered dataset
def search_dataframe(df: pd.DataFrame, label='Поиск') -> pd.DataFrame:
    df = df.copy()
    user_text_input = st.text_input(label, placeholder='Введите текст', help='Укажите текст, который могут содержать интересующие Вас проекты')
    if user_text_input:
        _user_text_input = "".join([char for char in user_text_input if char.isalnum()])
        mask = df.apply(lambda x: x.astype(str).str.contains(_user_text_input, na=False, flags=re.IGNORECASE))
        df = df.loc[mask.any(axis=1)]
    return df

# Apply filters and return company name
def company_selection(df: pd.DataFrame):
    df = df[['ID компании', 'Название компании', 'Тип компании', 'Отрасль']].copy()
    df.sort_values(by='ID компании', inplace=True)
    df.insert(0, 'Составной ключ', df['ID компании'].astype('str') + ' - ' + df['Название компании'])
    company = False
    modification_container = st.container()
    with modification_container:
        options = np.insert(df['Составной ключ'].unique(), 0, 'Не выбрано', axis=0)
        # Household name selection
        preselection = 0
        if 'company_selectbox' in session:
            try:
                preselection = int(np.where(options == session['company_selectbox'])[0][0])
            except:
                pass
        user_cat_input = st.selectbox(
            "Название компании",
            options,
            index=preselection,
            key='company_selectbox',
        )
        if user_cat_input and user_cat_input != 'Не выбрано':
            company = user_cat_input
    return company

# App launch
def run():
    # Load dataframe
    with st.spinner('Изучаем SCRUM...'):
        projects_df = utils.load_projects()
    with st.spinner('Звоним в деканат...'):
        fields_df               = utils.load_fields()
    st.title('Портфолио компании')
    st.write('''
            #### На данной странице можно ознакомиться с портфелем проектов выбранной компании!
            :mag: Раздел __О компании__ содержит основную информацию о выбранной компании.  
            :art: Раздел __Проекты__ содержит таблицу всех проектов, которые выполнялись с выбранной компанией.  
            :male-student: Раздел __Студенты__ количество совместных проектов компании и студентов.\n

            :floppy_disk: Все таблицы можно скачать в формате Microsoft Excel.
            ''')
    selection = st.sidebar.selectbox(options =color_themes.keys(),label='Выберите тему')
    colors = color_themes[selection]
    marker = colors[0]
    # Draw company search filters and return chosen company
    company = company_selection(projects_df)
    company_id = int(company[:5].split(' - ')[0])
    st.write(company_id)
    st.write("test_test")
    if company:
        company_id = int(company[:5].split(' - ')[0])
        tab1, tab2, tab3 = st.tabs(['О компании', 'Проекты', 'Студенты'])
        with st.spinner('Делаем однотумбовые столы...'):
            company_data_df            = utils.load_companies()
            company_data_df            = company_data_df.loc[company_data_df['ID компании'] == company_id].to_dict()
            projects_with_company   = projects_df.loc[projects_df['ID компании'] == company_id]
        with st.spinner('Захватываем мир...'):
            students_with_company   = utils.load_students_in_projects().merge(projects_with_company[['ID проекта']], on='ID проекта', how='right')

        # О компании
        with tab1:
            #INFO
            col1, col2 = st.columns([4,1])
            for key, value in company_data_df.items():
                key = key.casefold()
                value = list(value.values())[0]
                if 'сайт' in key:
                    col1.markdown(f'[{value}]({value})')
                elif 'логотип' in key:
                    try:
                        col2.image(value, use_column_width='auto')
                    except:
                        col2.caption('Логотип уехал в отпуск')
                elif 'название компании' in key:
                    col1.subheader(value)
                elif 'id компании' in key:
                    pass
                else: 
                    col1.caption(value)
            #METRICS
            projects_summary = {
                'Выполнено проектов'    : projects_with_company.loc[(projects_with_company['Статус'] == 'Завершен')|(projects_with_company['Статус'] == 'Заморожен')].shape[0],
                'Проектов в работе'     : projects_with_company.loc[projects_with_company['Статус'] == 'Активен'].shape[0],
                'Частый грейд'          : projects_with_company['Грейд'].mode()[0],
                'Партнеры'              : f"c {projects_with_company['Дата начала'].min().year} года",
            }
            cols = st.columns(4)
            for idx, key in enumerate(list(projects_summary)):
                cols[idx].metric(key, projects_summary[key])
            col1, col2, col3,col4 = st.columns([1,1,1,1])
                # График распределения проектов студента по макронаправлениям
            with col1:
                    with st.container():
                        st.markdown('**Распределение проектов с компанией по макронаправлениям**')
                        data = projects_df.loc[projects_df['ID проекта'].isin(projects_with_company['ID проекта'])]['Макро-направление'].value_counts().reset_index(name='Количество')
                        data = data.rename(columns={'index':'Макро'})
                        data = data.drop_duplicates().merge(fields_df['Макро'].drop_duplicates(), on='Макро', how='right').fillna(0).sort_values(by='Количество')
                        fig = px.line_polar(data,r='Количество',theta='Макро',line_close=True,color_discrete_sequence=colors)
                        fig.update_traces(fill='toself',mode='lines+markers',cliponaxis=False)
                        fig.update_layout(
                            font_family=font,
                            font_size = 10,
                            paper_bgcolor = tr,
                            plot_bgcolor  = tr,
                            height = 220,
                            yaxis_visible   = False,
                            margin                  = dict(t=35, l=0, r=0, b=35))
                        fig.update_layout(polar = dict(radialaxis = dict(showticklabels = False,tick0=0,dtick=1)))
                        st.plotly_chart(fig,use_container_width=True,config={'staticPlot': False,'displayModeBar': False})
                
                    # График распределения проектов студента по грейдам
            with col2:
                    with st.container():                    
                        data = projects_df.loc[projects_df['ID проекта'].isin(projects_with_company['ID проекта'])]['Микро-направление'].value_counts().reset_index(name='Количество')
                        data = data.rename(columns={'index':'Микро'})
                        st.markdown('**Распределение проектов  с компанией по микронаправлениям**')
                        v = data['Количество']
                        n = data['Микро']
                        utils.donut_chart(v,n,colors, textinfo='value')
                # Display regular projects             
            with col3:
                    with st.container():
                        st.markdown('**Распределение проектов  с компанией по<br>грейдам**',unsafe_allow_html=True)
                        data = projects_df.loc[projects_df['ID проекта'].isin(projects_with_company['ID проекта'])]['Грейд'].value_counts().reset_index(name='Количество')
                        data = data.rename(columns={'index':'Грейд'})
                        v = data['Количество']
                        n = data['Грейд']
                        utils.donut_chart(v,n,colors)      
                    # График вовлеченности студента в проекты по курсам
            with col4:
                    with st.container():
                        st.markdown('**Проекты с компанией по<br> академическим годам**',unsafe_allow_html=True)
                        a = projects_with_company['Академический год'].value_counts()
                        a = a.sort_index()
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                                x                   = a.index,
                                y                   = a.values,
                                width               = 0.7,
                                name                = 'Проектов',
                                marker_color        = marker,
                                opacity             = 1,
                                marker_line_width   = 0,
                                text = a.values
                                
                                ))
                            
                        fig.update_layout(
                            font_family    = font,
                            font_size      = 13,
                            paper_bgcolor  = tr,
                            plot_bgcolor   = tr,
                            margin         = dict(t=0, l=0, r=0, b=0),
                            yaxis_title    = "",
                            xaxis_title    = "",
                            width          = 10,
                            height         = 230,
                            xaxis_visible  = True,
                            yaxis_visible  = True,
                            xaxis          = dict(showgrid=False), 
                            yaxis          = dict(showgrid=True),
                            showlegend     = False
                            )
                        fig.update_traces(
                            textfont_size   = 14,
                            textangle      = 0,
                            textposition   = "auto",
                            cliponaxis     = False,
                            )
                        
                        st.plotly_chart(fig,use_container_width=True,config={'staticPlot': True,'displayModeBar': False})
                    # Распределение проектов студента по микронаправлениям

        # Проекты        
        with tab2:
            ## Draw search filters and return filtered df
            df_search_applied   = search_dataframe(projects_with_company, label='Поиск по проектам')
            ## if search has results draw dataframe and download buttons
            if df_search_applied.shape[0]:
                st.dataframe(df_search_applied, use_container_width=True)
                st.download_button('💾 CSV', data=utils.convert_df(df_search_applied), file_name=f"{company}_slice.csv", mime='text/csv')
                st.download_button('💾 Excel', data=utils.convert_df(df_search_applied, True), file_name=f"{company}_slice.xlsx")
            else:
                st.warning('Проекты не найдены')

        # Студенты
        with tab3:
            # Draw search filters and return filtered df
            _students_with_company  = students_with_company[['ID студента', 'ФИО студента']].dropna(subset='ID студента', inplace=False)
            _projects_count         = students_with_company.groupby(['ID студента'])['ID студента'].count().sort_values(ascending=False).to_frame(name='Проектов с компанией').reset_index(drop=False)
            projects_count          = _projects_count.merge(_students_with_company, how='left', on='ID студента').drop_duplicates()
            df_search_applied       = search_dataframe(projects_count[['ФИО студента', 'Проектов с компанией']], label='Поиск по студентам')
            # if search has results draw dataframe and download buttons
            if df_search_applied.shape[0]:
                st.dataframe(df_search_applied, use_container_width=True)
                st.download_button('💾 CSV', data=utils.convert_df(df_search_applied), file_name=f"{company}_students.csv", mime='text/csv')
                st.download_button('💾 Excel', data=utils.convert_df(df_search_applied, True), file_name=f"{company}_students.xlsx")
            else:
                st.warning('Студенты не найдены')

    else:
        st.markdown(f"<h4 style='text-align: center;'>Выберите компанию 😎</h4>", unsafe_allow_html=True)
    
if __name__ == "__main__":
    utils.page_config(layout='wide', title='Портфолио компании', page_icon=':bar_chart:')
    utils.remove_footer()
    utils.load_local_css('css/company.css')
    utils.set_logo()
    run()
