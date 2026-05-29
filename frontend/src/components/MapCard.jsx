import { mapImageUrl } from "../api";

export default function MapCard({ map }) {
    return (
        <div className="border rounded p-2 shadow">
            <img
                src={mapImageUrl(map.id)}
                alt={map.id}
                className="w-full"
            />

            <div className="mt-2">
                <i>{map.id}</i>
            </div>
        </div>
    );
}
