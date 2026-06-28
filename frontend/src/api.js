import axios from "axios";

const baseURL = "/api-dev"
//const baseURL: "http://localhost:5000"
export const api = axios.create({
    baseURL: baseURL
});

export const voteMap = async (mapId, vote) => {
    try {
        return await api.post("/vote", {
            mapid: mapId,
            vote,
        });
    } catch (error) {
        if (error.response?.status === 401) {
            window.location.href = "/oauth2/start";
            return;
        }

        throw error;
    }
};

export const voteMap = (mapId, vote) =>
    api.post("/vote", {
        mapid: mapId,
        vote,
    });

export const createRequest = (payload) =>
    api.post("/request/new", payload);

export const queueSize = (payload) =>
    api.get("/queue");

export const mapImageUrl = (mapId) =>
    `${baseURL}/maps/${mapId}/image`;
