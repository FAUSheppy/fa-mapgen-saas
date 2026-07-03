import { useState } from "react";
import { useFormStatus } from "react-dom";
import { useNavigate } from "react-router-dom";

import { createRequest } from "../api";
import { FILTERS } from "../constants/filters";

const VERSIONS = ["1.21.1"]

function isValidMapId(id: string): boolean {
    const PREFIX = "neroxis_map_generator_";

    if (!id.startsWith(PREFIX)) {
        return false;
    }

    const versionPattern = VERSIONS
        .map((v) => v.replace(/\./g, "\\."))
        .join("|");

    const regex = new RegExp(
        `^${PREFIX}(${versionPattern})_([a-z0-9]{13})_([a-z0-9]{16})$`
    );

    return regex.test(id);
}

export default function NewRequest() {



    const initialForm = Object.fromEntries(
        FILTERS.map((f) => [
            f.key,
            f.defaultValue ?? null,
        ])
    );
    const [form, setForm] = useState(initialForm);
    const [loading, setLoading] = useState(false);
    const [valid, setValid] = useState<Record<string, boolean>>({});

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

        setLoading(true);

        const payload = Object.fromEntries(
            Object.entries(form).map(([key, value]) => [
                key,
                value === "" ? null : value,
            ])
        );

        const response = await createRequest(payload);

        navigate(`/?request-id=${response.data.request_id}${
            "map_name" in valid ? "&single=1" : ""
        }`);
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
                                onChange={(e) => update(filter.key, e.target.value)}
                            >
                                <option value="">Select...</option>

                                {filter.options.map((option) => (
                                    <option key={option} value={option}>
                                        {option}
                                    </option>
                                ))}
                            </select>
                        ) : filter.type === "text" ? (
                            <input
                                disabled={disabled}
                                type="text"
                                className={`rounded border p-2 disabled:cursor-not-allowed disabled:bg-gray-100 ${
                                    valid[filter.key] ? "border-green-500" : "border-red-300"
                                }`}
                                value={form[filter.key] ?? ""}
                                onChange={(e) => {
                                    const value = e.target.value;
                                    update(filter.key, value);
                                    setValid((prev) => ({
                                        ...prev,
                                        [filter.key]: isValidMapId(value),
                                    }));
                                }}
                            />
                        ) : (
                            <>
                                <input
                                    disabled={disabled}
                                    type="range"
                                    min={filter.min}
                                    max={filter.max}
                                    step={filter.step}
                                    value={form[filter.key] ?? filter.min}
                                    onChange={(e) =>
                                        update(filter.key, Number(e.target.value))
                                    }
                                    className="w-full disabled:cursor-not-allowed"
                                />

                                <div className="text-sm text-gray-500">
                                    {form[filter.key] ?? filter.min}
                                </div>
                            </>
                        )}
                        </div>
                    );
                })}
            </div>

            <button
                type="submit"
                disabled={loading}
                className="rounded bg-blue-600 px-4 py-2 text-white disabled:bg-gray-400 disabled:text-gray-100"
            >
                {loading && (
                    <svg
                        className="h-4 w-4 animate-spin m-auto"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                    >
                        <circle
                            className="opacity-25"
                            cx="24"
                            cy="24"
                            r="20"
                            stroke="currentColor"
                            strokeWidth="4"
                        />
                        <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                        />
                    </svg>
                )}
                {loading ? "Waiting for server to accept the request.." : "Create Request"}
            </button>
        </form>
    </div>
    );
}
