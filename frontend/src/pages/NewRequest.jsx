import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { createRequest } from "../api";

export default function NewRequest() {
    const navigate = useNavigate();

    const [form, setForm] = useState({
        map_size: "",
        spawn_count: "",
        num_teams: "",
        style: "",
        terrain_symmetry: "",
        texture_style: "",
        terrain_style: "",
        resource_style: "",
        prop_style: "",
        reclaim_density: "",
        resource_density: "",
    });

    const update = (field, value) => {
        setForm((prev) => ({
            ...prev,
            [field]: value,
        }));
    };

    const submit = async (e) => {
        e.preventDefault();

        const response =
            await createRequest(form);

        navigate(
            `/?request-id=${response.data.request_id}`
        );
    };

    return (
        <form
            onSubmit={submit}
            style={{
                display: "grid",
                gap: "1rem",
                maxWidth: "500px",
                margin: "2rem auto",
            }}
        >
            {Object.keys(form).map((field) => (
                <input
                    key={field}
                    placeholder={field}
                    value={form[field]}
                    onChange={(e) =>
                        update(
                            field,
                            e.target.value
                        )
                    }
                />
            ))}

            <button type="submit">
                Create Request
            </button>
        </form>
    );
}
