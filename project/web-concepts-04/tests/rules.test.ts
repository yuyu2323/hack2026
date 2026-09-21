import {describe,it,expect} from 'vitest';
import {roleHome,safeReturn,validatePhotos,rate,listHref,hasBusinessInbox} from '../src/shared/rules';
describe('현재 역할과 제출 경계',()=>{
 it('PD-003 운영자에게 영업 알림을 열지 않는다',()=>{expect(hasBusinessInbox('platform_operator')).toBe(false);for(const role of ['store_owner','ofc','regional','hq'])expect(hasBusinessInbox(role)).toBe(true);});
 it('안전한 동일 역할 복귀만 허용한다',()=>{expect(roleHome('ofc')).toBe('/ofc-admin');expect(safeReturn('/platform-admin/accounts','store_owner')).toBe('/store-owner');expect(safeReturn('//external.test','hq')).toBe('/ofc-admin');expect(safeReturn('/store-owner/history?page=2','store_owner')).toBe('/store-owner/history?page=2');});
 it('장수 용량과 실제 제출 가능한 형식을 검증한다',()=>{expect(validatePhotos([])).toBeTruthy();expect(validatePhotos(Array.from({length:6},()=>({name:'x.png',type:'image/png',size:100})))).toBeTruthy();expect(validatePhotos([{name:'x.gif',type:'image/gif',size:100}])).toBeTruthy();expect(validatePhotos([{name:'x.png',type:'image/png',size:11*1024*1024}])).toBeTruthy();expect(validatePhotos([{name:'x.png',type:'image/png',size:100}])).toBeNull();});
 it('판단 가능한 기준이 없으면 0점으로 꾸미지 않는다',()=>{expect(rate(null)).toBe('—');expect(rate(0)).toBe('0%');expect(rate(83.3)).toBe('83.3%');});
 it('드릴다운에 필터와 페이지를 보존한다',()=>{expect(listHref('/ofc-admin/submissions','?store_id=demo&page=2')).toBe('/ofc-admin/submissions?store_id=demo&page=2');});
});
