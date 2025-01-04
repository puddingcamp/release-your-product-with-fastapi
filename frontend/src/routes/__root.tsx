import { createRouter, createRootRoute, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/router-devtools'
import { z } from 'zod'

import {
    createRoute,
} from '@tanstack/react-router'
import Calendar from '../pages/calendar/Calendar'
import Login from '../pages/account/Login'
import Home from '~/pages/main/Home'
import MyBookings from '~/pages/calendar/MyBookings'
import Booking from '~/pages/calendar/Booking'

const RootRoute = createRootRoute({
    component: () => {
        return (
            <>
                <div className="w-screen h-full flex flex-col items-center justify-center">
                    <div className="w-full h-fit md:w-[800px] md:mx-auto border border-gray-200 rounded-lg px-4 py-8">
                        <Outlet />
                    </div>
                </div>
                <TanStackRouterDevtools />
            </>
        )
    },
})

const homeRoute = createRoute({
    getParentRoute: () => RootRoute,
    path: '/app',
    component: Home,
})


const myBookingsRoute = createRoute({
    getParentRoute: () => RootRoute,
    path: '/app/my-bookings',
    component: MyBookings,
    validateSearch: z.object({
        page: z.number().min(1).optional().default(() => 1),
        pageSize: z.number().min(1).optional().default(() => 10),
    }),
})


const bookingRoute = createRoute({
    getParentRoute: () => RootRoute,
    path: '/app/booking/$id',
    component: Booking,
    params: z.object({
        id: z.string().transform<number>((val) => parseInt(val, 10)).pipe(z.number().min(1)),
    }),
})


const loginRoute = createRoute({
    getParentRoute: () => RootRoute,
    path: '/app/login',
    component: Login,
})


const calendarRoute = createRoute({
    getParentRoute: () => RootRoute,
    path: '/app/calendar/$slug',
    component: Calendar,
    params: z.object({
        slug: z.string().min(4),
    }),
    validateSearch: z.object({
        year: z.number().min(2024).optional().default(() => new Date().getFullYear()),
        month: z.number().min(1).max(12).optional().default(() => new Date().getMonth() + 1),
    }),
})

export const routeTree = RootRoute.addChildren([
    homeRoute,
    calendarRoute,
    loginRoute,
    myBookingsRoute,
    bookingRoute,
])

export const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
    interface Register {
        router: typeof router
    }
}