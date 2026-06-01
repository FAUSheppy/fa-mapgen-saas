import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { createRequest } from "../api";
import { FILTERS } from "../constants/filters";

export default function NewRequest() {



    const initialForm = Object.fromEntries(
        FILTERS.map((f) => [
            f.key,
            f.defaultValue ?? null,
        ])
    );
    const [form, setForm] = useState(initialForm);

    const navigate = useNavigate();
    const styleSelected = Boolean(form.style);
    const allowedWhenStyleSelected = [
        "map_size",
        "spawn_count",
        "num_teams",
        "style",
    ];

    const update = (field, value) => {
        setForm((prev) => ({
            ...prev,
            [field]: value,
        }));
    };

    const submit = async (e) => {
        e.preventDefault();

        const response = await createRequest(form);

        navigate(
            `/?request-id=${response.data.request_id}`
        );
    };


    return (
        <div className="mt-3">
        <div className="m-3">
            <h1>Leave fields unchanged for random values</h1>
        </div>
        <form
            onSubmit={submit}
            className="mx-auto grid max-w-4xl gap-6"
        >
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {FILTERS.map((filter) => {
                    const disabled =
                        styleSelected &&
                        !allowedWhenStyleSelected.includes(filter.key);

                    return (
                        <div
                            key={filter.key}
                            className={`flex flex-col gap-2 ${
                                disabled ? "opacity-50" : ""
                            }`}
                        >
                            <label className="text-sm font-medium">
                                {filter.label}
                            </label>

                            {filter.type === "select" ? (
                                <select
                                    disabled={disabled}
                                    className="rounded border p-2 chromium-select-fix disabled:cursor-not-allowed disabled:bg-gray-100"
                                    value={form[filter.key] ?? ""}
                                    onChange={(e) =>
                                        update(
                                            filter.key,
                                            e.target.value
                                        )
                                    }
                                >
                                    <option value="">
                                        Select...
                                    </option>

                                    {filter.options.map((option) => (
                                        <option
                                            key={option}
                                            value={option}
                                        >
                                            {option}
                                        </option>
                                    ))}
                                </select>
                            ) : (
                                <>
                                    <input
                                        disabled={disabled}
                                        type="range"
                                        min={filter.min}
                                        max={filter.max}
                                        step={filter.step}
                                        value={
                                            form[filter.key] ??
                                            filter.min
                                        }
                                        onChange={(e) =>
                                            update(
                                                filter.key,
                                                Number(
                                                    e.target.value
                                                )
                                            )
                                        }
                                        className="w-full disabled:cursor-not-allowed"
                                    />

                                    <div className="text-sm text-gray-500">
                                        {form[filter.key] ??
                                            filter.min}
                                    </div>
                                </>
                            )}
                        </div>
                    );
                })}
            </div>

            <button
                type="submit"
                className="rounded bg-blue-600 px-4 py-2 text-white"
            >
                Create Request
            </button>
        </form>
    </div>
    );
}
