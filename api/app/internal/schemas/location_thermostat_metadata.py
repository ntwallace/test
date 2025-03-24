from typing import Optional
from app.internal.schemas.common import BaseResponse
from app.internal.schemas.metadata_statistic import MetadataStatisticModel


class PostLocationThermostatsMetadataResponse(BaseResponse):
    data: Optional[MetadataStatisticModel]
