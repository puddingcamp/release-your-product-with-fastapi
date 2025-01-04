import { useMutation, UseMutationResult } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { httpClient } from '~/libs/httpClient';
import { User } from '~/types/user';

interface LoginCredentials {
    username: string;
    password: string;
}

interface LoginResponse {
    accessToken: string;
    tokenType: string;
    user: User;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useLogin(): UseMutationResult<LoginResponse, Error, LoginCredentials> {
    const navigate = useNavigate();

    return useMutation<LoginResponse, Error, LoginCredentials>({
        mutationFn: async (credentials: LoginCredentials): Promise<LoginResponse> => {
            const response = await httpClient<LoginResponse>(`${API_URL}/account/login`, {
                method: 'POST',
                body: credentials as unknown as BodyInit,
            });

            if (!response || !response.accessToken) {
                throw new Error('Login failed');
            }

            localStorage.setItem('auth_token', response.accessToken);
            return response;
        },
        onSuccess: () => {
            navigate({
                to: '/app',
            });
        },
        onError: (error: Error) => {
            console.error('Login error:', error);
        },
    }
    );
} 