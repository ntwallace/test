from datetime import datetime, timedelta
from typing import List
from uuid import UUID


from app.v1.timestream.schemas.circuit_energy_usage import CircuitEnergyUsage
from app.v1.timestream.schemas.circuit_measurement import CircuitAggregatedMeasurement
from app.v1.timestream.schemas.energy_usage import EnergyUsage
from app.v1.timestream.schemas.grouped_circuit_energy_usage_mesaure import GroupedCircuitEnergyUsageMeasure
from app.v1.timestream.schemas.phase_power import PhasePower
from app.v1.timestream.timestream_client import TimestreamClient
from app.v1.timestream.utils import parse_timestream_datetime
from app.v1.electricity_dashboards.schemas.energy_load_curve_electric_widget import EnergyLoadCurveElectricWidgetGroupByUnit


class TimestreamElectricityCircuitMeasurementsService:

    def __init__(self, database: str, table: str, client: TimestreamClient):
        self.database = database
        self.table = table
        self.client = client
    
    def get_aggregated_measurements_for_circuits(
        self,
        circuit_ids: List[UUID],
        start_datetime: datetime,
        end_datetime: datetime,
        aggregation_interval: timedelta = timedelta(minutes=10)
    ) -> List[CircuitAggregatedMeasurement]:
        if len(circuit_ids) == 0:
            return []
        if aggregation_interval.total_seconds() < 60:
            raise ValueError('aggregation_interval must be at least 1 minute')
        
        bin_minutes = round(aggregation_interval.total_seconds() / 60.0)

        query = f"""
            SELECT
                measure_name,
                BIN(time, {bin_minutes}m),
                SUM(ABS(watt)) AS sum_watt,
                SUM(ABS(watt) * period_s / 3600 / 1000 * money_per_kwh * 100) AS sum_cost_cents
            FROM "{self.database}"."{self.table}"
            WHERE measure_name in ({",".join(f"'{circuit_id!s}'" for circuit_id in circuit_ids)})
            AND time BETWEEN '{start_datetime}'
                         AND '{end_datetime}'
            GROUP BY measure_name, BIN(time, {bin_minutes}m)
            ORDER BY measure_name, BIN(time, {bin_minutes}m)
        """
        timestream_data = self.client.query(query)

        return [
            CircuitAggregatedMeasurement(
                circuit_id=UUID(row[0]),
                measurement_datetime=parse_timestream_datetime(row[1]),
                aggregation_interval=aggregation_interval,
                sum_watts=float(row[2]),
                sum_cost_cents=round(float(row[3]))
            )
            for row in timestream_data
        ]
    
    def get_energy_table_circuits_energy(
        self,
        circuit_ids: List[UUID],
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> List[CircuitEnergyUsage]:
        query = f"""
            SELECT
                measure_name,
                SUM( ABS(watt) ) / 3600 / 1000 AS kwh,
                SUM( ABS(watt) * money_per_kwh ) / 3600 / 1000 AS money
            FROM "{self.database}"."{self.table}"
            WHERE measure_name in ({",".join([f"'{circuit_id!s}'" for circuit_id in circuit_ids])})
            AND time BETWEEN '{start_datetime}'
                        AND '{end_datetime}'
            GROUP BY measure_name
        """
        timestream_data = self.client.query(query)
        measures = [
            CircuitEnergyUsage(
                circuit_id=UUID(row[0]),
                usage=EnergyUsage(
                    kwh=float(row[1]),
                    money=float(row[2])
                )
            )
            for row in timestream_data
        ]
        return measures
    
    def get_grouped_circuits_energy(
        self,
        circuit_ids: List[UUID],
        start_datetime: datetime,
        end_datetime: datetime,
        group_by_unit: EnergyLoadCurveElectricWidgetGroupByUnit,
        group_by_size: int
    ) -> List[GroupedCircuitEnergyUsageMeasure]:
        if not group_by_unit.is_supported_by_timestream():
            raise ValueError('Invalid group_by_unit')
        
        binning = f"{group_by_size}{group_by_unit.as_timestream_unit()}"
        query = f"""
            SELECT
                measure_name,
                BIN(local_time, {binning}) + (MIN(time) - MIN(local_time)) AS butc,
                SUM( ABS(watt) ) / 3600 / 1000 AS kwh,
                SUM( ABS(watt) * money_per_kwh ) / 3600 / 1000 AS money
            FROM "{self.database}"."{self.table}"
            WHERE measure_name in ({",".join(f"'{circuit_id!s}'" for circuit_id in circuit_ids)})
            AND time BETWEEN '{start_datetime}'
                        AND '{end_datetime}'
            GROUP BY measure_name, BIN(local_time, {binning})
            ORDER BY BIN(local_time, {binning})
        """
        timestream_data = self.client.query(query)
        measures = [
            GroupedCircuitEnergyUsageMeasure(
                start=parse_timestream_datetime(row[1]),
                usage=CircuitEnergyUsage(
                    circuit_id=UUID(row[0]),
                    usage=EnergyUsage(
                        kwh=float(row[2]),
                        money=float(row[3])
                    )
                )
            )
            for row in timestream_data
        ]
        return measures
    
    def get_phase_power(
        self,
        sensor_duids: List[str],
        clamp_pins: List[int]
    ) -> List[PhasePower]:
        pins = ", ".join(f"'{pin}'" for pin in clamp_pins)
        sensors = ", ".join(f"'{sensor}'" for sensor in sensor_duids)
        query = f"""
            SELECT
                sensor,
                clamp as pin,
                MAX_BY(ABS(watt) / period_s, time) AS watt
            FROM "{self.database}"."{self.table}"
            WHERE time > AGO(10m)
                AND sensor IN ({sensors})
                AND clamp IN ({pins})
            GROUP BY sensor, clamp
        """
        timestream_data = self.client.query(query)
        rows = [
            PhasePower(
                sensor=row[0],
                pin=int(row[1]),
                watt=float(row[2])
            )
            for row in timestream_data
        ]
        return rows
