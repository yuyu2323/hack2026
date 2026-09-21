"""시안01·02의 실제 미디어 허용200을 먼저 확인한 뒤 역할 거부를 대조한다."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path.cwd()
CONCEPT = int(sys.argv[1]) if len(sys.argv) > 1 else 1
assert CONCEPT in (1, 2)
OUT = ROOT / f'execute/workHitory/integration-concept-{CONCEPT:02d}'
BASE = f'http://127.0.0.1:{5172 + CONCEPT}'
SOUTH_BASELINE = '3fdb0cf3-61da-4008-84c1-79e2a58cde05'
checks = []
report = {'status': 'RUNNING', 'started_at': datetime.now(timezone.utc).isoformat(), 'concept': CONCEPT,
          'scope': 'localhost Vite 프록시 독립 HTTP 세션; CSRF/login/logout 외에는 GET만 사용; AI·Browser·업무 쓰기 없음',
          'checks': checks, 'http': [], 'sessions': []}


def need(value):
    if not value:
        raise ValueError('검사 선행조건 미충족')


def check(name, value):
    checks.append({'check': name, 'status': 'PASS' if value else 'FAIL'})


def request(client, role, path, status, sha=None):
    response = client.get(path)
    valid = response.status_code == status
    item = {'login_id': role, 'method': 'GET', 'path': path, 'expected_status': status, 'status': response.status_code}
    if status in (403, 404):
        # 예상과 다른 이미지 응답도 본문을 디코딩하지 않고 실패로 남긴다.
        body = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
        item['error_code'] = body.get('error', {}).get('code')
        item['business_body_absent'] = set(body) <= {'error', 'request_id'} and item['error_code'] == ('FORBIDDEN' if status == 403 else 'NOT_FOUND')
        valid = valid and item['business_body_absent']
    elif path.startswith('/api/media/'):
        item['content_type'] = response.headers.get('content-type', '')
        valid = valid and item['content_type'].startswith('image/') and bool(response.content)
        if sha:
            item['sha256'] = hashlib.sha256(response.content).hexdigest()
            valid = valid and item['sha256'] == sha
    item['result'] = 'PASS' if valid else 'FAIL'
    report['http'].append(item)
    check(role + ':' + path, valid)
    return response


try:
    candidates = []
    for path in OUT.glob('independent-ai-metadata*.json'):
        data = json.loads(path.read_text())
        if data['status'] == 'PASS':
            candidates.append((data['finished_at'], path, data))
    need(candidates)
    _, metadata_path, metadata = max(candidates, key=lambda x: x[0])
    report['metadata_evidence'] = str(metadata_path.relative_to(ROOT))
    report['metadata_sha256'] = hashlib.sha256(metadata_path.read_bytes()).hexdigest()
    submissions = metadata['submissions']
    media = {}
    for row in submissions:
        for photo in row['photos']:
            need(photo['photo_id'] != photo['media_id'])
            media[photo['media_id']] = {'sha256': photo['sha256'], 'kind': 'submission'}
        for ref in row['references']:
            media[ref['media_id']] = {'sha256': ref['sha256'], 'kind': 'reference', 'store_specific': ref['store_specific']}
    report['targets'] = {'submission_ids': [r['submission_id'] for r in submissions],
                         'media': [{'media_id': key, **value} for key, value in media.items()],
                         'regional_allowed_baseline': SOUTH_BASELINE}
    credentials = json.loads((ROOT / '.local/demo-credentials').read_text())
    roles = {'owner.north': 'store_owner', 'operator.demo': 'platform_operator', 'regional.south': 'regional'}
    owner_baseline_ok = False
    for role, expected_role in roles.items():
        if role != 'owner.north':
            need(owner_baseline_ok)
        session = {'login_id': role, 'csrf_status': None, 'login_status': None, 'logout_status': None}
        report['sessions'].append(session)
        with httpx.Client(base_url=BASE, trust_env=False, timeout=20, follow_redirects=False) as client:
            csrf = None
            try:
                response = client.get('/api/auth/csrf')
                session['csrf_status'] = response.status_code
                need(response.status_code == 200)
                csrf = response.json()['csrf_token']
                response = client.post('/api/auth/login', json={'login_id': role, 'password': credentials[role]['password']},
                                       headers={'Origin': BASE, 'X-CSRF-Token': csrf})
                session['login_status'] = response.status_code
                need(response.status_code == 200)
                body = response.json()
                csrf = body['csrf_token']
                check(role + ':expected_role', body['account']['role'] == expected_role)
                if role == 'owner.north':
                    for row in submissions:
                        response = request(client, role, f"/api/submissions/{row['submission_id']}", 200)
                        body = response.json()
                        check(row['submission_id'] + ':owner_snapshot_and_media', body['context']['snapshot_sha256'] == row['snapshot_sha256']
                              and {p['media_id'] for p in body['photos']} == {p['media_id'] for p in row['photos']})
                    for ident, value in media.items():
                        request(client, role, f'/api/media/{ident}', 200, value['sha256'])
                        request(client, role, f'/api/media/{ident}?variant=thumbnail', 200)
                    owner_baseline_ok = all(x['status'] == 'PASS' for x in checks)
                    check('owner_all_real_media_baselines_pass', owner_baseline_ok)
                else:
                    expected = 403 if role == 'operator.demo' else 404
                    if role == 'regional.south':
                        response = request(client, role, f'/api/submissions/{SOUTH_BASELINE}', 200)
                        need(response.status_code == 200)
                    for row in submissions:
                        request(client, role, f"/api/submissions/{row['submission_id']}", expected)
                    for ident, value in media.items():
                        # 공통 Reference는 타지역의 허용 관리 범위에도 속하므로 404 대상이 아니다.
                        media_expected = 200 if role == 'regional.south' and value['kind'] == 'reference' and not value['store_specific'] else expected
                        request(client, role, f'/api/media/{ident}', media_expected, value['sha256'] if media_expected == 200 else None)
                        request(client, role, f'/api/media/{ident}?variant=thumbnail', media_expected)
            finally:
                if csrf is not None:
                    response = client.post('/api/auth/logout', json={}, headers={'Origin': BASE, 'X-CSRF-Token': csrf})
                    session['logout_status'] = response.status_code
                    check(role + ':logout', response.status_code == 204)
    report['status'] = 'PASS' if all(x['status'] == 'PASS' for x in checks) else 'FAIL'
except Exception as error:
    report['status'] = 'FAIL'
    report['failure_type'] = type(error).__name__
    report['failure_detail'] = '자격값·본문 보호를 위해 예외 원문과 traceback은 기록하지 않는다.'
finally:
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    path = OUT / 'independent-live-http.json'
    if path.exists():
        path = path.with_name(path.stem + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.json')
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    path.chmod(0o600)
    print(json.dumps({'status': report['status'], 'checks': len(checks), 'http_requests': len(report['http']),
                      'failed_checks': [x['check'] for x in checks if x['status'] == 'FAIL'], 'failure_type': report.get('failure_type'),
                      'sessions': report['sessions'], 'evidence': str(path.relative_to(ROOT))}, ensure_ascii=False))
    if report['status'] != 'PASS':
        raise SystemExit(1)
