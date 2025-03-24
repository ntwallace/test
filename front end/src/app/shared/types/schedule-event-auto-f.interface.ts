import { HvacModeAuto } from 'src/app/shared/types/hvac-mode-auto.type';

export interface IScheduleEventAutoF {
    time: string;
    mode: HvacModeAuto;
    setPointHeatingF: number;
    setPointCoolingF: number;
}
