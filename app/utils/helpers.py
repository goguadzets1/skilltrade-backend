def flatten_ids(data: list, field="skill_id") -> list:
    return [row[field] for row in data if field in row]
