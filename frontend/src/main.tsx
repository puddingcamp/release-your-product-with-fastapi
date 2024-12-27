import { StrictMode, Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from '@tanstack/react-router'
import { router } from './routes/__root'

const queryClient = new QueryClient();

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <Suspense fallback={<div>Loading...</div>}>
            <QueryClientProvider client={queryClient}>
                <RouterProvider router={router} />
            </QueryClientProvider>
        </Suspense>
    </StrictMode>,
)
