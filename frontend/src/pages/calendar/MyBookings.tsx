import { Link, useSearch } from '@tanstack/react-router';
import { useState } from 'react';
import Pagination from '~/components/Pagination';
import { useMyBookings } from '~/hooks/useBookings';

export default function MyBookings() {
    const { page, pageSize } = useSearch({ from: '/app/my-bookings' });
    const [currentPage, setCurrentPage] = useState<number>(page);
    const { data: bookings, isLoading, error } = useMyBookings({ page: currentPage, pageSize });

    return (
        <div className="space-y-4">
            <Link to='/app' className='bg-gray-500 hover:bg-gray-700 hover:text-white text-white px-4 py-2 rounded-md'>첫 화면으로</Link>

            <h2 className="text-2xl font-bold">내 예약 목록</h2>

            {isLoading && <div>내 예약 목록을 불러오고 있습니다...</div>}
            {!!error && <div className="text-red-500 space-y-2">
                <div className="text-lg font-bold">오류 발생</div>
                <div className="text-sm">{error.message}</div>
                <Link to="/app/login" className="inline-block bg-primary text-white px-4 py-2 rounded-md">로그인하기</Link>
            </div>}

            <ul>
                {bookings?.bookings.map((booking) => {
                    const when = new Date(booking.when);

                    return <li key={booking.id} className="border-b py-2">
                        <Link to="/app/booking/$id" params={{ id: booking.id }} className="hover:text-primary">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-500">
                                    {when.getFullYear()}.{when.getMonth() + 1}.{when.getDate()}
                                </span>
                                <span className="text-sm text-gray-500">
                                    {booking.timeSlot.startTime} - {booking.timeSlot.endTime}
                                </span>
                            </div>

                            <div className="flex items-center space-x-2">
                                <span className="">{booking.host.displayName}님과</span>
                                <span className="">{booking.topic} 주제로 예약</span>
                            </div>
                        </Link>
                    </li>
                })}
            </ul>

            <Pagination
                page={currentPage}
                pageSize={pageSize}
                totalCount={bookings?.totalCount || 0}
                onPageChange={setCurrentPage}
            />
        </div>
    );
}

