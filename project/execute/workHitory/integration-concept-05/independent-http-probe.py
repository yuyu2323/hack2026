"""시안05 보호 미디어·영업 본문을 새 검사 세션에서만 읽는다."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import httpx

ROOT=Path.cwd()
OUT=ROOT/'execute/workHitory/integration-concept-05'
BASE='http://127.0.0.1:5177'
metadata=json.loads((OUT/'independent-pair-metadata.json').read_text())
first=metadata['submissions'][0]
child=metadata['submissions'][1]
photo=first['photos'][0]
MEDIA=photo['media_id']
ISSUE='c4ecb6f5-d284-42f4-bf90-d641e71097e3'
NORTH='e447d4e9-54c0-4c85-a0d6-20597b92d0ba'
checks=[]
report={'status':'RUNNING','started_at':datetime.now(timezone.utc).isoformat(),
        'scope':'독립 실제 HTTP·Vite5177; 별도 CSRF/login/logout 세션만 사용; 브라우저와 별도',
        'target':{'first_submission_id':first['submission_id'],'child_submission_id':child['submission_id'],
                  'issue_id':ISSUE,'photo_id':photo['photo_id'],'media_id':MEDIA,'expected_original_sha256':photo['sha256']},
        'checks':checks,'http':[],'sessions':[]}
def check(name,condition):
    checks.append({'check':name,'status':'PASS' if condition else 'FAIL'})
def need(value):
    if not value: raise ValueError('검사 선행조건 미충족')
def request(client,role,path,status,sha=None):
    response=client.get(path)
    valid=response.status_code==status
    item={'login_id':role,'method':'GET','path':path,'expected_status':status,'status':response.status_code}
    if status in (403,404):
        body=response.json()
        item['error_code']=body.get('error',{}).get('code')
        item['business_body_absent']=set(body)<= {'error','request_id'} and item['error_code']==('FORBIDDEN' if status==403 else 'NOT_FOUND')
        valid=valid and item['business_body_absent']
    elif path.startswith('/api/media/'):
        item['content_type']=response.headers.get('content-type','')
        valid=valid and item['content_type'].startswith('image/') and bool(response.content)
        if sha:
            item['sha256']=hashlib.sha256(response.content).hexdigest()
            valid=valid and item['sha256']==sha
    item['result']='PASS' if valid else 'FAIL'
    report['http'].append(item)
    check(role+':'+path,valid)
    return response
try:
    need(metadata['status']=='PASS')
    need(MEDIA!=photo['photo_id'])
    credentials=json.loads((ROOT/'.local/demo-credentials').read_text())
    roles={'owner.south':'store_owner','operator.demo':'platform_operator','regional.north':'regional'}
    for role,expected_role in roles.items():
        session={'login_id':role,'csrf_status':None,'login_status':None,'logout_status':None}
        report['sessions'].append(session)
        with httpx.Client(base_url=BASE,trust_env=False,timeout=20) as client:
            csrf=None
            try:
                response=client.get('/api/auth/csrf');session['csrf_status']=response.status_code
                need(response.status_code==200);csrf=response.json()['csrf_token']
                response=client.post('/api/auth/login',json={'login_id':role,'password':credentials[role]['password']},
                    headers={'Origin':BASE,'X-CSRF-Token':csrf})
                session['login_status']=response.status_code
                need(response.status_code==200);login=response.json();csrf=login['csrf_token']
                check(role+':expected_role',login['account']['role']==expected_role)
                if role=='owner.south':
                    response=request(client,role,f"/api/submissions/{first['submission_id']}",200)
                    body=response.json()
                    check('owner_detail_matches_stored_media_snapshot',body['context']['snapshot_sha256']==first['snapshot_sha256']
                          and any(p['media_id']==MEDIA for p in body['photos']))
                    request(client,role,f"/api/submissions/{child['submission_id']}",200)
                    response=request(client,role,f'/api/issues/{ISSUE}',200)
                    check('owner_issue_is_child_issue',response.json()['submission_id']==child['submission_id'])
                    request(client,role,f'/api/media/{MEDIA}',200,photo['sha256'])
                    request(client,role,f'/api/media/{MEDIA}?variant=thumbnail',200)
                elif role=='operator.demo':
                    for path in (f"/api/submissions/{first['submission_id']}",f"/api/submissions/{child['submission_id']}",
                                 f'/api/issues/{ISSUE}',f'/api/media/{MEDIA}',f'/api/media/{MEDIA}?variant=thumbnail'):
                        request(client,role,path,403)
                else:
                    request(client,role,f'/api/submissions/{NORTH}',200)
                    for path in (f"/api/submissions/{first['submission_id']}",f'/api/issues/{ISSUE}',
                                 f'/api/media/{MEDIA}',f'/api/media/{MEDIA}?variant=thumbnail'):
                        request(client,role,path,404)
            finally:
                if csrf is not None:
                    response=client.post('/api/auth/logout',json={},headers={'Origin':BASE,'X-CSRF-Token':csrf})
                    session['logout_status']=response.status_code
                    check(role+':logout',response.status_code==204)
    report['status']='PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL'
except Exception:
    report['status']='FAIL'
    report['failure_detail']='본문·자격값 보호를 위해 예외 원문 미기록'
finally:
    report['finished_at']=datetime.now(timezone.utc).isoformat()
    path=OUT/'independent-live-http.json'
    if path.exists():path=path.with_name(path.stem+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json')
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');path.chmod(0o600)
    print(json.dumps({'status':report['status'],'checks':len(checks),'http_checks':len(report['http']),
                      'failed_checks':[c['check'] for c in checks if c['status']=='FAIL'],
                      'sessions':report['sessions'],'evidence':str(path.relative_to(ROOT))},ensure_ascii=False))
    if report['status']!='PASS':raise SystemExit(1)
