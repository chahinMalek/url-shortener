import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.unit
@pytest.mark.asyncio
async def test_db_setup(db_session: AsyncSession):
    assert db_session is not None
