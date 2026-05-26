import { DefaultLayout } from "@/layouts/DefaultLayout";
import { useTravels } from "@/lib/api";
import { TravelsMap } from "@/components/travels/TravelsMap";
import { TravelsBadges } from "@/components/travels/TravelsBadges";

export function TravelsPage() {
  const { data, error, isLoading } = useTravels();

  if (isLoading) {
    return (
      <DefaultLayout>
        <h1 className="text-3xl font-bold">Travels</h1>
        <div className="mt-8 flex items-center justify-center">
          <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full" />
        </div>
      </DefaultLayout>
    );
  }

  if (error) {
    return (
      <DefaultLayout>
        <h1 className="text-3xl font-bold">Travels</h1>
        <p className="mt-4 text-destructive">Failed to load travels data.</p>
      </DefaultLayout>
    );
  }

  const visited = data?.visited ?? [];
  const bucketlist = data?.bucketlist ?? [];

  return (
    <DefaultLayout>
      <h1 className="text-3xl font-bold">Travels</h1>

      <TravelsMap visited={visited} bucketlist={bucketlist} />

      <div className="mt-12">
        {(visited.length > 0 || bucketlist.length > 0) && (
          <div className="grid gap-10 md:grid-cols-2 md:items-start">
            {visited.length > 0 && (
              <TravelsBadges countries={visited} title="Countries I've Visited" />
            )}
            {bucketlist.length > 0 && (
              <TravelsBadges countries={bucketlist} title="Bucketlist Countries" />
            )}
          </div>
        )}
        {visited.length === 0 && bucketlist.length === 0 && (
          <p className="text-muted-foreground text-center py-12">
            No travels data yet.
          </p>
        )}
      </div>
    </DefaultLayout>
  );
}

export default TravelsPage;
