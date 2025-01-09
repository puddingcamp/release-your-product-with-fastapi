import { useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { getBookingsByDate } from '~/libs/bookings';

export function useCalendarNavigation() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const handlePrevious = async (slug: string, date: { year: number; month: number }) => {
        // 이전 달 데이터를 미리 가져오기
        await queryClient.prefetchQuery({
            queryKey: ['bookings', date.year, date.month],
            queryFn: () => getBookingsByDate(slug, { year: date.year, month: date.month }),
        });

        navigate({
            to: '/app/calendar/$slug',
            params: {
                slug,
            },
            search: {
                year: date.year,
                month: date.month,
            },
        });

    };

    const handleNext = async (slug: string, date: { year: number; month: number }) => {
        // 다음 달 데이터를 미리 가져오기
        await queryClient.prefetchQuery({
            queryKey: ['bookings', date.year, date.month],
            queryFn: () => getBookingsByDate(slug, { year: date.year, month: date.month }),
        });

        navigate({
            to: '/app/calendar/$slug',
            params: {
                slug,
            },
            search: {
                year: date.year,
                month: date.month,
            },
        });
    };

    return { handlePrevious, handleNext };
} 