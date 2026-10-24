import { useQuery } from "@tanstack/react-query";

import Button from "../components/Button";

interface User {
  id: string;
  email: string;
}

async function fetchCurrentUser(): Promise<User> {
  const res = await fetch("/api/users/me");
  if (!res.ok) throw new Error("user.fetch_failed");
  return (await res.json()) as User;
}

export default function Home() {
  const { data, isLoading } = useQuery({
    queryKey: ["currentUser"],
    queryFn: fetchCurrentUser,
  });

  if (isLoading) return <p>Loading...</p>;

  return (
    <main>
      <h1>Welcome, {data?.email ?? "guest"}</h1>
      <Button variant="primary" onClick={() => location.assign("/dashboard")}>
        Open dashboard
      </Button>
    </main>
  );
}
