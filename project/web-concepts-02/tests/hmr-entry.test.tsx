import { afterEach, beforeEach, expect, it, vi } from 'vitest';
const mount = vi.hoisted(() => ({render: vi.fn(), createRoot: vi.fn()}));
vi.mock('react-dom/client', () => ({createRoot: mount.createRoot}));
beforeEach(()=>{vi.resetModules();mount.render.mockClear();mount.createRoot.mockReset().mockReturnValue({render:mount.render});document.body.innerHTML='<div id="root"></div>';});
afterEach(()=>{document.body.replaceChildren();vi.resetModules();});
it('같은 DOM의 entry 재평가는 기존 React root를 재사용한다',async()=>{
 await import('../src/app/main');
 vi.resetModules();
 await import('../src/app/main');
 expect(mount.createRoot).toHaveBeenCalledTimes(1);
 expect(mount.render).toHaveBeenCalledTimes(2);
});
it('새 문서 컨테이너에는 별도 React root를 만든다',async()=>{
 await import('../src/app/main');
 document.body.innerHTML='<div id="root"></div>';
 vi.resetModules();
 await import('../src/app/main');
 expect(mount.createRoot).toHaveBeenCalledTimes(2);
});
