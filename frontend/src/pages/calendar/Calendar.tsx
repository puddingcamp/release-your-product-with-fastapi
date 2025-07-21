import clsx from 'clsx';

import { useSearch, useParams, Link, useNavigate } from '@tanstack/react-router';
import { useEffect, useState, useCallback } from 'react';

import { Body, Navigator, Timeslots, BookingForm } from '~/components/calendar'
import { getCalendarDays } from '~/libs/utils';
import { useCalendarEvent } from '~/hooks/useCalendarEvent';
import { useCalendarNavigation } from '~/hooks/useCalendarNavigation';
import { useCalendarDateSelection } from '~/hooks/useCalendarDateSelection';
import { useTimeslots } from '~/hooks/useTimeslots';
import { ITimeSlot } from '~/types/timeslot';
import { useBookings } from '~/hooks/useBookings';

import './calendar.less';
import { useAuth } from '~/hooks/useAuth';
import { useBookingsStreamQuery } from '~/hooks/useBookings';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

function Calendar({ baseDate }: { baseDate?: Date }) {
    const { year, month } = useSearch({ from: '/app/calendar/$slug' });
    const { slug } = useParams({ from: '/app/calendar/$slug' });
    const [selectedDate, setSelectedDate] = useState<Date | null>(null);
    const [selectedTimeslot, setSelectedTimeslot] = useState<ITimeSlot | null>(null);

    const navigate = useNavigate();
    const auth = useAuth();
    const calendar = useCalendarEvent(slug);
    const { data: timeslots = [] } = useTimeslots(slug, selectedDate);
    const { data: bookingsApi = [], refetch: refetchBookings } = useBookings(slug, selectedDate);
    const bookingsStream = useBookingsStreamQuery({
        endpoint: `${API_URL}/calendar/${slug}/bookings/stream?year=${year}&month=${month}`,
        onMessage: (data) => {
            console.log('onMessage', data);
        },
    });
    const { handlePrevious, handleNext } = useCalendarNavigation();
    const { handleSelectDay } = useCalendarDateSelection();

    const handleDaySelect = useCallback((date: Date) => {
        setSelectedDate(date);
        handleSelectDay(slug, date);
    }, [slug, handleSelectDay]);

    const handleSelectTimeslot = (timeslot: ITimeSlot) => {
        setSelectedTimeslot(timeslot);
    };

    const handleBack = () => {
        setSelectedTimeslot(null);
    };

    const handleBookingCreated = () => {
        setSelectedTimeslot(null);
        refetchBookings();
    };

    useEffect(() => {
        const date = new Date(year, month - 1, 1);
        handleDaySelect(date);
    }, [year, month, handleDaySelect]);

    useEffect(() => {
        if (auth.isError) {
            navigate({
                to: '/app/login',
            });
        }
    }, [auth.isError, navigate]);

    if (!calendar) return null;

    return (
        <div className={clsx("flex flex-col w-full px-8 space-y-4")}>

            <div className='flex flex-row justify-between'>
                <div className='flex flex-row gap-4'>
                    <Link to='/app' className='bg-gray-500 hover:bg-gray-700 hover:text-white text-white px-4 py-2 rounded-md'>첫 화면으로</Link>
                    <Link to='/app/my-bookings' className='border border-gray-500 hover:border-gray-300 hover:text-gray-500 px-4 py-2 rounded-md'>내 예약 목록</Link>
                </div>

                <h2 className="text-primary text-2xl">
                    <span className="font-bold">{slug}</span>님과 약속잡기
                </h2>
            </div>

            {!selectedTimeslot && <div className={clsx("flex flex-col gap-4")}>
                <Navigator
                    slug={slug}
                    year={year}
                    month={month}
                    baseDate={baseDate}
                    onPrevious={handlePrevious}
                    onNext={handleNext}
                />

                <div className={clsx("flex flex-row gap-8 w-full")}>
                    <Body
                        year={year}
                        month={month}
                        days={getCalendarDays(new Date(year, month - 1))}
                        baseDate={baseDate}
                        timeslots={timeslots}
                        bookings={month % 2 === 0 ? bookingsApi : bookingsStream}
                        onSelectDay={handleDaySelect}
                    />
                    <Timeslots
                        timeslots={timeslots}
                        bookings={month % 2 === 0 ? bookingsApi : bookingsStream}
                        baseDate={selectedDate}
                        onSelectTimeslot={handleSelectTimeslot}
                    />
                </div>
            </div>}

            {!!selectedDate && !!selectedTimeslot && <BookingForm
                slug={slug}
                calendar={calendar}
                timeSlotId={selectedTimeslot.id}
                when={selectedDate}
                onBack={handleBack}
                onCreated={handleBookingCreated}
            />}
        </div>

    );
}
export default Calendar;

