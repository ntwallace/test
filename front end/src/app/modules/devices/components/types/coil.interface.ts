export interface ICoil {
    id: number;
    amperage_rating: string;
    coil_id: number;
    pes_breaker: {
        id: string;
        channel_type: string;
        label: string;
    };
}
