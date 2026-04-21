import streamlit as st
from datetime import datetime
from typing import List, Dict
def render_dynamic_list(field_name: str, field_label: str, items: List[Dict], template_type: str = "dynamic_list"):
    """Рендерит динамический список"""
    st.markdown(f'<div class="section-header">{field_label}</div>', unsafe_allow_html=True)

    # Отображение существующих пунктов
    for i, item in enumerate(items):
        with st.expander(f"Пункт {i+1}", expanded=True):
            if template_type == "dynamic_list":
                render_dynamic_list_item(field_name, i, item)
            elif template_type == "dynamic_list_with_dates":
                render_dynamic_list_with_dates_item(field_name, i, item)
            elif template_type == "business_process_list":
                render_business_process_item(field_name, i, item)
            elif template_type == "lss_assessment_list":
                render_lss_assessment_item(field_name, i, item)

            # Кнопка удаления
            with st.form(f"del_form_{field_name}_{i}"):
                if st.form_submit_button(f"❌ Удалить пункт {i+1}"):
                    items.pop(i)
                    st.rerun()

    # Кнопка добавления
    if st.button(f"➕ Добавить пункт в '{field_label}'", key=f"add_btn_{field_name}"):
        if template_type == "dynamic_list":
            items.append({
                'description': '',
                'responsible': '',
                'amount': ''
            })
        elif template_type == "dynamic_list_with_dates":
            items.append({
                'description': '',
                'start_date': datetime.now().date(),
                'end_date': None,
                'date_range': '',
                'responsible': '',
                'amount': '',
                'reference': ''
            })
        elif template_type == "business_process_list":
            items.append({
                'code': '',
                'business_process_name': '',
                'process_owner': '',
                'participants_process': ''
            })
        elif template_type == "lss_assessment_list":
            items.append({
                'process': '',
                'process_verification_area': '',
                'number_of_verified_copys': '',
                'number_of_reported_points': '',
                'rate': '',
                'sigma': ''
            })
        st.rerun()

def render_dynamic_list_item(field_name: str, index: int, item: Dict):
    """Рендерит элемент динамического списка"""
    col1, col2 = st.columns([3, 1])

    with col1:
        item_description = st.text_area(
            f"Описание {index+1}",
            value=item.get('description', '') if isinstance(item, dict) else '',
            placeholder="Введите описание...",
            height=100,
            key=f"{field_name}_desc_{index}"
        )

    with col2:
        item_responsible = st.text_input(
            f"Ответственное лицо {index+1}",
            value=item.get('responsible', '') if isinstance(item, dict) else '',
            placeholder="ФИО",
            key=f"{field_name}_resp_{index}"
        )
        item_amount = st.text_input(
            f"Сумма {index+1}",
            value=item.get('amount', '') if isinstance(item, dict) else '',
            placeholder="Сумма",
            key=f"{field_name}_amount_{index}"
        )

    # Обновляем данные
    if isinstance(item, dict):
        item.update({
            'description': item_description,
            'responsible': item_responsible,
            'amount': item_amount
        })

