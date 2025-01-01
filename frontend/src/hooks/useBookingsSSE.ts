import { useEffect, useState } from 'react';
import { snakeToCamel } from '~/libs/utils';
import { IBooking, ICalendarEvent } from '~/types/booking';

export function useBookingsStreamQuery({
    endpoint,
    onMessage,
}: {
    endpoint: string;
    onMessage?: (data: IBooking | ICalendarEvent) => void;
}) {
    const [data, setData] = useState<Array<IBooking | ICalendarEvent>>([]);

    useEffect(() => {
        const eventSource = new EventSource(
            endpoint,
            {
                withCredentials: true
            },
        );
        
        eventSource.onmessage = (event) => {
            try {
                const newData = snakeToCamel(JSON.parse(event.data)) as IBooking | ICalendarEvent;
                if ((newData as unknown as { type: string }).type === 'complete') {
                    eventSource.close();
                    return;
                }
                setData((prevData) => {
                    const index = prevData.findIndex((item) => item.id === newData.id);
                    if (index === -1) {
                        return [...prevData, newData];
                    }
                    return prevData;
                });
                onMessage?.(newData);
            } catch (error) {
                console.error('SSE message parsing error:', error);
            }
        };

        eventSource.onerror = (error) => {
            console.error('SSE connection error:', error);
        };

        return () => eventSource.close();
    }, [endpoint, onMessage]);

    return { data };
}
