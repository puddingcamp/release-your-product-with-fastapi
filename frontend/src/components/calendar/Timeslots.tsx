import { Suspense } from 'react';
import { Link } from "@tanstack/react-router";
import clsx from "clsx";

import { Button } from "~/components/button";
import { useAuth } from "~/hooks/useAuth";
import { checkAvailableBookingDate } from "~/libs/utils";
import { IBooking, ICalendarEvent } from "~/types/booking";
import { ITimeSlot } from "~/types/timeslot";

interface TimeslotsProps {
    baseDate: Date | null;
    timeslots: ITimeSlot[];
    bookings: Array<IBooking | ICalendarEvent>;
    onSelectTimeslot: (timeslot: ITimeSlot) => void;
}

export default function Timeslots({ baseDate, timeslots, bookings, onSelectTimeslot }: TimeslotsProps) {
    const { data: user } = useAuth();

    const now = baseDate ?? new Date();
    const weekday = now.getDay() === 0 ? 6 : now.getDay() - 1;
    const isAvailable = checkAvailableBookingDate(now, timeslots, bookings, now.getFullYear(), now.getMonth() + 1, now.getDate(), weekday);

    return <Suspense fallback={<div>Loading timeslots...</div>}>
        <div className="flex flex-col gap-4 items-center justify-start mx-auto">
            <h3 className="text-2xl font-bold">{now.getFullYear()}년 {now.getMonth() + 1}월 {now.getDate()}일</h3>
            {!user && (
                <div
                    role="status"
                    role-label="no-date"
                    className="space-y-3 md:space-y-4 w-full md:w-60 md:min-w-60 text-center md:w-full md:text-left">
                    <p>커피챗을 신청할 날짜를 고르세요.</p>
                    <Link
                        to="/app/login"
                        className="block w-full border border-blue-100 font-semibold rounded py-3 text-center bg-primary text-white hover:bg-secondary">
                        로그인 후 커피챗 신청하기
                    </Link>
                </div>
            )}

            {!!user && (timeslots.length === 0 || !isAvailable) && (<div role="status" role-label="no-timeslots">
                <p>예약 가능한 시간대가 없는 날입니다.</p>
            </div>
            )}

            {!!user && isAvailable && timeslots.sort((a, b) => a.startTime.localeCompare(b.startTime)).map((timeslot) => (
                <Button
                    variant="primary"
                    type="button"
                    role="button"
                    role-label={`timeslot-${timeslot.id}`}
                    key={`${timeslot.startTime}-${timeslot.endTime}`}
                    className={clsx("w-full h-fit py-2 px-4 rounded-md")}
                    onClick={() => onSelectTimeslot(timeslot)}
                >
                    <span role="time">{timeslot.startTime}</span>
                </Button>
            ))}
        </div>
    </Suspense>
}
