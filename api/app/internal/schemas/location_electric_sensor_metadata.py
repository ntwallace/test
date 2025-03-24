from typing import Optional
from app.internal.schemas.common import BaseResponse
from app.internal.schemas.metadata_statistic import MetadataStatisticModel


class PostLocationElectricSensorMetadataResponse(BaseResponse):
    data: Optional[MetadataStatisticModel]