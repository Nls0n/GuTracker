def find_json_differences(old_data, new_data, path="", differences=None):
    """
    Рекурсивно находит различия между двумя JSON-совместимыми структурами данных.

    Args:
        old_data: Исходные данные (dict/list)
        new_data: Новые данные (dict/list)
        path: Текущий путь в структуре (для рекурсии)
        differences: Список для накопления различий (для рекурсии)

    Returns:
        list: Список строк с описанием различий
    """
    if differences is None:
        differences = []

    # Типы данных не совпадают
    if type(old_data) != type(new_data):
        differences.append(f"{path}: Тип изменился с {type(old_data)} на {type(new_data)}")
        return differences

    # Сравнение словарей
    if isinstance(old_data, dict):
        # Проверка удаленных ключей
        for key in old_data.keys() - new_data.keys():
            differences.append(f"{path}.{key}: Ключ удален (значение было: {old_data[key]!r})")

        # Проверка добавленных ключей
        for key in new_data.keys() - old_data.keys():
            differences.append(f"{path}.{key}: Ключ добавлен (новое значение: {new_data[key]!r})")

        # Проверка измененных значений для общих ключей
        for key in old_data.keys() & new_data.keys():
            find_json_differences(
                old_data[key],
                new_data[key],
                f"{path}.{key}" if path else key,
                differences
            )

    # Сравнение списков
    elif isinstance(old_data, list):
        if len(old_data) != len(new_data):
            differences.append(f"{path}: Длина списка изменилась с {len(old_data)} на {len(new_data)}")

        for i, (old_item, new_item) in enumerate(zip(old_data, new_data)):
            find_json_differences(
                old_item,
                new_item,
                f"{path}[{i}]",
                differences
            )

    # Сравнение простых значений
    else:
        if old_data != new_data:
            differences.append(f"{path}: Значение изменилось с {old_data!r} на {new_data!r}")

    return differences


# Пример использования
if __name__ == "__main__":
    old_data = {
        "name": "John",
        "age": 30,
        "skills": ["Python", "pytest", "Docker"],
        "address": {
            "city": "Moscow",
            "street": "Lenina"
        }
    }

    new_data = {
        "name": "John",
        "age": 31,
        "skills": ["Python", "SQL", "Docker"],
        "address": {
            "city": "Moscow",
            "zip": "123456"
        },
        "married": True
    }

    differences = find_json_differences(old_data, new_data)

    print("Обнаружены различия:")
    for diff in differences:
        print(f"- {diff}")