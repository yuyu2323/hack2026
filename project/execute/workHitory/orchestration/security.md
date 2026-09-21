
### SR-02 merge 이력 검사 누락 수정
- 독립 검토의 임시 repo 테스트에서 merge commit만으로 도입·제거한 금지 파일/비밀2건이 허용되는 RED 확인.
- pre-push 경로 diff-tree에 -m, Gitleaks log-opts에도 -m을 전달하여 각 부모와의 merge 차이를 포함.
- 보안 전체 단위9 PASS(기존7+새merge2). 실제 프로젝트 commit/push는 수행하지 않았다.
