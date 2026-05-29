import axios from "axios";

const baseURL = "/api-dev"
//const baseURL: "http://localhost:5000"
export const api = axios.create({
    baseURL: baseURL
});

export const searchMaps = (filters) =>
    api.post("/maps/search", filters);

export const createRequest = (payload) =>
    api.post("/request/new", payload);

export const mapImageUrl = (mapId) =>
    `${baseURL}/maps/${mapId}/image`;
