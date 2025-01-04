import { Link } from '@tanstack/react-router';
import { useHosts } from '~/hooks/useHost';

export default function Home() {
    const hosts = useHosts();
    const now = new Date();

    return (
        <div className='w-6/12 mx-auto flex flex-col justify-center min-h-[200px] px-8 space-y-4'>
            <h1 className='text-2xl font-bold'>약속 잡기 서비스</h1>

            {hosts.isLoading && <div>읽어오는 중...</div>}
            {hosts.error && <div className='space-y-2'>
                <p className='text-red-500'>{hosts.error.message}</p>
                {hosts.error.cause === 401 && <p className=''>
                    <Link href='/app/login' className='block text-center bg-primary text-white px-4 py-2 rounded-md hover:bg-secondary hover:text-white'>로그인</Link>
                </p>}
            </div>}

            <ul>
                {hosts.data?.map((host) => (
                    <li key={host.username}>
                        <Link
                            to='/app/calendar/$slug'
                            params={{ slug: host.username }}
                            search={{ year: now.getFullYear(), month: now.getMonth() + 1 }}
                            className='block text-center bg-primary text-white px-4 py-2 rounded-md hover:bg-secondary hover:text-white'
                        >
                            {host.displayName} ({host.username})
                        </Link>
                    </li>
                ))}
            </ul>
        </div>
    );
};

