import { DefaultLayout } from "@/layouts/DefaultLayout";

export function HobbiesPage() {
  return (
    <DefaultLayout>
      <h1 className="text-3xl font-bold">/hobbies</h1>
      <p className="text-muted-foreground">
        Projects, pastimes, and personal interests.
      </p>
    </DefaultLayout>
  );
}

export default HobbiesPage;
