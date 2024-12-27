// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyObject = Record<string, any>;

function snakeToCamel(obj: AnyObject | AnyObject[]): AnyObject | AnyObject[] {
    if (Array.isArray(obj)) {
        return obj.map(v => snakeToCamel(v));
    } else if (obj !== null && obj.constructor === Object) {
        return Object.keys(obj).reduce((acc, key) => {
            const camelKey = key.replace(/_([a-z])/g, g => g[1].toUpperCase());
            acc[camelKey] = snakeToCamel(obj[key]);
            return acc;
        }, {} as AnyObject);
    }
    return obj;
}

function camelToSnake(obj: AnyObject | AnyObject[]): AnyObject | AnyObject[] {
    if (Array.isArray(obj)) {
        return obj.map(v => camelToSnake(v));
    } else if (obj !== null && obj.constructor === Object) {
        return Object.keys(obj).reduce((acc, key) => {
            const snakeKey = key.replace(/([A-Z])/g, g => `_${g.toLowerCase()}`);
            acc[snakeKey] = camelToSnake(obj[key]);
            return acc;
        }, {} as AnyObject);
    }
    return obj;
}

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