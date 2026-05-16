// Мапить domain sentinel errors на shared/apperr.AppError для HTTP-шару.
import { AppError } from "../../../shared/apperr.js";
import {
  EmailAlreadyExistsError,
  InvalidCredentialsError,
  UserNotFoundError,
} from "../../domain/errors.js";

export function toAPIError(err: unknown): unknown {
  if (err instanceof InvalidCredentialsError) {
    return new AppError(
      InvalidCredentialsError.CODE,
      "invalid email or password",
      401,
    );
  }
  if (err instanceof EmailAlreadyExistsError) {
    return new AppError(
      EmailAlreadyExistsError.CODE,
      "email is already registered",
      409,
    );
  }
  if (err instanceof UserNotFoundError) {
    return new AppError(UserNotFoundError.CODE, "user not found", 404);
  }
  return err;
}
