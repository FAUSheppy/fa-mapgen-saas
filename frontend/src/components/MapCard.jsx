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
                <div className="mt-2 break-all">
                    <i>{map.id}</i>
                </div>
            </div>

            {showImage && (
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center bg-black/70"
                    onClick={() => setShowImage(false)}
                >
                    <img
                        src={mapImageUrl(map.id)}
                        alt={map.id.replace(/_preview\.png$/, '')}
                        className="h-[80vw] w-auto"
                    />
                </div>
            )}
        </>
    );
}
