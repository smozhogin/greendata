import streamlit as st
import requests
from PIL import Image
import json
import pyperclip

st.set_page_config(page_title="9Perceptron", layout="wide")

st.title("🔍 9 Перцептрон")
st.markdown("Загрузите изображение для распознавания текста")

with st.expander("📖 Как использовать", expanded=False):
    st.markdown("""
    ### Шаги:
    1. **Настройте параметры** - токены, beams, нормализацию
    2. **Загрузите изображение** с текстом
    3. **Нажмите "Отправить"**
    4. **Получите результат** в правой колонке
    
    ### Параметры:
    - **max_new_tokens** - ограничивает длину ответа
    - **num_beams** - больше = точнее, но медленнее
    - **normalize** - приводит текст к единому формату
    """)

DEFAULT_API_URL = "https://bbar5687vel2bbtv62ae.containers.yandexcloud.net/ocr"

st.subheader("Параметры запроса")

col1, col2, col3 = st.columns(3)

with col1:
    max_new_tokens = st.number_input(
        "max_new_tokens", 
        value=32, 
        min_value=1, 
        max_value=128,
        help="Максимальное количество токенов в ответе"
    )

with col2:
    num_beams = st.number_input(
        "num_beams", 
        value=1, 
        min_value=1, 
        max_value=8,
        help="Количество лучей для поиска"
    )

with col3:
    normalize = st.checkbox(
        "normalize", 
        value=True,
        help="Нормализация текста"
    )


st.divider()

col_left, col_right = st.columns([1, 1])

with col_left:
    st.header("📤 Загрузка изображения")
    
    uploaded_file = st.file_uploader(
        "Выберите изображение", 
        type=['jpg', 'jpeg', 'png', 'bmp'],
        help="Поддерживаемые форматы: JPG, JPEG, PNG, BMP",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Загруженное изображение: {uploaded_file.name}", use_container_width=True)
        
        if st.button("🚀 Распознать", type="primary", use_container_width=True):
            st.session_state['uploaded_file'] = uploaded_file
            st.session_state['api_params'] = {
                'max_new_tokens': int(max_new_tokens),
                'num_beams': int(num_beams),
                'normalize': str(normalize).lower()
            }
            st.rerun()

with col_right:
    st.header("📥 Результат")

    if 'uploaded_file' in st.session_state and 'api_params' in st.session_state:
        uploaded_file = st.session_state['uploaded_file']
        api_params = st.session_state['api_params']
        
        with st.spinner("Распознаем текст..."):
            try:
                files = {
                    'file': (
                        uploaded_file.name, 
                        uploaded_file.getvalue(),
                        f'image/{uploaded_file.name.split(".")[-1]}'
                    )
                }
            
                headers = {
                    'accept': 'application/json',
                }
                
                response = requests.post(
                    DEFAULT_API_URL,
                    params=api_params,
                    files=files,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    st.success("✅ Запрос выполнен успешно!")
                    
                    try:
                        result = response.json()
                        
                        text_result = None
                        if isinstance(result, dict):
                            for key in ['text', 'result', 'ocr_text', 'output', 'data', 'content']:
                                if key in result:
                                    text_result = result[key]
                                    break
                        
                        if text_result:
                            st.subheader("📝 Распознанный текст:")
                            st.text_area(
                                "Текст", 
                                text_result,
                                height=200,
                                label_visibility="collapsed"
                            )
                            
                           
                            col_btn1, col_btn2, col_btn3 = st.columns(3)
                            with col_btn1:
                                st.download_button(
                                    label="💾 Скачать TXT",
                                    data=text_result,
                                    file_name=f"ocr_result_{uploaded_file.name.split('.')[0]}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                        
                    except json.JSONDecodeError:
                        st.warning("Ответ не в JSON формате")
                        st.code(response.text[:1000])
                    
                else:
                    st.error(f"❌ Ошибка API: {response.status_code}")
                    st.code(f"""
                    Статус: {response.status_code}
                    Ответ: {response.text[:500]}
                    """)
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Таймаут запроса. Попробуйте позже")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Ошибка подключения. Проверьте URL и интернет")
            except Exception as e:
                st.error(f"⚠️ Ошибка: {str(e)}")



