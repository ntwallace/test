export interface IWidget {
    id: string;
    widget_type:
        | 'unavailable'
        | 'UsageSource'
        | 'EnergyLoadCurve'
        | 'EnergyIntensity'
        | 'EnergyConsumptionBreakdown'
        | 'PanelSystemHealth'
        | 'TemperatureUnit'
        | 'HistoricTemperatureGraph'
        | 'ControlZone'
        | 'ControlZoneTrends'
        | 'ControlZoneTemperatures'
        | 'Unknown';
}
