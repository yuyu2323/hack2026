from server.core.models import Base


def test_domain_schema_covers_immutable_history_and_access():
    required = {'accounts', 'auth_sessions', 'regions', 'stores', 'categories',
                'store_owner_mappings', 'ofc_store_mappings', 'guidelines',
                'guideline_versions', 'media_assets', 'reference_photos',
                'submissions', 'submission_photos', 'analysis_contexts',
                'analysis_jobs', 'analysis_attempts', 'review_results',
                'criterion_evaluations', 'idempotency_records', 'issues',
                'issue_actions', 'notifications', 'sales_mock', 'inventory_mock',
                'audit_events', 'service_status', 'announcements'}
    assert required <= set(Base.metadata.tables)


def test_migration_matches_model_metadata(db):
    from alembic.migration import MigrationContext
    from alembic.autogenerate import compare_metadata
    assert compare_metadata(MigrationContext.configure(db.connection()),Base.metadata)==[]


def test_current_ofc_assignment_is_unique_but_history_is_kept(db,account_factory,store_factory):
    import pytest
    from sqlalchemy.exc import IntegrityError
    from server.stores.models import OFCStoreMapping
    from server.core.db import utcnow
    store=store_factory()
    first=account_factory('ofc',region_id=store.region_id)
    second=account_factory('ofc',region_id=store.region_id)
    mapping=OFCStoreMapping(account_id=first.id,store_id=store.id,changed_by_id=first.id,reason='테스트 배정')
    db.add(mapping);db.commit()
    db.add(OFCStoreMapping(account_id=second.id,store_id=store.id,changed_by_id=second.id,reason='동시 배정'))
    with pytest.raises(IntegrityError): db.commit()
    db.rollback()
    mapping.ended_at=utcnow();db.commit()
    db.add(OFCStoreMapping(account_id=second.id,store_id=store.id,changed_by_id=second.id,reason='종료 후 배정'));db.commit()
    assert db.get(OFCStoreMapping,mapping.id).ended_at is not None


import pytest
@pytest.mark.postgres
def test_postgres_migration_has_all_constraints(postgres_db):
    from alembic.migration import MigrationContext
    from alembic.autogenerate import compare_metadata
    from sqlalchemy import inspect
    assert set(Base.metadata.tables) <= set(inspect(postgres_db.bind).get_table_names())
    assert 'ck_issue_version' in {item['name'] for item in inspect(postgres_db.bind).get_check_constraints('issues')}
    assert compare_metadata(MigrationContext.configure(postgres_db.connection()),Base.metadata)==[]


def test_issue_version_requires_positive_value(db,account_factory,store_factory):
    from sqlalchemy.exc import IntegrityError
    from server.core.models import Category,Submission,Issue
    owner=account_factory();store=store_factory()
    category=Category(code='issue-version',name='검증');db.add(category);db.flush()
    submission=Submission(store_id=store.id,category_id=category.id,submitted_by_id=owner.id,question='',source_kind='seed_demo');db.add(submission);db.flush()
    issue=Issue(submission_id=submission.id,type='owner_question',status='open',priority='normal',title='버전 검증',description='유효한 업무내용',version=0)
    db.add(issue)
    with pytest.raises(IntegrityError):db.flush()
    db.rollback()
