import { StringTime } from "./base";

export interface ITimeSlot {
    id: number;
    startTime: StringTime;
    endTime: StringTime;
    weekdays: number[];
}