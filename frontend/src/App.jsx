import { BrowserRouter, Routes, Route } from "react-router-dom";

import MapBrowser from "./pages/MapBrowser";
import NewRequest from "./pages/NewRequest";
import NavBar from "./components/NavBar";

export default function App() {
    return (
        <BrowserRouter>
            <NavBar />
            <Routes>
                <Route path="/" element={<MapBrowser />} />
                <Route path="/new" element={<NewRequest />} />
            </Routes>
        </BrowserRouter>
    );
}
