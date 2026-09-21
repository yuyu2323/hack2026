import {defineConfig} from 'vitest/config';
import react from '@vitejs/plugin-react';
export default defineConfig({plugins:[react()],test:{environment:'jsdom',include:['execute/workHitory/input-boundary/independent-recovery01-edge.test.tsx'],globals:true}});
