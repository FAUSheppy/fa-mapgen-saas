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
            const response = await searchMaps(filters);

            // avoid using a new presigned URL for existing ID
            setMaps(prev => {
                const previousById = new Map(
                    prev.map(item => [item.id, item])
                );

                return response.data.map(item => ({
                    ...item,
                    presigned_image_url:
                        previousById.get(item.id)?.presigned_image_url ??
                        item.presigned_image_url,
                }));
            });

        } catch (e) {
            console.error(e);
        }
    }, [filters]);

    useEffect(() => {
        loadMaps();
    }, [loadMaps]);

    useEffect(() => {
        if (!requestId) {
            loadMaps();
            return;
        }
    
        const timer = setInterval(loadMaps, 5000);
    
        return () => clearInterval(timer);
    }, [loadMaps, requestId]);

    return (
        <div style={{ padding: "1rem" }}>
            <h1 className="p-3 text-lg font-bold">Maps</h1>

            <button onClick={loadMaps} type="button"
                    className="
                        px-4 py-2
                        rounded-md
                        bg-blue-600
                        text-white
                        font-medium
                        transition-colors
                        hover:bg-blue-700
                        active:bg-blue-800
                        focus:outline-none
                        focus:ring-2
                        focus:ring-blue-500
                        disabled:opacity-50
                        disabled:cursor-not-allowed
                    ">
                Reload Maps with filters
            </button>

            {requestId && (
                <div className="p3">
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

            {requestId && maps.length < 20 && (
                <div
                    className="
                        border rounded-lg p-6
                        flex flex-col items-center justify-center
                        gap-4 min-h-[200px]
                    "
                >
                    <div
                        className="
                            h-8 w-8
                            border-4 border-gray-300
                            border-t-blue-500
                            rounded-full
                            animate-spin
                        "
                    />

                    <span className="text-sm text-gray-500">
                        Requests queued...
                    </span>
                </div>
            )}

            </div>
        </div>
    );
}
