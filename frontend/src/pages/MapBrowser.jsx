import { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "react-router-dom";

import { searchMaps } from "../api";
import FilterBar from "../components/FilterBar";
import MapCard from "../components/MapCard";

export default function MapBrowser() {

    const [loading, setLoading] = useState(false);
    const [maps, setMaps] = useState([]);
    const [searchParams, setSearchParams] = useSearchParams();


    const requestId = searchParams.get("request-id");
    const [filters, setFilters] = useState(
        requestId
            ? { request_id: requestId }
            : {}
    );

    async function resetRayAndloadMaps(){
        searchParams.delete("ray_id")
        setSearchParams(searchParams);
        loadMaps()
    }

    const loadMaps = useCallback(async () => {
        try {
            setLoading(true);

            const response = await searchMaps(filters);

            const { result, seed } = response.data;

            // Persist seed in URL as ray_id if not already present
            const params = new URLSearchParams(window.location.search);

            if (!params.get("ray_id") && seed) {
                params.set("ray_id", seed);

                window.history.replaceState(
                    {},
                    "",
                    `${window.location.pathname}?${params.toString()}`
                );
            }

            // avoid using a new presigned URL for existing ID
            setMaps(prev => {
                const previousById = new Map(
                    prev.map(item => [item.id, item])
                );

                return result.map(item => ({
                    ...item,
                    presigned_image_url:
                        previousById.get(item.id)?.presigned_image_url ??
                        item.presigned_image_url,
                }));
            });

        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
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

            { !requestId && (
                <button onClick={resetRayAndloadMaps} type="button"
                        disabled={loading}
                        className="
                            px-4 py-2
                            w-80
                            h-10
                            transition active:scale-95 
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
                    {loading && (
                        <svg
                            className="h-4 w-4 animate-spin m-auto"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                        >
                            <circle
                                className="opacity-25"
                                cx="24"
                                cy="24"
                                r="20"
                                stroke="currentColor"
                                strokeWidth="4"
                            />
                            <path
                                className="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                            />
                        </svg>
                    )}
                    {loading ? "" : "Reload Maps with filters"}
                </button>
            )}

            {requestId && (
                <div className="my-3">
                    <i>You are viewing a specific Map request.</i><br></br>
                    <b>Request ID:</b> {requestId}
                </div>
            )}

            {!requestId && (
                <FilterBar
                    filters={filters}
                    setFilters={setFilters}
                />
            )}

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
                            onVote={(vote) => {
                                setMaps(prev =>
                                    prev.map(m =>
                                        m.id === map.id
                                            ? { ...m, vote }
                                            : m
                                    )
                                );
                            }}
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
                        { 20 - maps.length } more requests queued...
                    </span>
                </div>
            )}

            </div>
        </div>
    );
}
