"""llm_calls: every model call is written to a real Postgres and added up per day."""

from sqlalchemy import func, select

from djangodesk.config import Settings
from djangodesk.db.llm_calls import UsageRepository, make_recorder
from djangodesk.db.models import LlmCall
from djangodesk.db.session import make_engine, make_sessionmaker
from djangodesk.llm.gateway import FakeLLM, LLMError, LLMGateway


async def test_gateway_calls_are_recorded_and_summed_per_day(test_database):
    engine = make_engine(Settings(app_env="ci", database_url=test_database, _env_file=None))
    sessionmaker = make_sessionmaker(engine)
    async with sessionmaker() as session:
        await session.execute(LlmCall.__table__.delete())
        await session.commit()
    primary = FakeLLM("gemini", "gemini-3.8-flash", [LLMError("HTTP 401", retryable=False), "Ok."])
    backup = FakeLLM("groq", "openai/gpt-oss-20b", ["From the backup."])
    gateway = LLMGateway([primary, backup], recorder=make_recorder(sessionmaker))
    await gateway.generate([{"role": "user", "content": "one"}], prompt_version="chat_system_v1")
    await gateway.generate([{"role": "user", "content": "two"}], prompt_version="chat_system_v1")
    async with sessionmaker() as session:
        assert await session.scalar(select(func.count()).select_from(LlmCall)) == 3
        days = await UsageRepository(session).by_day()
    await engine.dispose()
    assert len(days) == 1
    assert days[0]["calls"] == 3 and days[0]["errors"] == 1 and days[0]["fallbacks"] == 1
    assert days[0]["tokens_in"] == 24 and days[0]["cost_inr"] > 0
