from sqlalchemy.ext.asyncio.session import AsyncSession


class BaseService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _create_response(self,
                               data: dict,
                               status:str='success'):
        res = {
            'status': status,
            'data': data
        }
        return res