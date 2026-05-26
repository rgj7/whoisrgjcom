"use client";

import { useMemo } from "react";
import { getCountry } from "@/lib/countries";

interface TravelsBadgesProps {
  countries: string[];
  title: string;
}

const CONTINENT_ORDER = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania", "Antarctica"];

export function TravelsBadges({ countries, title }: TravelsBadgesProps) {
  const grouped = useMemo(() => {
    const groups = new Map<string, { code: string; name: string }[]>();

    for (const code of countries) {
      const info = getCountry(code);
      if (!info) continue;

      const name = info.name;
      if (!groups.has(info.continent)) {
        groups.set(info.continent, []);
      }
      groups.get(info.continent)!.push({ code, name });
    }

    for (const [, entries] of groups) {
      entries.sort((a, b) => a.name.localeCompare(b.name));
    }

    return Array.from(groups.entries()).sort((a, b) => {
      if (b[1].length !== a[1].length) return b[1].length - a[1].length;
      const idxA = CONTINENT_ORDER.indexOf(a[0]);
      const idxB = CONTINENT_ORDER.indexOf(b[0]);
      if (idxA === -1 && idxB === -1) return 0;
      if (idxA === -1) return 1;
      if (idxB === -1) return -1;
      return idxA - idxB;
    });
  }, [countries]);

  if (grouped.length === 0) {
    return (
      <div>
        <h2 className="text-xl font-semibold mb-4">{title}</h2>
        <p className="text-muted-foreground text-sm">No countries added yet.</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      {grouped.map(([continent, entries]) => (
        <div key={continent} className="mb-6 last:mb-0">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">{continent}</h3>
          <div className="flex flex-wrap gap-2">
            {entries.map(({ code, name }) => (
              <span
                key={code}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm bg-secondary text-secondary-foreground select-none"
              >
                <span className={`fi fi-${code.toLowerCase()}`} />
                <span>{name}</span>
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default TravelsBadges;
