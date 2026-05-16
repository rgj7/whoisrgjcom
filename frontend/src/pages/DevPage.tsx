import { DefaultLayout } from "../components/ui/default-layout";

export function DevPage() {
  return (
    <DefaultLayout>
      <h1 className="text-3xl font-bold">Dev</h1>
      <p className="text-muted-foreground">
        Projects, code snippets, and development notes.
      </p>
    </DefaultLayout>
  );
}

export default DevPage;
