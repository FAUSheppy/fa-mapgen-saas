import { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "react-router-dom";

import { searchMaps } from "../api";
import FilterBar from "../components/FilterBar";
import MapCard from "../components/MapCard";

export default function MapBrowser() {
    const [searchParams] = useSearchParams();

    const requestId =
        searchParams.get("request-id");

    const [maps, setMaps] = useState([]);

    const [filters, setFilters] = useState(
        requestId
            ? { request_id: requestId }
            : {}
    );

    const loadMaps = useCallback(async () => {
        try {
            const response =
                await searchMaps(filters);

            setMaps(response.data);
        } catch (e) {
            console.error(e);
        }
    }, [filters]);

    useEffect(() => {
        loadMaps();
    }, [loadMaps]);

    useEffect(() => {
        const timer = setInterval(
            loadMaps,
            5000
        );

        return () =>
            clearInterval(timer);
    }, [loadMaps]);

    return (
        <div style={{ padding: "1rem" }}>
            <h1>Maps</h1>

            {requestId && (
                <div>
                    Request ID: {requestId}
                </div>
            )}

            <FilterBar
                filters={filters}
                setFilters={setFilters}
            />

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns:
                        "repeat(auto-fill,minmax(300px,1fr))",
                    gap: "1rem",
                    marginTop: "1rem",
                }}
            >
                {maps
                    .slice(0, 20)
                    .map((map) => (
                        <MapCard
                            key={map.id}
                            map={map}
                        />
                    ))}
            </div>
        </div>
    );
}
