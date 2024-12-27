import { httpClient } from '~/libs/httpClient';
import { IBooking, IBookingDetail, IPaginatedBookingDetail } from '~/types/booking';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function getBookingsByDate(slug: string, date: { year: number; month: number }): Promise<IBooking[]> {
    const url = `${API_URL}/calendar/${slug}/bookings?year=${date.year}&month=${date.month}`;
    const data: IBooking[] = await httpClient<IBooking[]>(url);
    return data;
}

export async function getMyBookings({ page = 1, pageSize = 10 }: { page?: number; pageSize?: number }): Promise<IPaginatedBookingDetail> {
    const url = `${API_URL}/guest-calendar/bookings?page=${page}&page_size=${pageSize}`;
    const data: IPaginatedBookingDetail = await httpClient<IPaginatedBookingDetail>(url);
    return data;
}

export async function getBooking(id: number): Promise<IBookingDetail> {
    const url = `${API_URL}/bookings/${id}`;
    const data: IBookingDetail = await httpClient<IBookingDetail>(url);
    return data;
}

export async function uploadBookingFile(id: number, files: FormData): Promise<IBookingDetail> {
    const url = `${API_URL}/bookings/${id}/upload`;
    const data: IBookingDetail = await httpClient<IBookingDetail>(url, {
        method: 'POST',
        body: files,
    });
    return data;
}