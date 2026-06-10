import { BrowserRouter, Routes, Route } from "react-router-dom";

import MapBrowser from "./pages/MapBrowser";
import NewRequest from "./pages/NewRequest";
import NavBar from "./components/NavBar";
import { UserProvider } from "./context/UserContext"

export default function App() {
    return (
        <BrowserRouter>
            <UserProvider>
                <NavBar />
                <Routes>
                    <Route path="/" element={<MapBrowser />} />
                    <Route path="/new" element={<NewRequest />} />
                </Routes>
            </UserProvider>
        </BrowserRouter>
    );
}
