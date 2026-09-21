import type { Role } from '@storeloop/api-client';
export const homeFor = (role: Role) => role === 'store_owner' ? '/store-owner' : role === 'platform_operator' ? '/platform-admin' : '/ofc-admin';
export function canVisit(role: Role, path: string) { const home = homeFor(role); return (path === home || path.startsWith(home + '/')) && !(role === 'platform_operator' && path.startsWith('/platform-admin/notifications')); }
export function errorRoute(status: number, code: string) { if (status === 401)
    return '/login'; if ((status === 403 && code !== 'CSRF_INVALID') || status === 404)
    return '/forbidden'; return null; }
export function validatePhotos(files: {
    type: string;
    size: number;
}[], max = 5) { if (!files.length)
    return '사진을 한 장 이상 선택해 주세요.'; if (files.length > max)
    return `사진은 ${max}장까지 선택할 수 있습니다.`; if (files.some(f => !['image/jpeg', 'image/png'].includes(f.type)))
    return 'JPEG 또는 PNG 사진만 선택해 주세요.'; if (files.some(f => f.size > 10 * 1024 * 1024))
    return '사진 한 장은 10MiB 이하여야 합니다.'; return ''; }
export function payloadKey(make = () => crypto.randomUUID()) { let previous = '', key = ''; return (body: unknown, files: unknown[] = []) => { const next = JSON.stringify([body, files]); if (previous !== next) {
    previous = next;
    key = make();
} return key; }; }
export const filterKeys = ['region_id', 'store_id', 'category_id', 'date_from', 'date_to', 'is_active'];
export function filterParams(search: string) { const input = new URLSearchParams(search); const output = new URLSearchParams(); filterKeys.forEach(k => { const v = input.get(k); if (v)
    output.set(k, v); }); return output; }
export const formatRate = (value: number | null | undefined) => value == null ? '—' : `${value}%`;
export function statusLabel(value: string) { return ({ queued: '분석 대기', running: '분석 중', succeeded: '분석 완료', failed: '기술 실패', pass: '준수', fail: '개선 필요', unknown: '판단 불가', open: '확인 대기', in_progress: '조치 중', resolved: '해결', not_submitted: '미제출', needs_attention: '확인 필요', processing: '처리 중', technical_failure: '기술 실패', unassessable: '판단 확인', evaluated: '평가 완료', available: '사용 가능', unavailable: '사용 불가', healthy: '정상', up: '정상', down: '중단', stale: '응답 지연', ready: '연결 완료', missing: '연결 누락', invalid: '연결 확인', expired: '기한 종료', similar: '유사', different: '차이 있음' } as Record<string, string>)[value] ?? value; }
export const roleLabel = (role: string) => ({ store_owner: '점주', ofc: 'OFC', regional: '지역 관리자', hq: '본사', platform_operator: '플랫폼 운영자' } as Record<string, string>)[role] ?? role;
export const displayTime = (value?: string | null) => value ? new Intl.DateTimeFormat('ko-KR', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Seoul' }).format(new Date(value)) : '—';