def render_dynamic_list_with_dates_item(field_name: str, index: int, item: Dict):
    """Рендерит элемент динамического списка с датами"""
    col1, col2 = st.columns([3, 1])

    with col1:
        item_description = st.text_area(
            f"Описание {index+1}",
            value=item.get('description', '') if isinstance(item, dict) else '',
            placeholder="Опишите что было установлено...",
            height=100,
            key=f"{field_name}_desc_{index}"
        )

    with col2:
        # Обработка дат
        item_start_date = item.get('start_date', datetime.now().date()) if isinstance(item, dict) else datetime.now().date()
        if isinstance(item_start_date, str):
            try:
                item_start_date = datetime.strptime(item_start_date, '%Y-%m-%d').date()
            except:
                item_start_date = datetime.now().date()

        item_end_date = item.get('end_date', None) if isinstance(item, dict) else None
        if item_end_date and isinstance(item_end_date, str):
            try:
                item_end_date = datetime.strptime(item_end_date, '%Y-%m-%d').date()
            except:
                item_end_date = None

        col_date1, col_date2 = st.columns(2)
        with col_date1:
            item_start_date = st.date_input(
                f"Начало периода {index+1}",
                value=item_start_date,
                key=f"{field_name}_start_{index}"
            )

        with col_date2:
            use_end_date = st.checkbox(
                "Указать окончание",
                value=bool(item_end_date),
                key=f"{field_name}_use_end_{index}"
            )
            if use_end_date:
                item_end_date = st.date_input(
                    f"Окончание периода {index+1}",
                    value=item_end_date or datetime.now().date() + timedelta(days=7),
                    min_value=item_start_date,
                    key=f"{field_name}_end_{index}"
                )
            else:
                item_end_date = None

        item_responsible = st.text_input(
            f"Ответственное лицо {index+1}",
            value=item.get('responsible', '') if isinstance(item, dict) else '',
            placeholder="ФИО",
            key=f"{field_name}_resp_{index}"
        )

        item_amount = st.text_input(
            f"Сумма {index+1}",
            value=item.get('amount', '') if isinstance(item, dict) else '',
            placeholder="Сумма",
            key=f"{field_name}_amount_{index}"
        )

        # Поле "Справочно"
        item_reference = st.text_input(
            f"Справочно {index+1}",
            value=item.get('reference', '') if isinstance(item, dict) else '',
            placeholder="Комментарий (опционально)",
            key=f"{field_name}_ref_{index}"
        )

    # Обновляем данные
    if isinstance(item, dict):
        item.update({
            'description': item_description,
            'start_date': item_start_date,
            'end_date': item_end_date if use_end_date else None,
            'date_range': format_date_range(item_start_date, item_end_date if use_end_date else None),
            'responsible': item_responsible,
            'amount': item_amount,
            'reference': item_reference
        })

def render_participant_group_simple(field_name: str, field_label: str, items: List[Dict]):
    """Рендерит состав аудиторской группы: слева участник, справа выбор должности"""
    st.markdown(f'<div class="section-header">{field_label}</div>', unsafe_allow_html=True)

    predefined_participants = [
        "Давыденко О. В. - главный аудитор-аналитик данных Отдела аудита обеспечивающих процессов Управления внутреннего аудита",
        "Селезнева Н. С. - начальник ОАОП УВА по Уральскому банку",
        "Киселева А. А. - аудитор-аналитик данных Отдела аудита обеспечивающих процессов Управления внутреннего аудита",
    ]

    participant_positions = [
        "Куратор проверки",
        "Руководитель проверки",
        "Руководитель направления УВА"
    ]

    # Показываем существующих участников
    for i, item in enumerate(items):
        col1, col2 = st.columns([3, 1])

        with col1:
            participant = st.selectbox(
                f"Участник {i + 1}",
                options=predefined_participants,
                index=predefined_participants.index(item.get('participant', predefined_participants[0]))
                if item.get('participant') in predefined_participants else 0,
                key=f"{field_name}_participant_{i}"
            )

        with col2:
            position = st.selectbox(
                f"Должность {i + 1}",
                options=participant_positions,
                index=participant_positions.index(item.get('position', participant_positions[0]))
                if item.get('position') in participant_positions else 0,
                key=f"{field_name}_position_{i}"
            )

        # Кнопка удаления справа от выбора
        with st.container():
            if st.button(f"❌ Удалить", key=f"del_participant_{field_name}_{i}"):
                items.pop(i)
                st.rerun()

        # Обновляем данные
        if isinstance(item, dict):
            item.update({
                'participant': participant,
                'position': position
            })

    # Кнопка добавления нового участника снизу
    if st.button(f"➕ Добавить участника", key=f"add_btn_{field_name}"):
        items.append({
            'participant': predefined_participants[0],
            'position': participant_positions[0]
        })
        st.rerun()


