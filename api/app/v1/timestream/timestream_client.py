from typing import List

from mypy_boto3_timestream_query import TimestreamQueryClient


class TimestreamClient:

    def __init__(self, query_client: TimestreamQueryClient):
        self.query_client = query_client
    
    def query(self, query: str) -> List[List[str]]:
        paginator = self.query_client.get_paginator('query')
        try:
            # TODO: Double check that this logic is correct
            data: List[List[str]] = []
            for page in paginator.paginate(QueryString=query):
                data.extend([
                    [
                        column['ScalarValue']
                        for column in row['Data']
                    ]
                    for row in page['Rows']
                ])
            return data
        except Exception as error:
            if 'At least two points are required in the timeseries' in str(error):
                return []
            raise
