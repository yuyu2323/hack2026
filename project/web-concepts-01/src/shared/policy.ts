export function roleHome(role: string): string {
  return role === 'store_owner' ? '/store-owner' : role === 'platform_operator' ? '/platform-admin' : '/ofc-admin';
}
export function canVisit(role: string, path: string): boolean {
  const home = roleHome(role);
  return path === home || path.startsWith(home + '/');
}
export function uploadError(files: {type:string;size:number}[], question: string): string | null {
  if (!files.length || files.length > 5) return '사진은 1~5장 선택해 주세요.';
  if (files.some(f => !['image/jpeg', 'image/png'].includes(f.type))) return 'JPEG 또는 PNG 사진만 사용할 수 있습니다.';
  if (files.some(f => f.size > 10485760)) return '사진 한 장은 10MiB 이하로 선택해 주세요.';
  if (question.length > 2000) return '질문은 2,000자 이내로 입력해 주세요.';
  return null;
}
export function pollingInterval(status: string | undefined): number | false {
  return status === 'queued' || status === 'running' ? 2000 : false;
}
export function rateLabel(rate: number | null | undefined): string { return rate == null ? '—' : `${rate}%`; }
export function drilldown(filters: Record<string, unknown>, extra: Record<string, unknown> = {}): Record<string, unknown> {
  const {page, page_size, ...scope} = filters;
  return {...scope, ...extra};
}
export function canEditGuideline(role:string,regionId:string|null,row:Record<string,any>):boolean {
  if(role==='hq')return true;
  if(role==='regional'&&row.level==='REGION')return row.region_id===regionId;
  return ['ofc','regional'].includes(role)&&['STORE','CATEGORY'].includes(row.level)&&!!row.store_id;
}
export function canEditReference(role:string,row:Record<string,any>):boolean {return role==='hq'||(['ofc','regional'].includes(role)&&!!row.store_id);}