def render_business_process_table(field_name: str, field_label: str, items: List[Dict]):
    """Рендерит таблицу бизнес-процессов (4 поля в строке)"""
    # Заголовок таблицы
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**Код бизнес-процесса**")
    with col2:
        st.markdown("**Название бизнес-процесса**")
    with col3:
        st.markdown("**Владелец процесса**")
    with col4:
        st.markdown("**Участники процесса**")

    # Показываем существующие строки
    for i, item in enumerate(items):
        cols = st.columns(4)

        with cols[0]:
            code = st.text_input(
                f"Код {i + 1}",
                value=item.get('code', ''),
                placeholder="Код",
                key=f"{field_name}_code_{i}",
                label_visibility="collapsed"
            )

        with cols[1]:
            business_process_name = st.text_input(
                f"Название {i + 1}",
                value=item.get('business_process_name', ''),
                placeholder="Название",
                key=f"{field_name}_name_{i}",
                label_visibility="collapsed"
            )

        with cols[2]:
            process_owner = st.text_input(
                f"Владелец {i + 1}",
                value=item.get('process_owner', ''),
                placeholder="Владелец",
                key=f"{field_name}_owner_{i}",
                label_visibility="collapsed"
            )

        with cols[3]:
            participants_process = st.text_input(
                f"Участники {i + 1}",
                value=item.get('participants_process', ''),
                placeholder="Участники",
                key=f"{field_name}_participants_{i}",
                label_visibility="collapsed"
            )

        # Кнопка удаления под строкой
        if st.button(f"❌ Удалить строку {i + 1}", key=f"del_bp_{field_name}_{i}"):
            items.pop(i)
            st.rerun()

        # Обновляем данные
        if isinstance(item, dict):
            item.update({
                'code': code,
                'business_process_name': business_process_name,
                'process_owner': process_owner,
                'participants_process': participants_process
            })

    # Кнопка добавления новой строки
    if st.button(f"➕ Добавить строку бизнес-процесса", key=f"add_bp_btn_{field_name}"):
        items.append({
            'code': '',
            'business_process_name': '',
            'process_owner': '',
            'participants_process': ''
        })
        st.rerun()


def render_lss_table(field_name: str, field_label: str, items: List[Dict]):
    """Рендерит таблицу LSS"""
    # Заголовок таблицы
    cols = st.columns(6)
    headers = ["Процесс", "Область проверки процесса", "Кол-во проверенных экземпляров процесса, %",
               "Кол-во выявленных отклонений, млн шт.", "Уровень отклонений, %", "Сигма процесса, σ"]

    for i, header in enumerate(headers):
        with cols[i]:
            st.markdown(f"**{header}**")

    # Показываем существующие строки
    for i, item in enumerate(items):
        cols = st.columns(6)

        with cols[0]:
            process = st.text_input(
                f"Процесс {i + 1}",
                value=item.get('process', ''),
                placeholder="Процесс",
                key=f"{field_name}_process_{i}",
                label_visibility="collapsed"
            )

        with cols[1]:
            process_verification_area = st.text_input(
                f"Область проверки {i + 1}",
                value=item.get('process_verification_area', ''),
                placeholder="Область проверки",
                key=f"{field_name}_area_{i}",
                label_visibility="collapsed"
            )

        with cols[2]:
            number_of_verified_copys = st.text_input(
                f"Кол-во проверенных экземпляров {i + 1}",
                value=item.get('number_of_verified_copys', ''),
                placeholder="%",
                key=f"{field_name}_verified_{i}",
                label_visibility="collapsed"
            )

        with cols[3]:
            number_of_reported_points = st.text_input(
                f"Кол-во отклонений {i + 1}",
                value=item.get('number_of_reported_points', ''),
                placeholder="млн шт.",
                key=f"{field_name}_deviations_{i}",
                label_visibility="collapsed"
            )

        with cols[4]:
            rate = st.text_input(
                f"Уровень отклонений {i + 1}",
                value=item.get('rate', ''),
                placeholder="%",
                key=f"{field_name}_rate_{i}",
                label_visibility="collapsed"
            )

        with cols[5]:
            sigma = st.text_input(
                f"Сигма процесса {i + 1}",
                value=item.get('sigma', ''),
                placeholder="σ",
                key=f"{field_name}_sigma_{i}",
                label_visibility="collapsed"
            )

        # Кнопка удаления
        if st.button(f"❌ Удалить строку LSS {i + 1}", key=f"del_lss_{field_name}_{i}"):
            items.pop(i)
            st.rerun()

        # Обновляем данные
        if isinstance(item, dict):
            item.update({
                'process': process,
                'process_verification_area': process_verification_area,
                'number_of_verified_copys': number_of_verified_copys,
                'number_of_reported_points': number_of_reported_points,
                'rate': rate,
                'sigma': sigma
            })

    # Кнопка добавления новой строки
    if st.button(f"➕ Добавить строку LSS", key=f"add_lss_btn_{field_name}"):
        items.append({
            'process': '',
            'process_verification_area': '',
            'number_of_verified_copys': '',
            'number_of_reported_points': '',
            'rate': '',
            'sigma': ''
        })
        st.rerun()


