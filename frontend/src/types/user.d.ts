import { ISO8601String } from "./base";

export interface User {
    id: number;
    username: string;
    email: string;
    displayName: string;
    isHost: boolean;
    createdAt: ISO8601String;
    updatedAt: ISO8601String;
}

export interface IUserSimple {
    username: string;
    displayName: string;
    isHost: boolean;
}
