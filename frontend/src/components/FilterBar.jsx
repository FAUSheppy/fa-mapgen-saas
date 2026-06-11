import { FILTERS } from "../constants/filters";
import { useEffect, useState, useCallback } from "react";
import { useUser } from "../context/UserContext";

export default function FilterBar({ filters, setFilters }) {
    const styleSelected = Boolean(filters.style);
    const [localValue, setLocalValue] = useState({});
    const { user, userLoading } = useUser();

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

    const updateCache = (field, value) => {
        setLocalValue((prev) => ({
            ...prev,
            [field]: value === "" ? undefined : value,
        }));
    };


    return (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3 pt-5">

            <div className="flex flex-wrap gap-4 w-100">
                <input
                    type="text"
                    value={filters.user ?? ""}
                    onChange={(e) =>
                        update(
                            "user",
                            e.target.value || undefined
                        )
                    }
                    placeholder="Liked by user (% for partial match)"
                    className="rounded border p-2"
                />

                <label className="flex items-center gap-2">
                    <input
                        type="checkbox"
                        checked={Boolean(filters.curators)}
                        onChange={(e) =>
                            update(
                                "curators",
                                e.target.checked ? true : undefined
                            )
                        }
                    />
                    Liked by curators
                </label>

                <label className="flex items-center gap-2">
                    <input
                        type="checkbox"
                        checked={Boolean(filters.order_by_likes)}
                        onChange={(e) =>
                            update(
                                "order_by_likes",
                                e.target.checked ? true : undefined
                            )
                        }
                    />
                    Order by likes
                </label>

                {user?.user_id ? (
                <label className="flex items-center gap-2">
                    <input
                        type="checkbox"
                        checked={Boolean(filters.voted_self)}
                        onChange={(e) =>
                            update(
                                "voted_self",
                                e.target.checked ? true : undefined
                            )
                        }
                    />
                    Voted on by you
                </label>
                ) :  (<p>Login to filer for your own votes.</p>)}
            </div>

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
                                        localValue[
                                            filter.key
                                        ] ?? filter.min
                                    }
                                    onChange={(e) => updateCache(filter.key, e.target.value || undefined)}
                                    onMouseUp={() => update(filter.key, localValue[filter.key] || undefined)}
                                    onTouchEnd={() => update(filter.key, localValue[filter.key] || undefined)}
                                    className="w-full disabled:cursor-not-allowed"
                                />

                                <div className="text-sm text-gray-500">
                                    {localValue[
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