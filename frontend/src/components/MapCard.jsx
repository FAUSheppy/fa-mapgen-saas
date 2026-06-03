import { useEffect, useState } from "react";
import { mapImageUrl } from "../api";

export default function MapCard({ map }) {
    const [showImage, setShowImage] = useState(false);
    const [loaded, setLoaded] = useState(false);

    const grayPlaceholder =
        "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2Ij48cmVjdCB3aWR0aD0iMjU2IiBoZWlnaHQ9IjI1NiIgZmlsbD0iIzgwODA4MCIvPjwvc3ZnPg==";
    
    // component mount
    const [visible, setVisible] = useState(false);
    useEffect(() => {
        requestAnimationFrame(() => setVisible(true));
    }, []);

    useEffect(() => {
        setLoaded(false);

        const img = new Image();
        img.src = map.presigned_image_url;
        img.onload = () => setLoaded(true);
    }, [map.presigned_image_url]);

    return (
        <>
            <div className={`
                    border rounded p-2 shadow transition-all duration-300 ${visible ? "opacity-100" : "opacity-0"}
                `}>
                <img
                    src={map.presigned_image_url}
                    alt={map.id}
                    width="265"
                    height="265"
                    className={`w-[256px] mx-auto cursor-pointer transition-opacity transition-duration-700 ${
                        loaded ? "opacity-100" : "opacity-0"
                    }`}
                    onLoad={() => setLoaded(true)}
                    onClick={() => setShowImage(true)}
                />
                <div className="mt-2 w-[256px] mx-auto">

                    <i className="w-full break-all">
                        {map.id.replace(/_preview\.png$/, '')}
                    </i>

                    <button
                        type="button"
                        className="w-full transition active:scale-95 mt-2 rounded bg-gray-200 px-2 py-1 text-xs hover:bg-gray-300 text-black"
                        onClick={() =>
                            navigator.clipboard.writeText(
                                map.id.replace(/_preview\.png$/, '')
                            )
                        }
                    >
                        Copy Seed
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
                        src={map.presigned_image_url}
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
