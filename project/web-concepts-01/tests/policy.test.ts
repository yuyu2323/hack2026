import test from 'node:test';
import assert from 'node:assert/strict';
import {roleHome, canVisit, uploadError, pollingInterval, rateLabel, drilldown} from '../src/shared/policy.ts';

test('역할별 시작과 직접 URL 경계를 구분한다', () => {
  assert.equal(roleHome('store_owner'), '/store-owner');
  assert.equal(roleHome('regional'), '/ofc-admin');
  assert.equal(roleHome('platform_operator'), '/platform-admin');
  assert.equal(canVisit('store_owner', '/store-owner/history'), true);
  assert.equal(canVisit('store_owner', '/store-owner-attack'), false);
  assert.equal(canVisit('platform_operator', '/ofc-admin'), false);
});
test('사진과 질문 한도를 제출 전에 안내한다', () => {
  assert.match(uploadError([], '')!, /사진/);
  assert.match(uploadError([{type:'image/gif',size:100}], '')!, /JPEG/);
  assert.match(uploadError([{type:'image/png',size:10485761}], '')!, /10/);
  assert.match(uploadError([{type:'image/png',size:100}], '가'.repeat(2001))!, /2,000/);
  assert.equal(uploadError([{type:'image/jpeg',size:100}], '앞줄을 어떻게 정리할까요?'), null);
});
test('기술 실패와 성공에서 polling을 멈추고 unknown 평가는 작업상태가 아니다', () => {
  assert.equal(pollingInterval('queued'), 2000);
  assert.equal(pollingInterval('running'), 2000);
  assert.equal(pollingInterval('succeeded'), false);
  assert.equal(pollingInterval('failed'), false);
  assert.equal(pollingInterval(undefined), false);
});
test('판단 불가 null을 준수율 0으로 꾸미지 않는다', () => {
  assert.equal(rateLabel(null), '—');
  assert.equal(rateLabel(0), '0%');
  assert.equal(rateLabel(83.3), '83.3%');
});
test('관제 drilldown은 동일 범위·기간·활성 조건을 보존한다', () => {
  assert.deepEqual(drilldown({region_id:'north',date_from:'2026-09-01',is_active:false,page:4},{unresolved:true}), {region_id:'north',date_from:'2026-09-01',is_active:false,unresolved:true});
});

test('상위 기준과 공통 Reference에 허용되지 않은 수정 행동을 표시하지 않는다', async () => {
  const {canEditGuideline,canEditReference}=await import('../src/shared/policy.ts');
  assert.equal(canEditGuideline('ofc','north',{level:'HQ'}),false);
  assert.equal(canEditGuideline('regional','north',{level:'REGION',region_id:'south'}),false);
  assert.equal(canEditGuideline('regional','north',{level:'REGION',region_id:'north'}),true);
  assert.equal(canEditGuideline('ofc','north',{level:'CATEGORY',store_id:null}),false);
  assert.equal(canEditGuideline('hq',null,{level:'HQ'}),true);
  assert.equal(canEditReference('ofc',{store_id:null}),false);
  assert.equal(canEditReference('regional',{store_id:'scoped-store'}),true);
});
