export class InvalidPlanError extends Error {
  static readonly CODE = "billing.invalid_plan";
  constructor() {
    super(InvalidPlanError.CODE);
    this.name = "InvalidPlanError";
  }
}
