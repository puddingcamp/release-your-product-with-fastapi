import { useQuery } from '@tanstack/react-query';
import { httpClient } from '~/libs/httpClient';
import { ICalendar } from '~/types/event';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useCalendarEvent(slug: string) {
    const { data: event } = useQuery<ICalendar | null>({
        queryKey: ['slug', slug],
        queryFn: async () => {
            const url = `${API_URL}/calendar/${slug}`;

            const data: ICalendar = await httpClient(url);
            return data;
        },
    });

    return event ?? null;
} 
