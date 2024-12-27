import React, { useEffect, useRef } from 'react';
import { useCreateBooking } from '~/hooks/useCreateBooking';
import { ICalendar } from '~/types/event';
import { Button } from '../button';

interface BookingFormProps {
    calendar: ICalendar;
    slug: string;
    timeSlotId: number;
    when: Date;
    onBack: () => void;
    onCreated: () => void;
}

export default function BookingForm({ calendar, slug, timeSlotId, when, onBack, onCreated }: BookingFormProps) {
    const createBookingMutation = useCreateBooking(slug, when.getFullYear(), when.getMonth() + 1);
    const topicRef = useRef<HTMLSelectElement>(null);
    const descriptionRef = useRef<HTMLTextAreaElement>(null);

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        createBookingMutation.mutate({
            timeSlotId,
            topic: topicRef.current?.value ?? '',
            description: descriptionRef.current?.value ?? '',
            when: `${when.getFullYear()}-${String(when.getMonth() + 1).padStart(2, '0')}-${String(when.getDate()).padStart(2, '0')}`,
        });
    };

    useEffect(() => {
        if (createBookingMutation.isSuccess) {
            onCreated();
        }
    }, [createBookingMutation.isSuccess, onCreated]);

    return (
        <div className='flex flex-col items-center justify-center space-y-4'>
            <div className="w-full">
                <Button variant="secondary" className="inline-block py-2 px-4" onClick={onBack}>달력으로 돌아가기</Button>
            </div>
            <form onSubmit={handleSubmit} className="w-full">
                <div className="space-y-4 w-full">
                    <div className="space-y-2">
                        <label htmlFor="topic">주제:</label>
                        <select
                            ref={topicRef}
                            id="topic"
                            className="w-full border border-gray-300 rounded-md p-2"
                        >
                            {calendar.topics.map((topic) => <option key={topic} value={topic}>{topic}</option>)}
                        </select>
                    </div>
                    <div className="space-y-2">
                        <label htmlFor="description">설명:</label>
                        <textarea
                            ref={descriptionRef}
                            id="description"
                            className="w-full border border-gray-300 rounded-md p-2"
                        />
                    </div>
                    <Button variant='primary' type="submit" disabled={createBookingMutation.isPending} className='w-full py-3 font-semibold'>
                        {createBookingMutation.isPending ? '예약 신청 중...' : '예약 신청하기'}
                    </Button>
                    {createBookingMutation.isError && (
                        <div className="error-message">{createBookingMutation.error.message}</div>
                    )}
                    {createBookingMutation.isSuccess && (
                        <div className="success-message">예약 생성 완료!</div>
                    )}
                </div>
            </form>
        </div>
    );
}