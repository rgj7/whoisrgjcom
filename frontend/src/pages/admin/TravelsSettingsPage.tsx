"use client";

import { useState, useEffect, useCallback } from "react";
import { toast } from "sonner";
import { MultiCombobox, type ComboboxOption } from "@/components/ui/combobox";
import { useTravels, saveTravels } from "@/lib/api";
import { getAllCountriesSorted } from "@/lib/countries";

export function TravelsSettingsPage() {
  const { data, isLoading, mutate } = useTravels();
  const [visited, setVisited] = useState<string[]>([]);
  const [bucketlist, setBucketlist] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [options] = useState<ComboboxOption[]>(() =>
    getAllCountriesSorted().map((c) => ({ value: c.value, label: c.label })),
  );

  const sortCodesByCountryName = useCallback((codes: string[]) => {
    const labelByCode = new Map(options.map((o) => [o.value, o.label.replace(/<[^>]*>/g, "").trim()]));
    return [...codes].sort((a, b) => {
      const aLabel = labelByCode.get(a) ?? a;
      const bLabel = labelByCode.get(b) ?? b;
      return aLabel.localeCompare(bLabel);
    });
  }, [options]);

  // Populate from SWR data on mount / data change
  useEffect(() => {
    if (data) {
      setVisited(sortCodesByCountryName(data.visited));
      setBucketlist(sortCodesByCountryName(data.bucketlist));
    }
  }, [data, sortCodesByCountryName]);

  // Auto-move: selecting in one list removes from the other
  const handleVisitedChange = useCallback((selected: string[]) => {
    setVisited(sortCodesByCountryName(selected));
    setBucketlist((prev) => sortCodesByCountryName(prev.filter((c) => !selected.includes(c))));
  }, [sortCodesByCountryName]);

  const handleBucketlistChange = useCallback((selected: string[]) => {
    setBucketlist(sortCodesByCountryName(selected));
    setVisited((prev) => sortCodesByCountryName(prev.filter((c) => !selected.includes(c))));
  }, [sortCodesByCountryName]);

  const handleSave = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      toast.error("Not authenticated");
      return;
    }

    setSaving(true);
    try {
      await saveTravels(token, { visited, bucketlist });
      toast.success("Travels saved!");
      mutate(); // invalidate SWR cache
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to save travels");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Travels Settings</h1>

      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-medium mb-2">
            Countries I've visited ({visited.length})
          </h2>
          <MultiCombobox
            options={options}
            selected={visited}
            onSelectedChange={handleVisitedChange}
            placeholder="Search and add countries…"
            emptyText="No countries found."
          />
        </div>

        <div>
          <h2 className="text-lg font-medium mb-2">
            Countries I want to visit ({bucketlist.length})
          </h2>
          <MultiCombobox
            options={options}
            selected={bucketlist}
            onSelectedChange={handleBucketlistChange}
            placeholder="Search and add countries…"
            emptyText="No countries found."
          />
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving || isLoading}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? "Saving…" : "Save Travels"}
        </button>
      </div>
    </div>
  );
}

export default TravelsSettingsPage;
