"use client";

import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

export interface ComboboxOption {
  value: string;
  label: string;
}

interface ComboboxProps {
  options: ComboboxOption[];
  value: string;
  onValueChange: (value: string) => void;
  placeholder?: string;
  emptyText?: string;
}

export function Combobox({
  options,
  value,
  onValueChange,
  placeholder = "Select…",
  emptyText = "No results found.",
}: ComboboxProps) {
  const [open, setOpen] = React.useState(false);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-full justify-between"
        >
          {value
            ? options.find((option) => option.value === value)?.label
            : placeholder}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0">
        <Command>
          <CommandInput placeholder={placeholder} />
          <CommandList>
            <CommandEmpty>{emptyText}</CommandEmpty>
            <CommandGroup>
              {options.map((option) => (
                <CommandItem
                  key={option.value}
                  value={option.value}
                  onSelect={() => {
                    onValueChange(option.value === value ? "" : option.value);
                    setOpen(false);
                  }}
                >
                  {option.label}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

interface MultiComboboxProps {
  options: ComboboxOption[];
  selected: string[];
  onSelectedChange: (selected: string[]) => void;
  onCreateNew?: (value: string) => void;
  searchTags?: (query: string) => Promise<ComboboxOption[]>;
  placeholder?: string;
  emptyText?: string;
}

export function MultiCombobox({
  options,
  selected,
  onSelectedChange,
  onCreateNew,
  searchTags,
  placeholder = "Select…",
  emptyText = "No results found.",
}: MultiComboboxProps) {
  const [open, setOpen] = React.useState(false);
  const [inputValue, setInputValue] = React.useState("");
  const [searchOptions, setSearchOptions] = React.useState<ComboboxOption[]>([]);
  const searchTimeoutRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);
  const inlineInputRef = React.useRef<HTMLInputElement>(null);
  const commandInputRef = React.useRef<HTMLInputElement>(null);

  // Merge search results with provided options, excluding already-selected
  const displayedOptions = React.useMemo(() => {
    const combined = [...options, ...searchOptions];
    const seen = new Set<string>();
    return combined.filter((opt) => {
      if (selected.includes(opt.value)) return false;
      if (seen.has(opt.value)) return false;
      seen.add(opt.value);
      return true;
    });
  }, [options, searchOptions, selected]);

  const filteredOptions = displayedOptions.filter(
    (option) =>
      option.label.toLowerCase().includes(inputValue.toLowerCase()),
  );

  // Live-search tags when input changes (debounced)
  React.useEffect(() => {
    if (!searchTags) return;
    const query = inputValue.trim();
    if (!query) {
      setSearchOptions([]);
      return;
    }
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    searchTimeoutRef.current = setTimeout(() => {
      searchTags(query).then(setSearchOptions).catch(() => {});
    }, 300);
    return () => {
      if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    };
  }, [searchTags, inputValue]);

  const handleSelect = (value: string) => {
    if (selected.includes(value)) return;
    onSelectedChange([...selected, value]);
    setInputValue("");
  };

  const handleRemove = (value: string) => {
    onSelectedChange(selected.filter((s) => s !== value));
  };

  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && inputValue.trim() && onCreateNew) {
      e.preventDefault();
      const trimmed = inputValue.trim();
      const existing = displayedOptions.find(
        (o) => o.label.toLowerCase() === trimmed.toLowerCase(),
      );
      if (existing && !selected.includes(existing.value)) {
        handleSelect(existing.value);
      } else {
        onCreateNew(trimmed);
        setInputValue("");
      }
    }
  };

  const handleCommandKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && inputValue.trim() && onCreateNew) {
      e.preventDefault();
      const trimmed = inputValue.trim();
      const existing = displayedOptions.find(
        (o) => o.label.toLowerCase() === trimmed.toLowerCase(),
      );
      if (existing && !selected.includes(existing.value)) {
        handleSelect(existing.value);
      } else {
        onCreateNew(trimmed);
        setInputValue("");
      }
    }
  };

  React.useEffect(() => {
    if (open) {
      // Focus the inline input inside the PopoverTrigger so focus never leaves the trigger
      // and Radix doesn't close the popover
      const timer = setTimeout(() => {
        inlineInputRef.current?.focus();
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [open]);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-full justify-start min-h-9"
        >
          <div className="flex flex-wrap gap-1">
            {selected.map((s) => {
              const option = options.find((o) => o.value === s) ?? searchOptions.find((o) => o.value === s);
              return (
                <Badge
                  key={s}
                  variant="secondary"
                  className="cursor-pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemove(s);
                  }}
                >
                  {option?.label ?? s}
                  <span className="ml-1 opacity-60 hover:opacity-100">×</span>
                </Badge>
              );
            })}
            <input
              ref={inlineInputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleInputKeyDown}
              onFocus={() => setOpen(true)}
              placeholder={selected.length === 0 ? placeholder : undefined}
              className="flex-1 bg-transparent outline-hidden min-w-[80px] px-1"
            />
          </div>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0">
        <Command filter={(value, search) => {
          const option = displayedOptions.find(o => o.value === value);
          if (!option) return 0;
          return option.label.toLowerCase().includes(search.toLowerCase()) ? 1 : 0;
        }}>
          <CommandInput
            ref={commandInputRef}
            value={inputValue}
            onValueChange={setInputValue}
            onKeyDown={handleCommandKeyDown}
            placeholder={placeholder}
          />
          <CommandList>
            <CommandEmpty>{emptyText}</CommandEmpty>
            <CommandGroup>
              {filteredOptions.map((option) => (
                <CommandItem
                  key={option.value}
                  value={option.value}
                  onSelect={() => {
                    handleSelect(option.value);
                    setOpen(false);
                  }}
                >
                  {option.label}
                </CommandItem>
              ))}
              {onCreateNew && inputValue.trim() && !displayedOptions.find(o => o.label.toLowerCase() === inputValue.trim().toLowerCase()) && (
                <CommandItem
                  value={`create-${inputValue.trim().toLowerCase()}`}
                  onSelect={() => {
                    onCreateNew?.(inputValue.trim());
                    setInputValue("");
                    setOpen(false);
                  }}
                >
                  Create "{inputValue.trim()}"
                </CommandItem>
              )}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
