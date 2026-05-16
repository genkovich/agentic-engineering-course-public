// Sentinel errors для Auth BC. Ports мапить їх на AppError.

export class InvalidCredentialsError extends Error {
  static readonly CODE = "auth.invalid_credentials";
  constructor() {
    super(InvalidCredentialsError.CODE);
    this.name = "InvalidCredentialsError";
  }
}

export class EmailAlreadyExistsError extends Error {
  static readonly CODE = "auth.email_already_exists";
  constructor() {
    super(EmailAlreadyExistsError.CODE);
    this.name = "EmailAlreadyExistsError";
  }
}

export class UserNotFoundError extends Error {
  static readonly CODE = "auth.user_not_found";
  constructor() {
    super(UserNotFoundError.CODE);
    this.name = "UserNotFoundError";
  }
}
