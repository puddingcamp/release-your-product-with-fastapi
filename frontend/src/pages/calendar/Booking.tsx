import { Link, useParams } from "@tanstack/react-router";
import { useEffect } from "react";
import { Button } from "~/components/button";
import { useBooking, useUploadBookingFile } from "~/hooks/useBookings";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Booking() {
    const { id } = useParams({ from: '/app/booking/$id' });
    const { data: booking, isLoading, error, refetch } = useBooking(id);
    const { mutate: uploadFile, isSuccess: isUploadSuccess } = useUploadBookingFile(id);

    useEffect(() => {
        if (isUploadSuccess) {
            refetch();
        }
    }, [isUploadSuccess, refetch]);


    if (!booking || isLoading) return <div>예약 정보를 불러오고 있습니다...</div>;
    if (error) return <div>예약 정보를 불러오는 중 오류가 발생했습니다.</div>;

    const when = new Date(booking.when);
    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const formData = new FormData(e.target as HTMLFormElement);
        uploadFile(formData);
    }

    return <div className="flex flex-col space-y-4">
        <Link to='/app/my-bookings' className='inline-block w-fit bg-gray-500 hover:bg-gray-700 hover:text-white text-white px-4 py-2 rounded-md'>내 예약 목록으로</Link>

        <h1 className="text-2xl font-bold">{booking.host.displayName}님과 약속잡기</h1>

        <div className="flex flex-row space-x-2 items-center">
            <div>{booking.topic}</div>
            <div className="text-sm text-gray-500 flex flex-row items-center space-x-2">
                <div>{when.getFullYear()}년 {when.getMonth() + 1}월 {when.getDate()}일</div>
                <div>{booking.timeSlot.startTime} - {booking.timeSlot.endTime}</div>
            </div>
        </div>

        <div className="flex flex-row space-x-2 items-center">
            {booking.description}
        </div>

        <hr className="w-full" />

        <form className="flex flex-col space-y-2 items-start" onSubmit={handleSubmit}>
            <input type="file" name="files" multiple />
            <Button type="submit" variant="primary" className="w-full py-2">첨부</Button>
        </form>

        {booking.files.length > 0 && (
            <ul className="list-disc pl-4 space-y-2">
                {booking.files.map((file) => {
                    const filename = file.file.split('/').pop();
                    return <li key={file.id} className="">
                        <a href={`${API_URL}/${file.file}`} target="_blank" rel="noopener noreferrer">{filename}</a>
                    </li>
                })}
            </ul>
        )}
        {booking.files.length === 0 && (
            <div>첨부 파일이 없습니다.</div>
        )}
    </div>;
}
