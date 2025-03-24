from enum import StrEnum
from typing import Optional


class VoltageField(StrEnum):
    volt_A = "volt_A"
    volt_B = "volt_B"
    volt_C = "volt_C"


def voltage_field_from_db(field: str) -> Optional[VoltageField]:
    if field == "voltage1":
        return VoltageField.volt_A
    if field == "voltage2":
        return VoltageField.volt_B
    if field == "voltage3":
        return VoltageField.volt_C
    if field == "unmeasured":  # explicitly show that this value is expected
        return None
    return None

def pin_number_from_port(port_name: str, port_pin: int) -> int:
    return ["A", "B", "C", "D"].index(port_name.upper()) * 4 + port_pin