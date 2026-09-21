import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({plugins:[react()],server:{proxy:{'/api':'http://127.0.0.1:8105'}},preview:{port:5185,strictPort:true,host:'127.0.0.1',proxy:{'/api':'http://127.0.0.1:8105'}}});
