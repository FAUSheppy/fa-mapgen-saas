import { NavLink } from "react-router-dom";
import { queueSize } from "../api";
import { useState, useEffect } from "react";

export default function NavBar() {
    const linkClass = ({ isActive }) =>
        [
            "rounded px-3 py-2 transition-colors",
            isActive
                ? "bg-gray-200 text-gray-900"
                : "text-gray-800 hover:bg-gray-200",
        ].join(" ");

    const handleMainClick = (e) => {
        if (location.pathname === "/") {
            e.preventDefault();
            window.location.href = "/";
        }
    };

    const [queueCount, setQueueCount] = useState(-1);

    useEffect(() => {
        const loadQueueSize = async () => {
            try {
                const response = await queueSize();
                setQueueCount(response.data.count);
            } catch (error) {
                console.error(error);
            }
        };

        loadQueueSize();

        // Refresh every 30 seconds
        const interval = setInterval(
            loadQueueSize,
            1000
        );

        return () => clearInterval(interval);
    }, []);

    const queueColor =
        queueCount > 200
            ? "text-red-700 font-bold"
            : queueCount > 50
              ? "text-orange-600 font-semibold"
              : "text-green-700";


   return (
        <nav className="border-b bg-[#bf6868]">
            <div className="flex max-w-6xl items-center gap-4 px-4 py-3">
                <NavLink
                    to="/"
                    className={linkClass}
                    onClick={handleMainClick}
                >
                    Main Page / Reload Maps
                </NavLink>

                <NavLink
                    to="/new"
                    className={linkClass}
                >
                    Request New Maps
                </NavLink>

                {queueCount >= 0 && (
                    <div
                        className={`ml-auto rounded bg-white px-3 py-1 text-sm ${queueColor}`}
                    >
                        Queue Size: {queueCount}
                    </div>
                )}  
            </div>
        </nav>
    );
}
