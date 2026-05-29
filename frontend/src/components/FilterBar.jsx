import { FILTERS } from "../constants/filters";

export default function FilterBar({ filters, setFilters }) {
    const update = (field, value) => {
        setFilters((prev) => ({
            ...prev,
            [field]: value === "" ? undefined : value,
        }));
    };

    return (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {FILTERS.map((filter) => (
                <div key={filter.key} className="flex flex-col gap-2">
                    <label className="text-sm font-medium">
                        {filter.label}
                    </label>

                    {filter.type === "select" ? (
                        <select
                            className="rounded border p-2"
                            value={filters[filter.key] ?? ""}
                            onChange={(e) =>
                                update(
                                    filter.key,
                                    e.target.value || undefined
                                )
                            }
                        >
                            <option value="">Any</option>

                            {filter.options.map((option) => (
                                <option
                                    key={option}
                                    value={option}
                                >
                                    {option}
                                </option>
                            ))}
                        </select>
                    ) : (
                        <>
                            <input
                                type="range"
                                min={filter.min}
                                max={filter.max}
                                step={filter.step}
                                value={
                                    filters[filter.key] ??
                                    filter.min
                                }
                                onChange={(e) =>
                                    update(
                                        filter.key,
                                        Number(e.target.value)
                                    )
                                }
                                className="w-full"
                            />

                            <div className="text-sm text-gray-500">
                                {filters[filter.key] ??
                                    filter.min}
                            </div>
                        </>
                    )}
                </div>
            ))}
        </div>
    );
}
