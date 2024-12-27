import { useMutation, useQuery } from '@tanstack/react-query';
import { getBooking, getBookingsByDate, getMyBookings, uploadBookingFile } from '~/libs/bookings';
import { IBooking, IBookingDetail, IPaginatedBookingDetail } from '~/types/booking';


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
