import os
import re
import json
import uuid
from datetime import datetime, date
from typing import List, Dict, Optional
import difflib


def ensure_versions_dir():
    """Создает директорию для хранения версий"""
    versions_dir = "versions"
    if not os.path.exists(versions_dir):
        os.makedirs(versions_dir)
    return versions_dir


def get_document_filename(document_name: str) -> str:
    """Генерирует имя файла на основе названия документа"""
    safe_name = re.sub(r'[^\w\s-]', '', document_name)
    safe_name = re.sub(r'[-\s]+', '_', safe_name)
    return safe_name[:100]


def save_document_version(document_data: Dict, author: str, template_name: str):
    """Сохраняет документ в два файла"""
    versions_dir = ensure_versions_dir()

    def convert_dates(obj):
        if isinstance(obj, (datetime, date)):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, dict):
            return {key: convert_dates(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_dates(item) for item in obj]
        else:
            return obj

    serializable_data = convert_dates(document_data)
    document_name = serializable_data.get('audit_report', 'Без названия')
    safe_filename = get_document_filename(document_name)

    version_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    version_info = {
        "version_id": version_id,
        "timestamp": timestamp,
        "author": author,
        "template_used": template_name,
        "data": serializable_data
    }

    # Сохраняем последнюю версию
    latest_file = os.path.join(versions_dir, f"latest_{safe_filename}.json")
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(version_info, f, ensure_ascii=False, indent=2)

    # Обновляем историю
    history_file = os.path.join(versions_dir, f"history_{safe_filename}.json")

    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
    else:
        history_data = {
            "document_name": document_name,
            "versions": []
        }

    history_data["versions"].append(version_info)

    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)

    return version_id


def load_latest_version(document_name: str) -> Optional[Dict]:
    """Загружает последнюю актуальную версию документа"""
    versions_dir = ensure_versions_dir()
    safe_filename = get_document_filename(document_name)
    latest_file = os.path.join(versions_dir, f"latest_{safe_filename}.json")

    if os.path.exists(latest_file):
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None


def load_document_history(document_name: str) -> Optional[Dict]:
    """Загружает историю версий документа"""
    versions_dir = ensure_versions_dir()
    safe_filename = get_document_filename(document_name)
    history_file = os.path.join(versions_dir, f"history_{safe_filename}.json")

    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None


def get_field_history(document_name: str, field_name: str) -> List[Dict]:
    """Получает историю изменений конкретного поля"""
    history = load_document_history(document_name)
    if not history or "versions" not in history:
        return []

    field_history = []

    for version in history["versions"]:
        if "data" in version and field_name in version["data"]:
            field_history.append({
                "timestamp": version["timestamp"],
                "author": version["author"],
                "value": version["data"][field_name],
                "version_id": version["version_id"][:8]
            })

    return field_history


def get_all_documents() -> List[Dict]:
    """Получает список всех документов (по последним версиям)"""
    versions_dir = ensure_versions_dir()
    documents = []

    for filename in os.listdir(versions_dir):
        if filename.startswith("latest_") and filename.endswith(".json"):
            filepath = os.path.join(versions_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                    documents.append({
                        "name": version_data.get("data", {}).get("audit_report", "Без названия"),
                        "filename": filename.replace("latest_", "").replace(".json", ""),
                        "last_modified": version_data.get("timestamp"),
                        "author": version_data.get("author"),
                        "template": version_data.get("template_used")
                    })
            except:
                continue

    documents.sort(key=lambda x: x.get("last_modified", ""), reverse=True)
    return documents


def highlight_text_differences(old_text: str, new_text: str) -> str:
    """Подсвечивает различия между двумя текстами"""
    if not old_text or not new_text:
        return new_text

    if old_text == new_text:
        return new_text

    differ = difflib.Differ()
    diff = list(differ.compare(old_text.splitlines(), new_text.splitlines()))

    highlighted_lines = []
    for line in diff:
        if line.startswith('  '):
            highlighted_lines.append(line[2:])
        elif line.startswith('- '):
            highlighted_lines.append(
                f'<span style="background-color: #ffcccc; text-decoration: line-through;">{line[2:]}</span>')
        elif line.startswith('+ '):
            highlighted_lines.append(f'<span style="background-color: #ccffcc;">{line[2:]}</span>')

    return '<br>'.join(highlighted_lines)