def render_problem_facts_list(field_name: str, field_label: str, items: List[Dict]):
    """Рендерит список фактов проблем с доходами/расходами"""
    for i, item in enumerate(items):
        with st.expander(f"Факт проблемы {i + 1}", expanded=True):
            # Описание факта
            acts = st.text_area(
                f"Описание факта {i + 1}",
                value=item.get('acts', ''),
                placeholder="Опишите факт, подтверждающий наличие проблемы...",
                height=100,
                key=f"{field_name}_acts_{i}"
            )

            # Доходы и описание
            st.markdown("**Доходы:**")
            col1, col2 = st.columns(2)
            with col1:
                income_acts = st.number_input(
                    f"Сумма доходов {i + 1}",
                    value=float(item.get('income_acts', 0.0)),
                    key=f"{field_name}_income_{i}"
                )
            with col2:
                income_description_acts = st.text_input(
                    f"Описание доходов {i + 1}",
                    value=item.get('income_description_acts', ''),
                    placeholder="Описание",
                    key=f"{field_name}_income_desc_{i}"
                )

            # Расходы и описание
            st.markdown("**Расходы:**")
            col1, col2 = st.columns(2)
            with col1:
                expenses_acts = st.number_input(
                    f"Сумма расходов {i + 1}",
                    value=float(item.get('expenses_acts', 0.0)),
                    key=f"{field_name}_expenses_{i}"
                )
            with col2:
                expenses_description_acts = st.text_input(
                    f"Описание расходов {i + 1}",
                    value=item.get('expenses_description_acts', ''),
                    placeholder="Описание",
                    key=f"{field_name}_expenses_desc_{i}"
                )

            # Кнопка удаления
            if st.button(f"❌ Удалить факт проблемы {i + 1}", key=f"del_problem_{field_name}_{i}"):
                items.pop(i)
                st.rerun()

            # Обновляем данные
            if isinstance(item, dict):
                item.update({
                    'acts': acts,
                    'income_acts': income_acts,
                    'income_description_acts': income_description_acts,
                    'expenses_acts': expenses_acts,
                    'expenses_description_acts': expenses_description_acts
                })

    # Кнопка добавления
    if st.button(f"➕ Добавить факт проблемы", key=f"add_problem_btn_{field_name}"):
        items.append({
            'acts': '',
            'income_acts': 0.0,
            'income_description_acts': '',
            'expenses_acts': 0.0,
            'expenses_description_acts': ''
        })
        st.rerun()


def render_opportunity_facts_list(field_name: str, field_label: str, items: List[Dict]):
    """Рендерит список фактов возможностей с доходами/расходами"""
    for i, item in enumerate(items):
        with st.expander(f"Факт возможности {i + 1}", expanded=True):
            # Описание факта
            facts = st.text_area(
                f"Описание факта {i + 1}",
                value=item.get('facts', ''),
                placeholder="Опишите факт, подтверждающий наличие возможности...",
                height=100,
                key=f"{field_name}_facts_{i}"
            )

            # Доходы и описание
            st.markdown("**Доходы:**")
            col1, col2 = st.columns(2)
            with col1:
                income_facts = st.number_input(
                    f"Сумма доходов {i + 1}",
                    value=float(item.get('income_facts', 0.0)),
                    key=f"{field_name}_income_f_{i}"
                )
            with col2:
                income_description_facts = st.text_input(
                    f"Описание доходов {i + 1}",
                    value=item.get('income_description_facts', ''),
                    placeholder="Описание",
                    key=f"{field_name}_income_desc_f_{i}"
                )

            # Расходы и описание
            st.markdown("**Расходы:**")
            col1, col2 = st.columns(2)
            with col1:
                expenses_facts = st.number_input(
                    f"Сумма расходов {i + 1}",
                    value=float(item.get('expenses_facts', 0.0)),
                    key=f"{field_name}_expenses_f_{i}"
                )
            with col2:
                expenses_description_facts = st.text_input(
                    f"Описание расходов {i + 1}",
                    value=item.get('expenses_description_facts', ''),
                    placeholder="Описание",
                    key=f"{field_name}_expenses_desc_f_{i}"
                )

            # Кнопка удаления
            if st.button(f"❌ Удалить факт возможности {i + 1}", key=f"del_opportunity_{field_name}_{i}"):
                items.pop(i)
                st.rerun()

            # Обновляем данные
            if isinstance(item, dict):
                item.update({
                    'facts': facts,
                    'income_facts': income_facts,
                    'income_description_facts': income_description_facts,
                    'expenses_facts': expenses_facts,
                    'expenses_description_facts': expenses_description_facts
                })

    # Кнопка добавления
    if st.button(f"➕ Добавить факт возможности", key=f"add_opportunity_btn_{field_name}"):
        items.append({
            'facts': '',
            'income_facts': 0.0,
            'income_description_facts': '',
            'expenses_facts': 0.0,
            'expenses_description_facts': ''
        })
        st.rerun()


