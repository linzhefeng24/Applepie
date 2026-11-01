export type User = {id: string; username: string; displayName: string; role: string; enabled: boolean; permissions: string[]};
export type Session = {id: string; createdAt: string; expiresAt: string; current: boolean};
