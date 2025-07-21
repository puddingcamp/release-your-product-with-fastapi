import { useMutation, UseMutationResult } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { httpClient } from '~/libs/httpClient';
import { IBookingDetail, IBookingPayload } from '~/types/booking';


const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export function useCreateBooking(slug: string, year: number, month: number): UseMutationResult<IBookingDetail, Error, IBookingPayload> {
    const navigate = useNavigate();

    return useMutation<IBookingDetail, Error, IBookingPayload>({
        mutationFn: async (bookingData: IBookingPayload): Promise<IBookingDetail> => {
            const response = await httpClient<IBookingDetail>(`${API_URL}/bookings/${slug}`, {
                method: 'POST',
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                body: bookingData as any,
            });

            if (!response) {
                throw new Error('Booking creation failed');
            }

            return response;
        },
        onSuccess: () => {
            navigate({
                to: '/app/calendar/$slug',
                params: { slug },
                search: { year, month },
            });
        },
        onError: (error: Error) => {
            console.error('Error creating booking:', error.message);
        },
    });
} 