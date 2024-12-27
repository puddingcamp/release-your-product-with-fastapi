import React, { useState } from 'react';
import { Button } from '~/components/button';
import { useLogin } from '~/hooks/useLogin';

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const loginMutation = useLogin();

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        loginMutation.mutate({ username, password });
    };

    return (
        <div className="space-y-4 px-8">
            <h2 className="text-2xl font-bold">로그인</h2>

            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <div className="flex flex-col gap-2">
                    <label htmlFor="username">아이디:</label>
                    <input
                        type="text"
                        id="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div className="flex flex-col gap-2">
                    <label htmlFor="password">비밀번호:</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <Button variant='primary' type="submit" disabled={loginMutation.isPending} className="w-full py-3 px-5">
                    {loginMutation.isPending ? '로그인 중...' : '로그인'}
                </Button>
            </form>
            {loginMutation.isError && (
                <div className="error-message">로그인에 실패했습니다. 다시 시도해주세요.</div>
            )}
        </div>
    );
}
