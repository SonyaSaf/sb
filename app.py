import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime, timedelta
import io
import os

# Импорт модулей
from utils.versioning import *
from utils.templates import *
from utils.helpers import *
from components.dynamic_lists import *
from components.form_fields import render_field_with_history

st.set_page_config(page_title="Генератор документов", page_icon="📄", layout="wide")

# ==================== CSS СТИЛИ ====================

st.markdown("""
<style>
    .stTextArea textarea {
        height: 200px !important;
        font-family: 'Times New Roman', serif !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
    .section-header {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0px;
        border-left: 4px solid #ff4b4b;
    }
    .field-label {
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 5px;
        color: #333;
    }
    .date-field-group {
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ==================== ИНИЦИАЛИЗАЦИЯ SESSION_STATE ====================

def init_session_state():
    # Основные поля
    basic_fields = ['established_items', 'violation_items', 'summary_items', 'recommendation_items',
                    'business_processes', 'scope_of_verification', 'lss_assessment',
                    'audit_group', 'problem_facts', 'opportunity_facts',
                    'formulated_problems', 'formulated_opportunities']

    for field in basic_fields:
        if field not in st.session_state:
            st.session_state[field] = []

    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Генератор документов"

    if 'current_template' not in st.session_state:
        st.session_state.current_template = ""

    # Для хранения истории
    if 'field_histories' not in st.session_state:
        st.session_state.field_histories = {}


# ==================== ИНИЦИАЛИЗАЦИЯ ====================

init_session_state()
available_templates = get_available_templates()

# ==================== НАВИГАЦИЯ ====================

st.sidebar.title("📋 Навигация")

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("📄 Генератор", use_container_width=True):
        st.session_state.current_page = "Генератор документов"
        st.rerun()
with col2:
    if st.button("🕐 Версии", use_container_width=True):
        st.session_state.current_page = "Управление версиями"
        st.rerun()

st.sidebar.markdown("---")

# ==================== СТРАНИЦА: ГЕНЕРАТОР ДОКУМЕНТОВ ====================

if st.session_state.current_page == "Генератор документов":
    st.title("📄 Генератор документов")

    # Выбор шаблона
    if available_templates:
        selected_template = st.selectbox(
            'Выберите шаблон документа *',
            available_templates,
            help='Выберите шаблон из доступных'
        )
    else:
        st.error('❌ Шаблоны не найдены. Добавьте файлы .docx в папку "templates"')
        st.stop()

    template_config = get_template_fields(selected_template)
    st.session_state.current_template = selected_template
    st.info(f"**Выбран шаблон:** {template_config['name']}")

    # Поле для автора
    author_name = st.text_input(
        "Ваше имя (для истории изменений)",
        placeholder="Введите ваше ФИО",
        help="Будет сохранено в истории версий",
        key="author_name"
    )

    # Загрузка существующих документов для выбора
    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 Существующие документы")

    existing_docs = get_all_documents()
    doc_names = ["Новый документ"] + [doc["name"] for doc in existing_docs]

    selected_doc_name = st.sidebar.selectbox(
        "Выберите документ:",
        options=doc_names,
        help="Выберите существующий документ или создайте новый"
    )

    # Загрузка последней версии выбранного документа
    current_doc_data = {}
    if selected_doc_name != "Новый документ":
        latest_version = load_latest_version(selected_doc_name)
        if latest_version and "data" in latest_version:
            current_doc_data = latest_version["data"]
            st.sidebar.success(f"✅ Загружена последняя версия документа")

    # Основные поля формы
    form_data = {}

    # Для шаблона application_template рендерим в правильном порядке
    if selected_template == "application_template.docx":
        # 1. Основная информация
        st.markdown("### Основная информация")

        basic_fields = ['state', 'generated_date', 'audit_report', 'basis_for_verify']
        for field_name in basic_fields:
            if field_name in template_config['fields']:
                field_config = template_config['fields'][field_name]
                field_label = field_config['label']

                # Получаем историю
                field_history = []
                if selected_doc_name != "Новый документ":
                    field_history = get_field_history(selected_doc_name, field_name)

                # Рендерим поле
                render_field_with_history(field_name, field_config, current_doc_data,
                                          field_history, selected_doc_name, form_data)

        # 2. Состав аудиторской группы
        st.markdown("### Состав аудиторской группы")

        # Загружаем данные для аудиторской группы
        items = st.session_state['audit_group']
        if not items and selected_doc_name != "Новый документ":
            saved_items = current_doc_data.get('audit_group', [])
            if isinstance(saved_items, list):
                items = saved_items
                st.session_state['audit_group'] = items

        render_participant_group_simple('audit_group', 'Состав аудиторской группы *', items)
        form_data['audit_group'] = items

        # 3. Сроки проведения проверки (фиксированные под заголовком)
        st.markdown('<div class="field-label">Сроки проведения аудиторской проверки:</div>', unsafe_allow_html=True)

        # Загружаем сохраненные даты
        start_date_val = datetime.now().date()
        end_date_val = datetime.now().date() + timedelta(days=14)

        if 'start_date' in current_doc_data and 'end_date' in current_doc_data:
            try:
                start_date_val = datetime.strptime(str(current_doc_data['start_date']), '%Y-%m-%d').date()
                end_date_val = datetime.strptime(str(current_doc_data['end_date']), '%Y-%m-%d').date()
            except:
                pass

        # Поля дат рядом под заголовком
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                'Начало проверки *',
                value=start_date_val,
                key="start_date_input"
            )
        with col2:
            end_date = st.date_input(
                'Окончание проверки *',
                value=end_date_val,
                key="end_date_input"
            )

        form_data['start_date'] = start_date
        form_data['end_date'] = end_date
        form_data['verification_period'] = format_date_range(start_date, end_date)

        # 4. Номер мероприятия
        if 'event_number' in template_config['fields']:
            field_config = template_config['fields']['event_number']
            field_history = []
            if selected_doc_name != "Новый документ":
                field_history = get_field_history(selected_doc_name, 'event_number')

            render_field_with_history('event_number', field_config, current_doc_data,
                                      field_history, selected_doc_name, form_data)

        # 5. Проверенный период (фиксированные под заголовком)
        st.markdown('<div class="field-label">Проверенный период:</div>', unsafe_allow_html=True)

        checked_start_val = datetime.now().date() - timedelta(days=30)
        checked_end_val = datetime.now().date()

        if 'checked_start_date' in current_doc_data and 'checked_end_date' in current_doc_data:
            try:
                checked_start_val = datetime.strptime(str(current_doc_data['checked_start_date']), '%Y-%m-%d').date()
                checked_end_val = datetime.strptime(str(current_doc_data['checked_end_date']), '%Y-%m-%d').date()
            except:
                pass

        col1, col2 = st.columns(2)
        with col1:
            checked_start_date = st.date_input(
                'Начало проверенного периода *',
                value=checked_start_val,
                key="checked_start_input"
            )
        with col2:
            checked_end_date = st.date_input(
                'Конец проверенного периода *',
                value=checked_end_val,
                key="checked_end_input"
            )

        form_data['checked_start_date'] = checked_start_date
        form_data['checked_end_date'] = checked_end_date
        form_data['checked_period'] = format_date_range(checked_start_date, checked_end_date)

        # 6. Информация о проверенных бизнес-процессах
        st.markdown("### 1. Информация о проверенных бизнес-процессах:")

        # Загружаем данные для бизнес-процессов
        items = st.session_state['business_processes']
        if not items and selected_doc_name != "Новый документ":
            saved_items = current_doc_data.get('business_processes', [])
            if isinstance(saved_items, list):
                items = saved_items
                st.session_state['business_processes'] = items

        render_business_process_table('business_processes', 'Бизнес-процессы', items)
        form_data['business_processes'] = items

        # 7. Охват проверки
        st.markdown("### Охват проверки:")

        # Загружаем данные для охвата проверки
        items = st.session_state['scope_of_verification']
        if not items and selected_doc_name != "Новый документ":
            saved_items = current_doc_data.get('scope_of_verification', [])
            if isinstance(saved_items, list):
                items = saved_items
                st.session_state['scope_of_verification'] = items

        render_dynamic_list('scope_of_verification', 'Охват проверки', items, "dynamic_list")
        form_data['scope_of_verification'] = items

        # 8. Описание процесса
        st.markdown("### Описание процесса:")

        if 'process_description' in template_config['fields']:
            field_config = template_config['fields']['process_description']
            field_history = []
            if selected_doc_name != "Новый документ":
                field_history = get_field_history(selected_doc_name, 'process_description')

            render_field_with_history('process_description', field_config, current_doc_data,
                                      field_history, selected_doc_name, form_data)

        # 9. Оценка качества LSS
        st.markdown("### 2. Оценка качества проверенных процессов по методологии LSS")

        # Загружаем данные для LSS
        items = st.session_state['lss_assessment']
        if not items and selected_doc_name != "Новый документ":
            saved_items = current_doc_data.get('lss_assessment', [])
            if isinstance(saved_items, list):
                items = saved_items
                st.session_state['lss_assessment'] = items

        render_lss_table('lss_assessment', 'Таблица LSS', items)
        form_data['lss_assessment'] = items

        # 10. Факты проблем
        st.markdown("### 3. Факты, подтверждающие наличие проблем в бизнес-процессе:")

        # Загружаем данные для фактов проблем
        items = st.session_state['problem_facts']
        if not items and selected_doc_name != "Новый документ":
            saved_items = current_doc_data.get('problem_facts', [])
            if isinstance(saved_items, list):
                items = saved_items
                st.session_state['problem_facts'] = items

        render_problem_facts_list('problem_facts', 'Факты проблем', items)
        form_data['problem_facts'] = items

        # 11. Факты возможностей
        st.markdown("### 4. Факты, подтверждающие наличие возможности в бизнес-процессе:")

        # Загружаем данные для фактов возможностей
        items = st.session_state['opportunity_facts']
        if not items and selected_doc_name != "Новый документ":
            saved_items = current_doc_data.get('opportunity_facts', [])
            if isinstance(saved_items, list):
                items = saved_items
                st.session_state['opportunity_facts'] = items

        render_opportunity_facts_list('opportunity_facts', 'Факты возможностей', items)
        form_data['opportunity_facts'] = items

        # 12. Сформулированные проблемы
        st.markdown("### 5. Сформулирована проблема:")

        # Загружаем данные для сформулированных проблем
        items = st.session_state['formulated_problems']
        if not items and selected_doc_name != "Новый документ":
            saved_items = current_doc_data.get('formulated_problems', [])
            if isinstance(saved_items, list):
                items = saved_items
                st.session_state['formulated_problems'] = items

        render_formulated_problems_list('formulated_problems', 'Сформулированные проблемы', items)
        form_data['formulated_problems'] = items

        # 13. Сформулированные возможности
        st.markdown("### 6. Сформулирована возможность:")

        # Загружаем данные для сформулированных возможностей
        items = st.session_state['formulated_opportunities']
        if not items and selected_doc_name != "Новый документ":
            saved_items = current_doc_data.get('formulated_opportunities', [])
            if isinstance(saved_items, list):
                items = saved_items
                st.session_state['formulated_opportunities'] = items

        render_formulated_opportunities_list('formulated_opportunities', 'Сформулированные возможности', items)
        form_data['formulated_opportunities'] = items

        # 14. Подписи
        st.markdown("### Подписи")

        signature_fields = ['audit_leader', 'audit_curator', 'direction_leader']
        for field_name in signature_fields:
            if field_name in template_config['fields']:
                field_config = template_config['fields'][field_name]
                field_history = []
                if selected_doc_name != "Новый документ":
                    field_history = get_field_history(selected_doc_name, field_name)

                render_field_with_history(field_name, field_config, current_doc_data,
                                          field_history, selected_doc_name, form_data)

    # ДЛЯ ШАБЛОНА word_tpl.docx
    if selected_template == "word_tpl.docx":
        # Рендерим обычные поля
        for field_name, field_config in template_config['fields'].items():
            field_type = field_config['type']

            # Пропускаем динамические списки и специальные поля
            if field_type in ["dynamic_list", "dynamic_list_with_dates", "label"]:
                continue

            field_label = field_config['label']

            # Получаем историю для этого поля
            field_history = []
            if selected_doc_name != "Новый документ":
                field_history = get_field_history(selected_doc_name, field_name)
                st.session_state.field_histories[field_name] = field_history

            # Особый рендеринг для verification_period (диапазон дат)
            if field_name == "verification_period":
                st.markdown('<div class="field-label">Сроки проведения проверки:</div>', unsafe_allow_html=True)

                # Загружаем сохраненные даты
                start_date_val = datetime.now().date()
                end_date_val = datetime.now().date() + timedelta(days=14)

                if 'verification_period' in current_doc_data:
                    # Пытаемся распарсить сохраненный диапазон дат
                    try:
                        if isinstance(current_doc_data['verification_period'], dict):
                            # Если данные сохранены как словарь
                            start_date_val = datetime.strptime(
                                str(current_doc_data['verification_period'].get('start_date', '')),
                                '%Y-%m-%d').date()
                            end_date_val = datetime.strptime(
                                str(current_doc_data['verification_period'].get('end_date', '')), '%Y-%m-%d').date()
                        elif isinstance(current_doc_data['verification_period'], str):
                            # Если данные сохранены как строка "01.01.2023-15.01.2023"
                            parts = current_doc_data['verification_period'].split('-')
                            if len(parts) == 2:
                                start_date_val = datetime.strptime(parts[0].strip(), '%d.%m.%Y').date()
                                end_date_val = datetime.strptime(parts[1].strip(), '%d.%m.%Y').date()
                    except:
                        pass

                # Поля дат рядом под заголовком
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        'Начало проверки *',
                        value=start_date_val,
                        key="word_tpl_start_date"
                    )
                with col2:
                    end_date = st.date_input(
                        'Окончание проверки *',
                        value=end_date_val,
                        key="word_tpl_end_date"
                    )

                form_data['start_date'] = start_date
                form_data['end_date'] = end_date
                form_data['verification_period'] = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'formatted': format_date_range(start_date, end_date)
                }

                # Сохраняем для истории
                field_history = []
                if selected_doc_name != "Новый документ":
                    field_history = get_field_history(selected_doc_name, 'verification_period')

                # Показываем историю для этого поля
                if field_history:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        version_options = ["Текущая (новая версия)"] + [
                            f"Версия от {datetime.fromisoformat(h['timestamp']).strftime('%d.%m.%Y %H:%M')} ({h['author']})"
                            for h in field_history
                        ]

                        selected_version = st.selectbox(
                            f"Выберите версию для поля 'Сроки проведения проверки'",
                            options=version_options,
                            key=f"version_selector_verification_period",
                            help="Выберите версию значения из истории изменений"
                        )

                        if selected_version != "Текущая (новая версия)":
                            version_index = version_options.index(selected_version) - 1
                            selected_history = field_history[version_index]
                            st.info(
                                f"📅 **Выбрана версия от:** {datetime.fromisoformat(selected_history['timestamp']).strftime('%d.%m.%Y %H:%M')}")

                st.markdown("---")

            else:
                # Рендерим обычные поля
                render_field_with_history(field_name, field_config, current_doc_data,
                                          field_history, selected_doc_name, form_data)

        # Рендерим динамические списки
        for field_name, field_config in template_config['fields'].items():
            field_type = field_config['type']
            field_label = field_config['label']

            if field_type in ["dynamic_list", "dynamic_list_with_dates"]:
                # Загружаем данные из последней версии
                items = st.session_state[field_name]
                if not items and selected_doc_name != "Новый документ":
                    saved_items = current_doc_data.get(field_name, [])
                    if isinstance(saved_items, list):
                        items = saved_items
                        st.session_state[field_name] = items

                render_dynamic_list(field_name, field_label, items, field_type)
                form_data[field_name] = items


    else:
        # Оригинальный рендеринг для других шаблонов
        for field_name, field_config in template_config['fields'].items():
            field_type = field_config['type']

            # Пропускаем динамические списки - они будут отдельно
            if field_type in ["dynamic_list", "dynamic_list_with_dates"]:
                continue

            field_label = field_config['label']

            # Получаем историю для этого поля
            field_history = []
            if selected_doc_name != "Новый документ":
                field_history = get_field_history(selected_doc_name, field_name)
                st.session_state.field_histories[field_name] = field_history

            # Рендерим поле с возможностью выбора версий
            render_field_with_history(field_name, field_config, current_doc_data,
                                      field_history, selected_doc_name, form_data)

        # Рендерим динамические списки для других шаблонов
        for field_name, field_config in template_config['fields'].items():
            field_type = field_config['type']
            field_label = field_config['label']

            if field_type in ["dynamic_list", "dynamic_list_with_dates"]:
                # Загружаем данные из последней версии
                items = st.session_state[field_name]
                if not items and selected_doc_name != "Новый документ":
                    saved_items = current_doc_data.get(field_name, [])
                    if isinstance(saved_items, list):
                        items = saved_items
                        st.session_state[field_name] = items

                render_dynamic_list(field_name, field_label, items, field_type)
                form_data[field_name] = items

    # Большая финальная кнопка "Сгенерировать документ"
    st.markdown("---")
    st.markdown("### 🎉 Завершение заполнения документа")

    # Кнопка генерации документа
    if st.button("🚀 Сгенерировать документ", use_container_width=True, type="primary"):
        # Проверка обязательных полей
        errors = []

        # Проверяем основные обязательные поля
        required_fields = ['state', 'generated_date', 'audit_report', 'basis_for_verify']
        for field_name in required_fields:
            if field_name in template_config['fields'] and template_config['fields'][field_name].get('required', False):
                field_value = form_data.get(field_name)
                if not field_value or (isinstance(field_value, str) and not field_value.strip()):
                    errors.append(template_config['fields'][field_name]['label'])

        # Проверяем аудиторскую группу
        if 'audit_group' in form_data and not form_data['audit_group']:
            errors.append("Состав аудиторской группы")

        # Проверяем даты
        if 'start_date' in form_data and 'end_date' in form_data:
            if form_data['end_date'] <= form_data['start_date']:
                errors.append("Дата окончания должна быть позже даты начала")

        if 'checked_start_date' in form_data and 'checked_end_date' in form_data:
            if form_data['checked_end_date'] <= form_data['checked_start_date']:
                errors.append("Конец проверенного периода должен быть позже начала")

        # Проверка автора
        if not author_name:
            errors.append("Имя автора (для истории изменений)")

        if errors:
            st.error(f'❌ Пожалуйста, заполните обязательные поля: {", ".join(errors)}')
            st.stop()

        # Подготовка данных для документа
        document_data = form_data.copy()
        document_data['selected_template'] = selected_template
        document_data['generation_date'] = datetime.now().strftime('%d.%m.%Y %H:%M')

        # Форматирование специальных полей
        if 'audit_group' in document_data:
            document_data['audit_group_formatted'] = format_participant_group(document_data['audit_group'])

        if 'business_processes' in document_data:
            document_data['business_processes_formatted'] = format_business_process_group(
                document_data['business_processes'])

        if 'lss_assessment' in document_data:
            document_data['lss_assessment_formatted'] = format_lss_assessment(document_data['lss_assessment'])

        if 'problem_facts' in document_data:
            document_data['problem_facts_formatted'] = format_problem_facts_group(document_data['problem_facts'])

        if 'opportunity_facts' in document_data:
            document_data['opportunity_facts_formatted'] = format_opportunity_facts_group(
                document_data['opportunity_facts'])

        if 'formulated_problems' in document_data:
            document_data['formulated_problems_formatted'] = format_formulated_problems_group(
                document_data['formulated_problems'])

        if 'formulated_opportunities' in document_data:
            document_data['formulated_opportunities_formatted'] = format_formulated_opportunities_group(
                document_data['formulated_opportunities'])

        # Форматирование динамических списков
        if 'scope_of_verification' in document_data:
            document_data['scope_of_verification_formatted'] = format_items_list(document_data['scope_of_verification'])

        try:
            # Сохраняем версию
            version_id = save_document_version(
                document_data,
                author_name,
                selected_template
            )

            # Генерация документа
            template_path = os.path.join('templates', selected_template)
            doc = DocxTemplate(template_path)
            doc.render(document_data)

            file_stream = io.BytesIO()
            doc.save(file_stream)
            file_stream.seek(0)

            st.success("✅ Документ успешно сохранен и сгенерирован!")

            # Показываем информацию о сохраненной версии
            document_name = document_data.get('audit_report', 'Без названия')
            history = load_document_history(document_name)
            if history and "versions" in history:
                version_count = len(history["versions"])
                st.info(f"📊 Это **{version_count}-я версия** документа '{document_name}'")

            # Кнопка скачивания
            st.download_button(
                label='📥 Скачать документ',
                data=file_stream,
                file_name=f"{document_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
                mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                use_container_width=True
            )

        except Exception as e:
            st.error(f'❌ Произошла ошибка: {str(e)}')

# ==================== СТРАНИЦА: УПРАВЛЕНИЕ ВЕРСИЯМИ ====================

elif st.session_state.current_page == "Управление версиями":
    st.title("🕐 Управление версиями документов")

    # Выбор документа для просмотра истории
    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 Выбор документа")

    existing_docs = get_all_documents()

    if not existing_docs:
        st.info("📝 История версий пуста. Создайте первый документ на странице 'Генератор документов'.")
    else:
        doc_names = [doc["name"] for doc in existing_docs]
        selected_doc_name = st.sidebar.selectbox(
            "Выберите документ:",
            options=doc_names,
            help="Выберите документ для просмотра истории версий"
        )

        # Загружаем историю выбранного документа
        if selected_doc_name:
            history = load_document_history(selected_doc_name)

            if history and "versions" in history:
                st.subheader(f"📋 История версий: {selected_doc_name}")
                st.info(f"Всего версий: {len(history['versions'])}")

                # Сортируем версии по дате (новые сначала)
                versions = sorted(history["versions"], key=lambda x: x["timestamp"], reverse=True)

                for i, version in enumerate(versions):
                    with st.expander(
                            f"Версия #{i + 1} - {datetime.fromisoformat(version['timestamp']).strftime('%d.%m.%Y %H:%M')}",
                            expanded=i == 0
                    ):
                        col1, col2, col3 = st.columns([2, 1, 1])

                        with col1:
                            st.write(f"**Автор:** {version['author']}")
                            st.write(f"**Шаблон:** {version.get('template_used', 'Не указан')}")
                            st.write(
                                f"**Дата создания:** {datetime.fromisoformat(version['timestamp']).strftime('%d.%m.%Y %H:%M')}")

                        with col2:
                            if st.button(f"📝 Загрузить", key=f"load_{version['version_id'][:8]}"):
                                # Загружаем данные в форму
                                for field_name, value in version.get('data', {}).items():
                                    if isinstance(value, list):
                                        st.session_state[field_name] = value
                                    else:
                                        st.session_state[f'loaded_{field_name}'] = value

                                st.session_state.current_page = "Генератор документов"
                                st.rerun()

                        with col3:
                            if i < len(versions) - 1:
                                if st.button(f"🔍 Сравнить", key=f"compare_{version['version_id'][:8]}"):
                                    # Показываем сравнение с предыдущей версией
                                    prev_version = versions[i + 1]
                                    st.session_state.compare_versions = {
                                        "current": version,
                                        "previous": prev_version
                                    }

                    # Показываем сравнение версий если выбрано
                    if "compare_versions" in st.session_state:
                        compare = st.session_state.compare_versions
                        if compare["current"]["version_id"] == version["version_id"]:
                            st.markdown("---")
                            st.subheader("🔍 Сравнение версий")

                            current_data = compare["current"]["data"]
                            previous_data = compare["previous"]["data"]

                            # Сравниваем поля
                            differences = []
                            all_fields = set(current_data.keys()) | set(previous_data.keys())

                            for field in all_fields:
                                current_val = current_data.get(field)
                                previous_val = previous_data.get(field)

                                if current_val != previous_val:
                                    differences.append({
                                        "field": field,
                                        "current": current_val,
                                        "previous": previous_val
                                    })

                            if differences:
                                st.write("**Обнаруженные изменения:**")
                                for diff in differences:
                                    with st.expander(f"Поле: {diff['field']}"):
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.write("**Было:**")
                                            st.text(diff['previous'] if diff['previous'] else "Пусто")
                                        with col2:
                                            st.write("**Стало:**")
                                            st.text(diff['current'] if diff['current'] else "Пусто")
                            else:
                                st.info("⚠️ Версии идентичны - изменений не обнаружено")

            else:
                st.warning("История версий для выбранного документа не найдена.")