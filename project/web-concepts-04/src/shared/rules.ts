export const roleHome = (role: string): string => role === 'store_owner' ? '/store-owner' : role === 'platform_operator' ? '/platform-admin' : '/ofc-admin';
export const safeReturn = (target: string|null, role: string) => {const home=roleHome(role);return target && !target.includes('\\') && (target===home||target.startsWith(home+'/')||target.startsWith(home+'?')) ? target : home;};
export const validatePhotos = (files: {name:string;type:string;size:number}[]): string|null => {
 if(files.length<1||files.length>5)return '사진을 1~5장 선택해 주세요.';
 if(files.some(f=>f.size>10*1024*1024||f.size===0))return '사진은 한 장당 10MB 이내여야 합니다.';
 if(files.some(f=>!['image/jpeg','image/png'].includes(f.type)||!(/\.(jpe?g|png)$/i).test(f.name)))return 'JPG 또는 PNG 사진을 선택해 주세요.';
 return null;
};
export const rate = (value: number|null|undefined): string => value==null?'—':`${value}%`;
export const listHref = (path:string,search:string) => path+(search.startsWith('?')?search:search?'?'+search:'');

export const hasBusinessInbox = (role:string) => ['store_owner','ofc','regional','hq'].includes(role);
