export const homeFor=(role:string):string=>role==='store_owner'?'/store-owner':role==='platform_operator'?'/platform-admin':'/ofc-admin';
export const canVisit=(role:string,path:string):boolean=>{const home=homeFor(role);const clean=path.split('?')[0];if(role==='platform_operator'&&(clean===home+'/notifications'||clean.startsWith(home+'/notifications/')))return false;return clean===home||clean.startsWith(home+'/')};
export const safeReturn=(role:string,path:string|null):string=>path&&!path.startsWith('//')&&!path.includes('\\')&&canVisit(role,path)?path:homeFor(role);
export const rate=(value:number|null|undefined):string=>value==null?'—':`${value}%`;
export const validatePhotos=(files:{type:string;size:number}[]):string=>!files.length||files.length>5?'사진은 1~5장을 선택해 주세요.':files.some(f=>!['image/jpeg','image/png'].includes(f.type))?'JPEG 또는 PNG 사진을 선택해 주세요.':files.some(f=>f.size>10*1024*1024||!f.size)?'사진 한 장은 0보다 크고 10MiB 이하여야 합니다.':'';
export const shouldPoll=(status:string):boolean=>status==='queued'||status==='running';
export const levelOptions=(role:string):string[]=>role==='hq'?['HQ','REGION','STORE','CATEGORY']:role==='regional'?['REGION','STORE','CATEGORY']:['STORE','CATEGORY'];
export function issueChange(version:number,values:Record<string,unknown>){return{version,...values,resolution:String(values.resolution??'').trim()||null};}
// 같은 대상과 본문의 명시적 재시도에만 기존 키를 다시 사용한다.
export function createMutationKeys(makeKey:()=>string=()=>crypto.randomUUID()){
  let signature='',key='';
  return {get(target:string,body:unknown){const next=JSON.stringify([target,body]);if(!key||next!==signature){signature=next;key=makeKey()}return key},reset(){signature='';key=''}};
}
