import { NavLink } from "react-router-dom";

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

    return (
        <nav className="border-b bg-[#bf6868]">
            <div className="flex max-w-6xl gap-2 px-4 py-3">
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

            </div>
        </nav>
    );
}
