import { DefaultLayout } from "@/components/ui/default-layout";

export function GamingPage() {
  return (
    <DefaultLayout>
      <h1 className="text-3xl font-bold">Gaming</h1>
      <p className="text-muted-foreground">
        Game reviews, setups, and gaming highlights.
      </p>
    </DefaultLayout>
  );
}

export default GamingPage;
