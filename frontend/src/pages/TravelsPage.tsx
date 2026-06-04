import { DefaultLayout } from "@/layouts/DefaultLayout";
import { useTravels } from "@/lib/api";
import { TravelsMap } from "@/components/travels/TravelsMap";
import { TravelsBadges } from "@/components/travels/TravelsBadges";

export function TravelsPage() {
  const { data, error, isLoading } = useTravels();

  if (isLoading) {
    return (
      <DefaultLayout>
        <h1 className="text-3xl font-bold">/travels</h1>
        <div className="mt-8 flex items-center justify-center">
          <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full" />
        </div>
      </DefaultLayout>
    );
  }

  if (error) {
    return (
      <DefaultLayout>
        <h1 className="text-3xl font-bold">/travels</h1>
        <p className="mt-4 text-destructive">Failed to load travels data.</p>
      </DefaultLayout>
    );
  }

  const visited = data?.visited ?? [];
  const bucketlist = data?.bucketlist ?? [];

  return (
    <DefaultLayout>
      <h1 className="text-3xl font-bold">/travels</h1>

      <p className="mt-4 text-muted-foreground">
        One of the best pieces of advice I received early in life was to travel as often as you can. I am extremely thankful to my family for their support, allowing me to discover the joys, memories and personal growth that traveling creates.
      </p>

      <h2 className="text-xl font-bold">Photos</h2>

      <section
        aria-label="Travel photo gallery coming soon"
        className="mt-4 rounded-2xl border border-dashed border-muted-foreground/30 bg-background/40 p-4"
      >
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div
              key={index}
              className="flex aspect-[4/3] items-center justify-center rounded-xl border border-dashed border-muted-foreground/25 bg-muted/30 text-2xl"
              aria-hidden="true"
            >
              📷
            </div>
          ))}
        </div>
        <p className="mt-3 text-sm font-medium text-muted-foreground">
          Photo gallery coming soon.
        </p>
      </section>

      <h2 className="text-xl font-bold">Where I've Been</h2>

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
