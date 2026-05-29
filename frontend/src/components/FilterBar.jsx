export default function FilterBar({ filters, setFilters }) {
    const update = (field, value) => {
        setFilters((prev) => ({
            ...prev,
            [field]: value === "" ? undefined : value,
        }));
    };

    return (
        <div
            style={{
                display: "grid",
                gridTemplateColumns: "repeat(4,1fr)",
                gap: "1rem",
            }}
        >
            <input
                placeholder="map_size"
                value={filters.map_size || ""}
                onChange={(e) =>
                    update("map_size", e.target.value)
                }
            />

            <input
                type="number"
                placeholder="spawn_count"
                value={filters.spawn_count || ""}
                onChange={(e) =>
                    update(
                        "spawn_count",
                        Number(e.target.value)
                    )
                }
            />

            <input
                type="number"
                placeholder="num_teams"
                value={filters.num_teams || ""}
                onChange={(e) =>
                    update(
                        "num_teams",
                        Number(e.target.value)
                    )
                }
            />

            <input
                placeholder="style"
                value={filters.style || ""}
                onChange={(e) =>
                    update("style", e.target.value)
                }
            />

            <input
                placeholder="terrain_symmetry"
                value={filters.terrain_symmetry || ""}
                onChange={(e) =>
                    update(
                        "terrain_symmetry",
                        e.target.value
                    )
                }
            />

            <input
                placeholder="texture_style"
                value={filters.texture_style || ""}
                onChange={(e) =>
                    update(
                        "texture_style",
                        e.target.value
                    )
                }
            />

            <input
                placeholder="terrain_style"
                value={filters.terrain_style || ""}
                onChange={(e) =>
                    update(
                        "terrain_style",
                        e.target.value
                    )
                }
            />

            <input
                placeholder="resource_style"
                value={filters.resource_style || ""}
                onChange={(e) =>
                    update(
                        "resource_style",
                        e.target.value
                    )
                }
            />

            <input
                placeholder="prop_style"
                value={filters.prop_style || ""}
                onChange={(e) =>
                    update(
                        "prop_style",
                        e.target.value
                    )
                }
            />

            <input
                type="number"
                step="0.1"
                placeholder="reclaim_density"
                value={filters.reclaim_density || ""}
                onChange={(e) =>
                    update(
                        "reclaim_density",
                        Number(e.target.value)
                    )
                }
            />

            <input
                type="number"
                step="0.1"
                placeholder="resource_density"
                value={filters.resource_density || ""}
                onChange={(e) =>
                    update(
                        "resource_density",
                        Number(e.target.value)
                    )
                }
            />
        </div>
    );
}
