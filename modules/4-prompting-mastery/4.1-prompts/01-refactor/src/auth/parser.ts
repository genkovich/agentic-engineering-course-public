type RawUser = {
  email?: unknown;
  name?: unknown;
  age?: unknown;
};

type DomainUser = {
  email: string;
  displayName: string;
  ageGroup: "minor" | "adult" | "senior";
};

export function parseUser(raw: RawUser): DomainUser {
  // validation
  if (typeof raw.email !== "string" || !raw.email.includes("@")) {
    throw new Error("invalid email");
  }
  if (typeof raw.name !== "string" || raw.name.trim().length === 0) {
    throw new Error("invalid name");
  }
  if (typeof raw.age !== "number" || raw.age < 0 || raw.age > 150) {
    throw new Error("invalid age");
  }

  // mapping
  const email = raw.email.toLowerCase().trim();
  const displayName = raw.name.trim().replace(/\s+/g, " ");
  let ageGroup: DomainUser["ageGroup"];
  if (raw.age < 18) ageGroup = "minor";
  else if (raw.age < 65) ageGroup = "adult";
  else ageGroup = "senior";

  return { email, displayName, ageGroup };
}
