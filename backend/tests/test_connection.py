from app.database.connection import Base, SessionLocal, engine, get_db


def test_database_infrastructure_components_are_configured():
    assert Base is not None
    assert engine is not None
    assert SessionLocal is not None


def test_get_db_yields_a_session_and_closes_it():
    db_gen = get_db()
    session = next(db_gen)

    try:
        assert session is not None
        assert session.bind is engine
        assert session.is_active
    finally:
        db_gen.close()
        assert session.bind is engine
