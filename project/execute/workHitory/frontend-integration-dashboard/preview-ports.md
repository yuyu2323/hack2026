# PREVIEW-PORT-01
- docs10 localhost5173~5177 Origin 계약과 각 매뉴얼 bare npm run preview에 비해02~05의 Vite preview포트가4173으로설정해결됨. 기본preview로그인은ORIGIN_DENIED 위험. 독립contract_data가resolveConfig로재현.
- root단독소유02~05 vite.config.ts preview옵션에각5174~5177/127.0.0.1/strictPort 명시,기존proxy유지. API/DB/허용Origin범위불변.01기존정상과정합.
- 변경전실제앱QA진행,현재모델작업없음. 이후config해결값검사와독립재확인,각preview실제기동인수필요.
