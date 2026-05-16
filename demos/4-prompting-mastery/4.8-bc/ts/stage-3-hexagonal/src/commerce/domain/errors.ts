export class InvalidOrderError extends Error {
  static readonly CODE = "commerce.invalid_order";
  constructor() {
    super(InvalidOrderError.CODE);
    this.name = "InvalidOrderError";
  }
}
