from datetime import datetime
from typing import List, Dict

def format_date_range(start_date, end_date):
    if end_date:
        return f"{start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')}"
    else:
        return f"{start_date.strftime('%d.%m.%Y')}"

def format_items_list(items: List[Dict]) -> str:
    if not items:
        return "Не указано"

    formatted_lines = []
    for i, item in enumerate(items, 1):
        if isinstance(item, dict):
            description = item.get('description', '')
            responsible = item.get('responsible', '')
            amount = item.get('amount', '')
            reference = item.get('reference', '')
        else:
            description = str(item)
            responsible = ''
            amount = ''
            reference = ''

        line_parts = [f"{i}. {description}"]

        if responsible:
            line_parts.append(f"\n   Ответственное лицо: {responsible}")
        if amount:
            line_parts.append(f"\n   Сумма: {amount} руб")
        if reference:
            line_parts.append(f"\n   Справочно: {reference}")

        formatted_lines.append(''.join(line_parts))

    return '\n\n'.join(formatted_lines)

def format_dated_items(items: List[Dict]) -> str:
    """Форматирует пункты с датами в текст с правильной нумерацией"""
    if not items:
        return "Не указано"

    formatted_lines = []
    for i, item in enumerate(items, 1):
        if isinstance(item, dict):
            date_range = item.get('date_range', '')
            description = item.get('description', '')
            responsible = item.get('responsible', '')
            amount = item.get('amount', '')
            reference = item.get('reference', '')
        else:
            date_range = ''
            description = str(item)
            responsible = ''
            amount = ''
            reference = ''

        line_parts = [f"{i}. {date_range} - {description}"]

        if responsible:
            line_parts.append(f"\n   Ответственное лицо: {responsible}")
        if amount:
            line_parts.append(f"\n   Сумма: {amount} руб")
        if reference:
            line_parts.append(f"\n   Справочно: {reference}")

        formatted_lines.append(''.join(line_parts))

    return '\n\n'.join(formatted_lines)

def format_participants_list(selected_participants: List[str], additional_participants: str) -> str:
    """Форматирует список участников для документа"""
    result = []

    for i, participant in enumerate(selected_participants, 1):
        result.append(f"{i}. {participant}")

    if additional_participants and additional_participants.strip():
        result.append("\nДополнительные участники:")
        additional_lines = additional_participants.strip().split('\n')
        for i, line in enumerate(additional_lines, len(selected_participants) + 1):
            if line.strip():
                result.append(f"{i}. {line.strip()}")

    return '\n'.join(result) if result else "Не указано"

def format_business_processes(items: List[Dict]) -> str:
    """Форматирует таблицу бизнес-процессов"""
    if not items:
        return "Не указано"

    header = "Код бизнес-процесса | Название бизнес-процесса | Владелец процесса | Участники процесса\n"
    separator = "--- | --- | --- | ---\n"

    rows = []
    for item in items:
        if isinstance(item, dict):
            code = item.get('code', '')
            name = item.get('business_process_name', '')
            owner = item.get('process_owner', '')
            participants = item.get('participants_process', '')
            rows.append(f"{code} | {name} | {owner} | {participants}")

    return header + separator + "\n".join(rows)

def format_lss_assessment(items: List[Dict]) -> str:
    """Форматирует таблицу оценки LSS"""
    if not items:
        return "Не указано"

    header = "Процесс | Область проверки процесса | Кол-во проверенных экземпляров процесса, % | Кол-во выявленных отклонений, млн шт. | Уровень отклонений, % | Сигма процесса, σ\n"
    separator = "--- | --- | --- | --- | --- | ---\n"

    rows = []
    for item in items:
        if isinstance(item, dict):
            process = item.get('process', '')
            area = item.get('process_verification_area', '')
            verified = item.get('number_of_verified_copys', '')
            deviations = item.get('number_of_reported_points', '')
            level = item.get('rate', '')
            sigma = item.get('sigma', '')
            rows.append(f"{process} | {area} | {verified} | {deviations} | {level} | {sigma}")

    return header + separator + "\n".join(rows)