import { ArrowDownIcon, ArrowUpIcon, PlusIcon, TrashIcon } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { saveSocialLinks, useSocialLinks } from "@/lib/api";

interface EditableSocialLink {
  localId: string;
  platform: string;
  url: string;
}

function createEmptyLink(): EditableSocialLink {
  return {
    localId: crypto.randomUUID(),
    platform: "",
    url: "",
  };
}

function toEditableLink(link: { id: string; platform: string; url: string }): EditableSocialLink {
  return {
    localId: link.id,
    platform: link.platform,
    url: link.url,
  };
}

function isValidHttpUrl(value: string) {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}

export function SettingsPage() {
  const { data, isLoading, mutate } = useSocialLinks();
  const [links, setLinks] = useState<EditableSocialLink[]>([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (data) {
      setLinks(data.links.map(toEditableLink));
    }
  }, [data]);

  const addLink = useCallback(() => {
    setLinks((current) => [...current, createEmptyLink()]);
  }, []);

  const removeLink = useCallback((localId: string) => {
    setLinks((current) => current.filter((link) => link.localId !== localId));
  }, []);

  const updateLink = useCallback((localId: string, field: "platform" | "url", value: string) => {
    setLinks((current) => current.map((link) => (link.localId === localId ? { ...link, [field]: value } : link)));
  }, []);

  const moveLink = useCallback((localId: string, direction: -1 | 1) => {
    setLinks((current) => {
      const index = current.findIndex((link) => link.localId === localId);
      const nextIndex = index + direction;
      if (index < 0 || nextIndex < 0 || nextIndex >= current.length) {
        return current;
      }

      const next = [...current];
      [next[index], next[nextIndex]] = [next[nextIndex], next[index]];
      return next;
    });
  }, []);

  const handleSave = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      toast.error("Not authenticated");
      return;
    }

    const cleanedLinks = links
      .map((link) => ({
        platform: link.platform.trim(),
        url: link.url.trim(),
      }))
      .filter((link) => link.platform || link.url);

    const invalidLink = cleanedLinks.find((link) => !link.platform || !isValidHttpUrl(link.url));
    if (invalidLink) {
      toast.error("Each social link needs a platform and a valid http(s) URL.");
      return;
    }

    setSaving(true);
    try {
      await saveSocialLinks(
        token,
        cleanedLinks.map((link, index) => ({ ...link, sort_order: index })),
      );
      toast.success("Social links saved!");
      await mutate();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to save social links");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Site Settings</h1>
        <p className="mt-2 text-sm text-muted-foreground">Manage public site settings.</p>
      </div>

      <section className="space-y-4 rounded-lg border p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold">Social Links</h2>
            <p className="text-sm text-muted-foreground">These links appear in the Find Me On card on the home page.</p>
          </div>
          <Button type="button" variant="outline" onClick={addLink}>
            <PlusIcon />
            Add Link
          </Button>
        </div>

        {isLoading && <p className="text-sm text-muted-foreground">Loading social links…</p>}

        {!isLoading && links.length === 0 && (
          <div className="rounded-md border border-dashed p-6 text-center text-sm text-muted-foreground">
            No social links yet. Add one to get started.
          </div>
        )}

        <div className="space-y-3">
          {links.map((link, index) => (
            <div key={link.localId} className="grid gap-3 rounded-md border p-3 md:grid-cols-[1fr_2fr_auto] md:items-end">
              <div className="space-y-2">
                <Label htmlFor={`platform-${link.localId}`}>Platform</Label>
                <Input
                  id={`platform-${link.localId}`}
                  value={link.platform}
                  onChange={(event) => updateLink(link.localId, "platform", event.target.value)}
                  placeholder="GitHub"
                  maxLength={50}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor={`url-${link.localId}`}>URL</Label>
                <Input
                  id={`url-${link.localId}`}
                  value={link.url}
                  onChange={(event) => updateLink(link.localId, "url", event.target.value)}
                  placeholder="https://github.com/username"
                  maxLength={500}
                />
              </div>

              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => moveLink(link.localId, -1)}
                  disabled={index === 0}
                  aria-label="Move link up"
                >
                  <ArrowUpIcon />
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => moveLink(link.localId, 1)}
                  disabled={index === links.length - 1}
                  aria-label="Move link down"
                >
                  <ArrowDownIcon />
                </Button>
                <Button
                  type="button"
                  variant="destructive"
                  size="icon"
                  onClick={() => removeLink(link.localId)}
                  aria-label="Remove link"
                >
                  <TrashIcon />
                </Button>
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-end">
          <Button type="button" onClick={handleSave} disabled={saving || isLoading}>
            {saving ? "Saving…" : "Save Social Links"}
          </Button>
        </div>
      </section>
    </div>
  );
}

export default SettingsPage;
