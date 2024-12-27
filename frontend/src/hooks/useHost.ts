import { useQuery } from '@tanstack/react-query';
import { httpClient } from '~/libs/httpClient';
import { User } from '~/types/user';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useHosts() {
    return useQuery<User[]>({
        queryKey: ['hosts'],
        queryFn: async () => {
            const response = await httpClient<User[]>(`${API_URL}/account/hosts`);
            if (!response) {
                throw new Error('Failed to fetch hosts');
            }
            return response;
        },
        retry: false,
    });
}

