import { IBooking, ICalendarEvent } from "~/types/booking";
import { ITimeSlot } from "~/types/timeslot";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyObject = Record<string, any>;

export function snakeToCamel(obj: AnyObject | AnyObject[]): AnyObject | AnyObject[] {
    if (Array.isArray(obj)) {
        return obj.map(v => snakeToCamel(v));
    } else if (obj !== null && obj.constructor === Object) {
        return Object.keys(obj).reduce((acc, key) => {
            const camelKey = key.replace(/_([a-z])/g, g => g[1].toUpperCase());
            acc[camelKey] = snakeToCamel(obj[key]);
            return acc;
        }, {} as AnyObject);
    }
    return obj;
}

export function camelToSnake(obj: AnyObject | AnyObject[]): AnyObject | AnyObject[] {
    if (Array.isArray(obj)) {
        return obj.map(v => camelToSnake(v));
    } else if (obj !== null && obj.constructor === Object) {
        return Object.keys(obj).reduce((acc, key) => {
            const snakeKey = key.replace(/([A-Z])/g, g => `_${g.toLowerCase()}`);
            acc[snakeKey] = camelToSnake(obj[key]);
            return acc;
        }, {} as AnyObject);
    }
    return obj;
}

export const getDaysInMonth = (date: Date) => {
    // 해당 월의 마지막 날짜를 구함
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
};

export const getCalendarDays = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const daysInMonth = getDaysInMonth(date);

    // 해당 월의 1일의 요일을 구함 (0: 일요일, 1: 월요일, ...)
    const firstDayOfMonth = new Date(year, month, 1).getDay();

    // 첫 주의 빈 날짜를 0으로 채움
    const days: number[] = Array(firstDayOfMonth).fill(0);

    // 실제 날짜 추가
    for (let day = 1; day <= daysInMonth; day++) {
        days.push(day);
    }

    // 마지막 주의 남은 칸을 0으로 채움 (7의 배수가 되도록)
    const remainingDays = 7 - (days.length % 7);
    if (remainingDays < 7) {
        days.push(...Array(remainingDays).fill(0));
    }

    return days;
};


export function checkAvailableBookingDate(
    baseDate: Date,
    timeslots: ITimeSlot[],
    bookings: Array<IBooking | ICalendarEvent>,
    year: number,
    month: number,
    day: number,
    weekday: number
) {
    const isUnavailable =
    (weekday === 5 || weekday === 6) ||
    (year < baseDate.getFullYear() ||
      (year === baseDate.getFullYear() && month < baseDate.getMonth() + 1)) ||
    (year === baseDate.getFullYear() &&
      month === baseDate.getMonth() + 1 &&
      day < baseDate.getDate());

    if (isUnavailable) {
        return false;
    }

    if (timeslots.length === 0) {
        return false;
    }

    if (day === 0) {
        return false;
    }

    const isTimeSlotWeekday = timeslots.some(timeslot => timeslot.weekdays.includes(weekday));
    if (!isTimeSlotWeekday) return false;

    return !bookings.some((booking) => {
        const [bookingYear, bookingMonth, bookingDay] = booking.when.split("-");
        if (Number(bookingYear) !== year || Number(bookingMonth) !== month || Number(bookingDay) !== day) {
            return false;
        }

        const [bookingStartHour, bookingStartMinute] = booking.timeSlot.startTime.split(":");
        const bookingStartTime = Number(bookingStartHour) * 60 + Number(bookingStartMinute);
        const [bookingEndHour, bookingEndMinute] = booking.timeSlot.endTime.split(":");
        const bookingEndTime = Number(bookingEndHour) * 60 + Number(bookingEndMinute);

        return timeslots.some((timeslot) => {
            const [startHour, startMinute] = timeslot.startTime.split(":");
            const startTime = Number(startHour) * 60 + Number(startMinute);
            const [endHour, endMinute] = timeslot.endTime.split(":");
            const endTime = Number(endHour) * 60 + Number(endMinute);

            return (bookingEndTime >= startTime && bookingEndTime <= endTime)
        || (bookingStartTime >= startTime && bookingStartTime <= endTime)
        || (startTime <= bookingStartTime && bookingEndTime <= endTime)
        || (bookingStartTime <= startTime && bookingEndTime >= endTime);
        });
    });
}