import os
import streamlit as st
from typing import Dict


def get_available_templates():
    templates = []
    template_dir = "templates"

    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
        st.warning(f"Создана папка '{template_dir}'. Добавьте туда ваши шаблоны DOCX.")

    for file in os.listdir(template_dir):
        if file.endswith('.docx'):
            templates.append(file)

    return templates


def get_template_fields(template_name: str) -> Dict:
    """Возвращает конфигурацию полей для конкретного шаблона"""
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

    template_configs = {
        "word_tpl.docx": {
            "name": "Основной шаблон аудита",
            "fields": {
                "audit_report": {"type": "text_area", "required": True, "label": "Акт аудиторской проверки *"},
                "basis_for_verify": {"type": "text_area", "required": True,
                                     "label": "Основание для проведения проверки *"},
                "working_group": {"type": "text_area", "required": True, "label": "Состав рабочей группы *"},
                "verification_period_title": {"type": "label", "label": "Сроки проведения проверки *"},
                "verification_period": {"type": "date_range", "required": True, "label": "Сроки проведения проверки *"},
                "held_events": {"type": "text_area", "required": True, "label": "Проведенные мероприятия *"},
                "established_items": {"type": "dynamic_list_with_dates",
                                      "label": "В ходе проверочных мероприятий установлено"},
                "violation_items": {"type": "dynamic_list",
                                    "label": "В ходе проверочных мероприятий выявлены нарушения"},
                "summary_items": {"type": "dynamic_list", "label": "Выводы"},
                "recommendation_items": {"type": "dynamic_list", "label": "Рекомендации"},
            }
        },
        "application_template.docx": {
            "name": "Шаблон заявки на аудит",
            "fields": {
                # Основная информация
                "state": {"type": "select", "required": True, "label": "Город *",
                          "options": ["г. Москва", "г. Екатеринбург", "г. Санкт-Петербург"]},
                "generated_date": {"type": "date", "required": True, "label": "Дата создания документа *"},
                "audit_report": {"type": "text_area", "required": True,
                                 "label": "Название акта аудиторской проверки *"},
                "basis_for_verify": {"type": "text_area", "required": True,
                                     "label": "Основание аудиторской проверки *"},

                # Состав аудиторской группы (динамический)
                "audit_group": {"type": "participant_group_simple", "required": True,
                                "label": "Состав аудиторской группы *"},

                # Сроки проверки (фиксированные под заголовками)
                "verification_period_title": {"type": "label", "label": "Сроки проведения аудиторской проверки:"},
                "start_date": {"type": "date", "required": True, "label": "Начало проверки *"},
                "end_date": {"type": "date", "required": True, "label": "Окончание проверки *"},

                # Номер мероприятия
                "event_number": {"type": "text", "required": False,
                                 "label": "Номер контрольного мероприятия в АС СУП СВА"},

                # Проверенный период (фиксированные под заголовками)
                "checked_period_title": {"type": "label", "label": "Проверенный период:"},
                "checked_start_date": {"type": "date", "required": True, "label": "Начало проверенного периода *"},
                "checked_end_date": {"type": "date", "required": True, "label": "Конец проверенного периода *"},

                # Информация о проверенных бизнес-процессах (динамическая таблица)
                "business_processes_title": {"type": "label", "label": "1. Информация о проверенных бизнес-процессах:"},
                "business_processes": {"type": "business_process_table", "label": "Бизнес-процессы"},

                # Охват проверки (динамический список)
                "scope_title": {"type": "label", "label": "Охват проверки:"},
                "scope_of_verification": {"type": "dynamic_list", "label": "Охват проверки"},

                # Описание процесса
                "process_description_title": {"type": "label", "label": "Описание процесса:"},
                "process_description": {"type": "text_area", "required": False, "label": "Описание процесса"},

                # Оценка качества LSS (таблица)
                "lss_title": {"type": "label", "label": "2. Оценка качества проверенных процессов по методологии LSS"},
                "lss_assessment": {"type": "lss_table", "label": "Таблица LSS"},

                # Факты проблем
                "problem_facts_title": {"type": "label",
                                        "label": "3. Факты, подтверждающие наличие проблем в бизнес-процессе:"},
                "problem_facts": {"type": "problem_facts_list", "label": "Факты проблем"},

                # Факты возможностей
                "opportunity_facts_title": {"type": "label",
                                            "label": "4. Факты, подтверждающие наличие возможности в бизнес-процессе:"},
                "opportunity_facts": {"type": "opportunity_facts_list", "label": "Факты возможностей"},

                # Сформулированные проблемы
                "formulated_problems_title": {"type": "label", "label": "5. Сформулирована проблема:"},
                "formulated_problems": {"type": "formulated_problems_list", "label": "Сформулированные проблемы"},

                # Сформулированные возможности
                "formulated_opportunities_title": {"type": "label", "label": "6. Сформулирована возможность:"},
                "formulated_opportunities": {"type": "formulated_opportunities_list",
                                             "label": "Сформулированные возможности"},

                # Подписи
                "audit_leader": {"type": "select", "required": False, "label": "Руководитель проверки",
                                 "options": predefined_participants},
                "audit_curator": {"type": "select", "required": False, "label": "Куратор проверки",
                                  "options": predefined_participants},
                "direction_leader": {"type": "select", "required": False, "label": "Руководитель направления УВА",
                                     "options": predefined_participants},
            }
        }
    }

    return template_configs.get(template_name, template_configs["word_tpl.docx"])