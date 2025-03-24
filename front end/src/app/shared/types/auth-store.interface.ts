import { IAuthState } from './auth-state.interface';

export interface IAuthStore {
    isLoading: boolean;
    user: IAuthState;
}
