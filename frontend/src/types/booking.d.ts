import type { DateString, ISO8601String } from "./base";
import type { ITimeSlot } from "./timeslot";

export interface IBooking {
    id: number;
    when: DateString;
    timeSlot: ITimeSlot;
}

export interface ICalendarEvent {
    id: string;
    when: DateString;
    timeSlot: ITimeSlot;
}


export interface IBookingDetail {
    id: number
    when: Date
    topic: string
    description: string
    timeSlot: ITimeSlot
    host: IUserSimple
    files: IBookingFile[]
    createdAt: ISO8601String

    updatedAt: ISO8601String
}


export interface IBookingPayload {
    when: DateString
    topic: string
    description: string
    timeSlotId: number
}

export interface IPaginatedBookingDetail {
    bookings: IBookingDetail[]
    totalCount: number
}


export interface IBookingFile {
    id: number
    file: string
}