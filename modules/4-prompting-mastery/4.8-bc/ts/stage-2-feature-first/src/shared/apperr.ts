// shared/apperr — типізовані помилки для крос-BC помилкової семантики.

export class AppError extends Error {
  readonly code: string;
  readonly statusCode: number;

  constructor(code: string, message: string, statusCode: number) {
    super(message);
    this.name = "AppError";
    this.code = code;
    this.statusCode = statusCode;
  }
}

export function isAppError(e: unknown): e is AppError {
  return e instanceof AppError;
}
