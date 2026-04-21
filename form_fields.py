import streamlit as st
from datetime import datetime
from typing import Dict, Optional
from utils.versioning import highlight_text_differences


def render_field_with_history(field_name: str, field_config: Dict,
                              current_doc_data: Dict, field_history: list,
                              selected_doc_name: str, form_data: Dict):
    """Рендерит поле с возможностью выбора версий"""
    field_type = field_config['type']
    field_label = field_config['label']

    with st.container():
        st.markdown(f"**{field_label}**")

        # Если есть история версий, показываем селектор версий
        if field_history and len(field_history) > 0:
            version_options = ["Текущая (новая версия)"] + [
                f"Версия от {datetime.fromisoformat(h['timestamp']).strftime('%d.%m.%Y %H:%M')} ({h['author']})"
                for h in field_history
            ]

            col1, col2 = st.columns([3, 1])
            with col1:
                selected_version_key = f"version_selector_{field_name}"

                if selected_version_key not in st.session_state:
                    st.session_state[selected_version_key] = "Текущая (новая версия)"

                selected_version = st.selectbox(
                    f"Выберите версию для поля '{field_label}'",
                    options=version_options,
                    key=selected_version_key,
                    help="Выберите версию значения из истории изменений"
                )

            with col2:
                # Простая кнопка истории
                history_expander_key = f"history_expander_{field_name}"
                if st.button("📋", key=f"history_btn_{field_name}", help="Показать историю изменений"):
                    if history_expander_key not in st.session_state:
                        st.session_state[history_expander_key] = True
                    else:
                        st.session_state[history_expander_key] = not st.session_state[history_expander_key]
                    st.rerun()

            # Показываем историю если кнопка нажата
            if history_expander_key in st.session_state and st.session_state[history_expander_key]:
                with st.expander("История изменений этого поля", expanded=True):
                    for i, history_item in enumerate(field_history):
                        st.markdown(
                            f"**Версия {i + 1}** - {datetime.fromisoformat(history_item['timestamp']).strftime('%d.%m.%Y %H:%M')}")
                        st.markdown(f"👤 **Автор:** {history_item['author']}")
                        st.markdown(f"🔢 **ID версии:** {history_item['version_id']}")
                        if history_item['value']:
                            if isinstance(history_item['value'], str) and len(history_item['value']) > 200:
                                st.text_area("Значение:", value=history_item['value'], height=100,
                                             key=f"history_value_{field_name}_{i}")
                            else:
                                st.text(f"Значение: {history_item['value']}")
                        else:
                            st.text("Значение: Пусто")
                        st.markdown("---")

            # Определяем значение для предзаполнения
            if selected_version != "Текущая (новая версия)":
                version_index = version_options.index(selected_version) - 1
                selected_history = field_history[version_index]
                prefill_value = selected_history['value']

                # Показываем информацию о выбранной версии
                st.markdown(f"""
                <div class="version-info">
                    📅 <strong>Дата изменения:</strong> {datetime.fromisoformat(selected_history['timestamp']).strftime('%d.%m.%Y %H:%M')}<br>
                    👤 <strong>Автор:</strong> {selected_history['author']}<br>
                    🔢 <strong>ID версии:</strong> {selected_history['version_id']}
                </div>
                """, unsafe_allow_html=True)
            else:
                prefill_value = current_doc_data.get(field_name, "")
        else:
            prefill_value = current_doc_data.get(field_name, "")

        # Отображаем поле ввода в зависимости от типа
        if field_type == "text_area":
            # Показываем подсветку изменений если выбрана старая версия
            if selected_doc_name != "Новый документ" and field_history:
                current_value = current_doc_data.get(field_name, "")
                if prefill_value and current_value and prefill_value != current_value:
                    st.markdown("**Изменения в тексте:**")
                    highlighted = highlight_text_differences(current_value, prefill_value)
                    st.markdown(
                        f'<div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">{highlighted}</div>',
                        unsafe_allow_html=True)
                    st.markdown("---")

            form_data[field_name] = st.text_area(
                "",
                value=prefill_value,
                placeholder=f"Введите {field_label.lower()}...",
                height=120,
                key=f"text_{field_name}"
            )

        elif field_type == "text":
            form_data[field_name] = st.text_input(
                "",
                value=prefill_value,
                placeholder=f"Введите {field_label.lower()}...",
                key=f"text_input_{field_name}"
            )

        elif field_type == "number":
            num_val = float(prefill_value) if prefill_value else 0.0

            form_data[field_name] = st.number_input(
                "",
                value=num_val,
                key=f"number_{field_name}"
            )

        elif field_type == "select":
            options = field_config.get('options', [])
            selected_option = prefill_value if prefill_value in options else options[0] if options else ""

            form_data[field_name] = st.selectbox(
                "",
                options=options,
                index=options.index(selected_option) if selected_option in options else 0,
                key=f"select_{field_name}"
            )

        elif field_type == "multi_select":
            options = field_config.get('options', [])
            selected_options = prefill_value if isinstance(prefill_value, list) else []

            form_data[field_name] = st.multiselect(
                "",
                options=options,
                default=selected_options,
                key=f"multi_{field_name}"
            )

        elif field_type == "date":
            date_val = datetime.now().date()
            if prefill_value:
                try:
                    if '-' in prefill_value:
                        date_val = datetime.strptime(prefill_value, '%Y-%m-%d').date()
                    elif '.' in prefill_value:
                        date_val = datetime.strptime(prefill_value, '%d.%m.%Y').date()
                except:
                    pass

            form_data[field_name] = st.date_input(
                "",
                value=date_val,
                key=f"date_{field_name}"
            )

        st.markdown("---")