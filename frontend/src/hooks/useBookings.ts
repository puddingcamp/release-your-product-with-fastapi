import { useMutation, useQuery } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { getBooking, getBookingsByDate, getMyBookings, uploadBookingFile } from '~/libs/bookings';
import { snakeToCamel } from '~/libs/utils';
import { IBooking, IBookingDetail, ICalendarEvent, IPaginatedBookingDetail } from '~/types/booking';


export function useBookings(hostname: string, date: Date | null) {
    return useQuery<IBooking[]>({
        queryKey: ['bookings', date?.toISOString()],
        queryFn: async () => {
            const data: IBooking[] = await getBookingsByDate(hostname, { year: date!.getFullYear(), month: date!.getMonth() + 1 });
            return data;
        },
        enabled: !!date,
    });
}

export function useMyBookings({ page, pageSize }: { page?: number; pageSize?: number }) {
    return useQuery<IPaginatedBookingDetail>({
        queryKey: ['my-bookings', page, pageSize],
        queryFn: async () => {
            const data: IPaginatedBookingDetail = await getMyBookings({ page, pageSize });
            return data;
        },
    });
}

export function useBooking(id: number) {
    return useQuery<IBookingDetail>({
        queryKey: ['booking', id],
        queryFn: async () => {
            const data: IBookingDetail = await getBooking(id);
            return data;
        },
    });
}

export function useUploadBookingFile(id: number) {
    return useMutation<IBookingDetail, Error, FormData>({
        mutationFn: async (files: FormData) => {
            const data: IBookingDetail = await uploadBookingFile(id, files);
            return data;
        },
    });
}

export function useBookingsStreamQuery({
    endpoint,
    onMessage,
}: {
    endpoint: string;
    onMessage?: (data: IBooking | ICalendarEvent) => void;
}) {
    const [items, setItems] = useState<Array<IBooking | ICalendarEvent>>([]);

    useEffect(() => {
        const fetchStream = async () => {
            const response = await fetch(endpoint);
            const reader = response.body!.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    await reader.cancel();
                    break;
                }

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n').filter(Boolean);
                lines.forEach(line => {
                    const data = snakeToCamel(JSON.parse(line)) as IBooking | ICalendarEvent;
                    setItems((prevData) => {
                        const index = prevData.findIndex((item) => item.id === data.id);
                        if (index === -1) {
                            return [...prevData, data];
                        }
                        return prevData;
                    });
                    onMessage?.(data);
                });
            }
        };

        fetchStream();

    }, [endpoint, onMessage]);

    return items;
}