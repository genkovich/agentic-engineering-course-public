export interface RegisterReq {
  email?: string;
  password?: string;
}

export interface RegisterResp {
  user_id: string;
  email: string;
  created_at: Date;
}

export interface LoginReq {
  email?: string;
  password?: string;
}

export interface LoginResp {
  user_id: string;
  email: string;
}
