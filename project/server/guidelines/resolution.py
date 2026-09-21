"""기준 우선순위와 적용 후보 이력을 계산한다."""
LEVEL_ORDER = {'HQ': 0, 'REGION': 1, 'STORE': 2, 'CATEGORY': 3}


def resolve_guidelines(candidates):
    selected = {}
    for candidate in candidates:
        key = candidate['rule_key']
        priority = (LEVEL_ORDER[candidate['level']], bool(candidate.get('store_id')), bool(candidate.get('category_id')))
        previous = selected.get(key)
        if previous is None or priority > previous[0]:
            selected[key] = (priority, candidate)
        elif priority == previous[0]:
            raise ValueError('같은 범위·우선순위의 기준이 중복되었습니다.')
    effective = [dict(selected[key][1]) for key in sorted(selected)]
    if len(effective) > 100 or sum(len(row['text']) for row in effective) > 30000:
        raise ValueError('적용 기준의 개수 또는 본문 한도를 초과했습니다.')
    selected_ids = {row['guideline_id'] for row in effective}
    history = [dict(row, selected=row['guideline_id'] in selected_ids,
                    selection_reason='가장 구체적인 적용 기준' if row['guideline_id'] in selected_ids else '상위 우선순위의 같은 rule_key 기준 적용')
               for row in candidates]
    return effective, history
