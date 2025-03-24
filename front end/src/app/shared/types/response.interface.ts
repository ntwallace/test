export interface IResponse<DataT> {
    data: DataT;
    message: string | null;
    code: string;
}
