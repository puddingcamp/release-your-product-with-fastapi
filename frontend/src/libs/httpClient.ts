import { camelToSnake, snakeToCamel } from "./utils";

export async function httpClient<T>(url: string, options: RequestInit = {}): Promise<T> {
    const authToken = localStorage.getItem('auth_token');
    if (authToken) {
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${authToken}`,
        };
    }

    if (options.body && !(options.body instanceof FormData) && typeof options.body === 'object') {
        options.body = JSON.stringify(camelToSnake(options.body));
        options.headers = {
            ...options.headers,
            'Content-Type': 'application/json',
        };
    }

    const response = await fetch(url, options);

    if (!response.ok) {
        let data;
        try {
            data = await response.json();
        } catch (err) {
            throw new Error(`HTTP error! status: ${response.status}`, { cause: response.status });
        }
        throw new Error(data.detail, { cause: response.status });
    }

    const data = await response.json();
    return snakeToCamel(data) as T;
} 