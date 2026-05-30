import { useState } from "react";
import { mapImageUrl } from "../api";

export default function MapCard({ map }) {
    const [showImage, setShowImage] = useState(false);

    return (
        <>
            <div className="border rounded p-2 shadow">
                <img
                    src={mapImageUrl(map.id)}
                    alt={map.id}
                    className="w-full cursor-pointer"
                    onClick={() => setShowImage(true)}
                />
                <div className="mt-2 flex items-start gap-2">
                    <i className="break-all flex-1">
                        {map.id.replace(/_preview\.png$/, '')}
                    </i>

                    <button
                        type="button"
                        className="shrink-0 rounded bg-gray-200 px-2 py-1 text-xs hover:bg-gray-300 text-back"
                        onClick={() =>
                            navigator.clipboard.writeText(
                                map.id.replace(/_preview\.png$/, '')
                            )
                        }
                    >
                        Copy
                    </button>
                </div>
            </div>

        {showImage && (
            <div
                className="fixed inset-0 z-50 flex items-center justify-center bg-black/70"
                onClick={() => setShowImage(false)}
            >
                <div
                    className="flex h-[60vw] max-h-[80%] gap-6 rounded bg-[rgb(228,213,167)] p-4"
                    onClick={(e) => e.stopPropagation()}
                >
                    <img
                        src={mapImageUrl(map.id)}
                        alt={map.id.replace(/_preview\.png$/, '')}
                        className="w-auto border border-black rounded-[10px]"
                    />

                    <div className="max-w-md overflow-auto text-sm color-white text-black text-[17px]">
                        <h2 className="p-3 font-semibold">Options</h2>
                        <div className="p-3 space-y-1">
                            {Object.entries(map.options ?? {}).map(([key, value]) => (
                                <div key={key} className="flex gap-2">
                                    <span className="font-bold">{key}:</span>
                                    <span>{String(value)}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        )}
        </>
    );
}
