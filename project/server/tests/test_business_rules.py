from io import BytesIO
import hashlib
import pytest
from PIL import Image
from server.guidelines.resolution import resolve_guidelines
from server.submissions.media import normalize_image
from server.analytics.statistics import correlation


def candidate(level, key='facing', store_id=None, category_id=None):
    return {'level': level, 'rule_key': key, 'store_id': store_id, 'category_id': category_id,
            'guideline_id': level + key + str(store_id), 'version_id': level + '-v1', 'version': 1, 'text': level}


def png():
    output = BytesIO()
    Image.new('RGB', (64, 64), '#4c7862').save(output, 'PNG')
    return output.getvalue()


def test_guideline_specific_priority_and_candidate_history():
    rows = [candidate('HQ'), candidate('REGION'), candidate('STORE', store_id='s'),
            candidate('CATEGORY', category_id='c'), candidate('CATEGORY', store_id='s', category_id='c'),
            candidate('HQ', key='label')]
    selected, history = resolve_guidelines(rows)
    assert len(selected) == 2
    assert selected[0]['store_id'] == 's'
    assert selected[0]['level'] == 'CATEGORY'
    assert len(history) == 6 and sum(c['selected'] for c in history) == 2
    assert all(c['selection_reason'] for c in history)


def test_guideline_total_limit_not_silently_truncated():
    rows = [dict(candidate('HQ', key=str(i)), text='기' * 10000) for i in range(4)]
    with pytest.raises(ValueError):
        resolve_guidelines(rows)


def test_media_validates_real_format_and_hash():
    result = normalize_image(png(), 'photo.png', 'image/png')
    assert result['width'] == 64 and result['height'] == 64
    assert result['sha256'] == hashlib.sha256(result['content']).hexdigest()
    assert result['mime_type'] == 'image/png'
    with pytest.raises(ValueError):
        normalize_image(png(), 'photo.jpg', 'image/jpeg')
    with pytest.raises(ValueError):
        normalize_image(b'<svg></svg>', 'photo.png', 'image/png')


def test_correlation_missing_insufficient_and_zero_variance():
    assert correlation([{'compliance_rate': 10, 'sales_amount': None}])['r'] is None
    assert correlation([{'compliance_rate': 10, 'sales_amount': 20}])['reason'] == 'insufficient_samples'
    points = [{'compliance_rate': 10, 'sales_amount': amount} for amount in [10, 20, 30]]
    assert correlation(points)['reason'] == 'zero_variance'
    result = correlation([{'compliance_rate': value, 'sales_amount': value * 20} for value in [20, 30, 40]])
    assert result['n'] == 3 and result['r'] == 1.0
def test_business_input_rejects_blank_required_fields():
    import pytest
    from pydantic import ValidationError
    from server.guidelines.schemas import GuidelineCreate
    with pytest.raises(ValidationError):
        GuidelineCreate(rule_key='facing', title='  ', level='HQ', text='앞줄 정렬', reason='검증')
    with pytest.raises(ValidationError):
        GuidelineCreate(rule_key='Bad.Key', title='정렬', level='HQ', text='앞줄 정렬', reason='검증')
