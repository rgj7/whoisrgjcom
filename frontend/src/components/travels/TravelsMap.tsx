"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { geoNaturalEarth1, geoPath } from "d3-geo";
import { feature } from "topojson-client";
import { select } from "d3-selection";
import { zoom as d3Zoom, zoomIdentity } from "d3-zoom";
import { getCountry, m49ToAlpha2 } from "@/lib/countries";

interface TravelsMapProps {
  visited: string[];
  bucketlist: string[];
}

type MapStatus = "visited" | "bucketlist";

function getCountryFill(status?: MapStatus) {
  if (status === "visited") return "var(--color-map-visited)";
  if (status === "bucketlist") return "var(--color-map-bucket)";
  return "var(--muted)";
}

export function TravelsMap({ visited, bucketlist }: TravelsMapProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const visitedSet = useMemo(() => new Set(visited), [visited]);
  const bucketlistSet = useMemo(() => new Set(bucketlist), [bucketlist]);
  const [tooltip, setTooltip] = useState<{
    code: string;
    name: string;
    status: MapStatus | null;
    x: number;
    y: number;
  } | null>(null);

  const applyStatusesToPaths = (svgEl: SVGSVGElement) => {
    const paths = svgEl.querySelectorAll<SVGPathElement>("path[data-country]");
    for (const pathEl of paths) {
      const code = pathEl.dataset.country;
      if (!code) continue;

      const status = visitedSet.has(code)
        ? "visited"
        : bucketlistSet.has(code)
          ? "bucketlist"
          : undefined;
      pathEl.dataset.status = status ?? "";
      pathEl.style.fill = getCountryFill(status);
    }
  };

  const handleMouseMove = (e: MouseEvent, code: string, status?: MapStatus) => {
    const info = getCountry(code);
    if (!info) return;

    setTooltip({
      code,
      name: info.name,
      status: status ?? null,
      x: e.offsetX,
      y: e.offsetY,
    });
  };

  // Load world data and render
  useEffect(() => {
    let cancelled = false;

    async function loadAndRender() {
      try {
        const world = await import("world-atlas/countries-110m.json");
        if (cancelled) return;

        // Use `as any` — world-atlas JSON shape doesn't perfectly match topojson types
        const worldObj = world as any;
        const collection = feature(worldObj, worldObj.objects.countries) as any;

        const svgEl = svgRef.current;
        const containerEl = containerRef.current;
        if (!svgEl || !containerEl) return;

        const width = containerEl.clientWidth;
        const height = Math.round(width * 0.45);

        const projection = geoNaturalEarth1().fitSize([width, height], collection);
        const path = geoPath(projection);
        if (!path) return;

        // Clear existing
        while (svgEl.firstChild) {
          svgEl.removeChild(svgEl.firstChild);
        }

        svgEl.setAttribute("width", String(width));
        svgEl.setAttribute("height", String(height));
        svgEl.style.width = "100%";
        svgEl.style.height = "100%";

        // Create a group for the zoomable content
        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("class", "map-features");
        svgEl.appendChild(g);

        // Draw countries
        const features = (collection as any).features;
        for (const feat of features) {
          if (!feat) continue;
          const m49Code = feat.id?.toString();
          if (!m49Code) continue;

          const d = path(feat);
          if (!d) continue;

          // Convert UN M49 code to ISO alpha-2 to match travels data
          const alpha2 = m49ToAlpha2(m49Code);
          if (!alpha2) continue;

          const pathEl = document.createElementNS("http://www.w3.org/2000/svg", "path");
          pathEl.setAttribute("d", d);
          pathEl.dataset.country = alpha2;
          pathEl.dataset.status = "";
          pathEl.style.fill = getCountryFill();
          pathEl.style.stroke = "var(--border)";
          pathEl.style.strokeWidth = "0.5";
          pathEl.style.strokeLinejoin = "round";
          pathEl.style.cursor = "pointer";
          pathEl.style.transition = "fill 0.15s ease";

          // Hover handlers
          pathEl.addEventListener("mouseenter", () => {
            pathEl.style.fill = "var(--color-map-hover)";
          });
          pathEl.addEventListener("mouseleave", () => {
            const status = pathEl.dataset.status as MapStatus | undefined;
            pathEl.style.fill = getCountryFill(status);
            setTooltip(null);
          });
          pathEl.addEventListener("mousemove", (e) => {
            const status = pathEl.dataset.status as MapStatus | undefined;
            handleMouseMove(e, alpha2, status);
          });

          g.appendChild(pathEl);
        }

        // Apply current visited/bucketlist state after initial draw
        applyStatusesToPaths(svgEl)

        // Setup zoom behavior
        const zoomBehavior = d3Zoom()
          .scaleExtent([1, 8])
          .on("zoom", (event: any) => {
            g.setAttribute("transform", event.transform.toString());
          });

        const initialTransform = zoomIdentity
          .translate(-172.50079204922906, 30.079296208018377)
          .scale(1.3195079107728944);

        select(svgEl)
          .style("touch-action", "none")
          .call(zoomBehavior as any)
          .call((zoomBehavior as any).transform, initialTransform);
      } catch (err) {
        console.error("Failed to load world map:", err);
      }
    }

    loadAndRender();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const svgEl = svgRef.current;
    if (!svgEl) return;

    applyStatusesToPaths(svgEl);
  }, [visitedSet, bucketlistSet]);

  return (
    <div ref={containerRef} className="relative w-full aspect-video rounded-xl overflow-hidden border">
      <svg ref={svgRef} className="w-full h-full map-zoom" />
      {tooltip && (
        <div
          className="absolute pointer-events-none z-50 px-3 py-2 rounded-lg shadow-lg text-sm bg-popover text-popover-foreground border"
          style={{
            left: Math.min(tooltip.x + 12, (containerRef.current?.clientWidth ?? 800) - 160),
            top: Math.min(tooltip.y + 12, (containerRef.current?.clientHeight ?? 360) - 40),
          }}
        >
          <div className="font-medium flex items-center gap-1.5">
            <i className={`fi fi-${tooltip.code.toLowerCase()}`} />
            {tooltip.name}
          </div>
          {tooltip.status && (
            <div className="text-muted-foreground text-xs capitalize">{tooltip.status}</div>
          )}
        </div>
      )}
    </div>
  );
}

export default TravelsMap;
