import { FILTERS } from "../constants/filters";

export default function FilterBar({ filters, setFilters }) {
    const styleSelected = Boolean(filters.style);

    const allowedWhenStyleSelected = [
        "style",
        "map_size",
        "spawn_count",
        "num_teams",
    ];

    const update = (field, value) => {
        setFilters((prev) => ({
            ...prev,
            [field]: value === "" ? undefined : value,
        }));
    };

    return (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3 pt-5">
            {FILTERS.map((filter) => {
                const disabled =
                    styleSelected &&
                    !allowedWhenStyleSelected.includes(filter.key);

                return (
                    <div
                        key={filter.key}
                        className={`flex flex-col gap-2 ${
                            disabled ? "opacity-50" : ""
                        }`}
                    >
                        <label className="text-sm font-medium">
                            {filter.label}
                        </label>

                        {filter.type === "select" ? (
                            <select
                                disabled={disabled}
                                className="rounded border p-2 chromium-select-fix disabled:bg-gray-100 disabled:cursor-not-allowed"
                                value={filters[filter.key] ?? ""}
                                onChange={(e) =>
                                    update(
                                        filter.key,
                                        e.target.value ||
                                            undefined
                                    )
                                }
                            >
                                <option value="">Any</option>

                                {filter.options.map((option) => (
                                    <option
                                        key={option}
                                        value={option}
                                        className="chromium-select-fix"
                                    >
                                        {option}
                                    </option>
                                ))}
                            </select>
                        ) : (
                            <>
                                <input
                                    disabled={disabled}
                                    type="range"
                                    min={filter.min}
                                    max={filter.max}
                                    step={filter.step}
                                    value={
                                        filters[
                                            filter.key
                                        ] ?? filter.min
                                    }
                                    onChange={(e) =>
                                        update(
                                            filter.key,
                                            Number(
                                                e.target.value
                                            )
                                        )
                                    }
                                    className="w-full disabled:cursor-not-allowed"
                                />

                                <div className="text-sm text-gray-500">
                                    {filters[
                                        filter.key
                                    ] ?? filter.min}
                                </div>
                            </>
                        )}
                    </div>
                );
            })}
        </div>
    );
}