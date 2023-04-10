import streamlit as st
import utils as utils

def run():
    st.header('О FESSBoard')
    st.write(
    """
    FESSBoard – это многокомпонентная информационно-аналитическая система с интерактивными элементами управления и визуализации данных, используемая для анализ бизнес-процессов и деятельности центра проектных решений при факультете экономических и социальных наук.  
    **Языки:** Python, CSS, HTML, JQuery  
    **Стэк:** Streamlit, Django, MySQL
    """
    )

    st.subheader('Обратная связь')
    text_col, qr_col    = st.columns([3,1])
    with qr_col:
        st.image('img/feedback.png')
    with text_col:
        st.write("""
        Нам очень важна Ваша обратная связь. Если Вы нашли баг, хотите предложить улучшение или оставить отзыв - заполните анкету **[по ссылке](https://forms.gle/yHKSg8oNko9MnQtB6)**.
        """
        )

    st.subheader('Команда проекта')
    col1, col2          = st.columns(2)
    col3, col4, col5    = st.columns(3)
    with col1:
        st.info("""
                **Project Manager & Streamlit Dev:**  
                **[Ilya Matyushin](https://t.me/terrorChay)**
                """, icon="💼")
    with col2:
        st.info("""
                **Process & Data Analyst:**  
                **[Semyon Kuvshinov](https://t.me/skuvshin0v)**
                """, icon="🕵️‍♂️")
    with col3:
        st.info("""
                **Django Dev:**  
                **[Mike Tanko](https://t.me/iie4enka)**"""
                , icon="🍪")
    with col4:
        st.info("""
                **Business Analyst:**  
                **[Nikolay Grudtsyn](https://t.me/ShkilyaGrit)**
                """, icon="🧛🏻‍♂️")
    with col5:
        st.info("""
                **Business Analyst:**  
                **[Tanya Leonova](https://t.me/alicetyler15)**"""
                , icon="🔥")

if __name__ == "__main__":
    utils.page_config(layout='centered', title='Информация о FESSBoard', page_icon=':bar_chart:')
    utils.remove_footer()
    utils.set_logo()
    run()