def render_formulated_problems_list(field_name: str, field_label: str, items: List[Dict]):
    """Рендерит список сформулированных проблем (3 поля)"""
    for i, item in enumerate(items):
        col1, col2, col3 = st.columns(3)

        with col1:
            formulated_problems = st.text_area(
                f"Описание проблемы {i + 1}",
                value=item.get('formulated_problems', ''),
                placeholder="Опишите проблему...",
                height=100,
                key=f"{field_name}_problem_{i}"
            )

        with col2:
            sums_problems = st.number_input(
                f"Сумма {i + 1}",
                value=float(item.get('sums_problems', 0.0)),
                key=f"{field_name}_sum_{i}"
            )

        with col3:
            sums_descriptions_problems = st.text_input(
                f"Описание суммы {i + 1}",
                value=item.get('sums_descriptions_problems', ''),
                placeholder="Описание суммы",
                key=f"{field_name}_sum_desc_{i}"
            )

        # Кнопка удаления справа
        if st.button(f"❌ Удалить", key=f"del_form_problem_{field_name}_{i}"):
            items.pop(i)
            st.rerun()

        # Обновляем данные
        if isinstance(item, dict):
            item.update({
                'formulated_problems': formulated_problems,
                'sums_problems': sums_problems,
                'sums_descriptions_problems': sums_descriptions_problems
            })

    # Кнопка добавления
    if st.button(f"➕ Добавить сформулированную проблему", key=f"add_form_problem_btn_{field_name}"):
        items.append({
            'formulated_problems': '',
            'sums_problems': 0.0,
            'sums_descriptions_problems': ''
        })
        st.rerun()


def render_formulated_opportunities_list(field_name: str, field_label: str, items: List[Dict]):
    """Рендерит список сформулированных возможностей (3 поля)"""
    for i, item in enumerate(items):
        col1, col2, col3 = st.columns(3)

        with col1:
            opportunities = st.text_area(
                f"Описание возможности {i + 1}",
                value=item.get('opportunities', ''),
                placeholder="Опишите возможность...",
                height=100,
                key=f"{field_name}_opportunity_{i}"
            )

        with col2:
            sums_opportunities = st.number_input(
                f"Сумма {i + 1}",
                value=float(item.get('sums_opportunities', 0.0)),
                key=f"{field_name}_sum_opp_{i}"
            )

        with col3:
            descriptions_opportunities = st.text_input(
                f"Описание суммы {i + 1}",
                value=item.get('descriptions_opportunities', ''),
                placeholder="Описание суммы",
                key=f"{field_name}_sum_desc_opp_{i}"
            )

        # Кнопка удаления
        if st.button(f"❌ Удалить", key=f"del_form_opportunity_{field_name}_{i}"):
            items.pop(i)
            st.rerun()

        # Обновляем данные
        if isinstance(item, dict):
            item.update({
                'opportunities': opportunities,
                'sums_opportunities': sums_opportunities,
                'descriptions_opportunities': descriptions_opportunities
            })

    # Кнопка добавления
    if st.button(f"➕ Добавить сформулированную возможность", key=f"add_form_opportunity_btn_{field_name}"):
        items.append({
            'opportunities': '',
            'sums_opportunities': 0.0,
            'descriptions_opportunities': ''
        })
        st.rerun()
