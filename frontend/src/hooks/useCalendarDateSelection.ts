import { useQueryClient } from '@tanstack/react-query';
import { httpClient } from '~/libs/httpClient';
import { ITimeSlot } from '~/types/timeslot';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useCalendarDateSelection() {
    const queryClient = useQueryClient();

    const handleSelectDay = async (slug: string, date: Date) => {
        await queryClient.prefetchQuery({
            queryKey: ['timeslots', slug, date.toISOString()],
            queryFn: async () => {
                if (!date) throw new Error("Date is required");

                const year = date.getFullYear();
                const month = date.getMonth() + 1;

                const url = `${API_URL}/time-slots/${slug}?year=${year}&month=${month}`;
                const data: ITimeSlot[] = await httpClient(url);

                return data;
                 
            },
        });
    };

    return { handleSelectDay };
} 