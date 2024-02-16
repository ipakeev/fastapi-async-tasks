from typing import Annotated

from fastapi import Depends

from app.store import get_store, Store

StoreDep = Annotated[Store, Depends(get_store)]
