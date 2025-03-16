// Playlist.js
import React, { useState, useEffect, useRef } from "react";
import PlaylistCard from "./PlaylistCard";

function Playlist() {
    const [playlists, setPlaylists] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [query, setQuery] = useState('java');
    const [pageToken, setPageToken] = useState(null); // Track page token for pagination
    const [nextPageToken, setNextPageToken] = useState(null);
    const [sortBy, setSortBy] = useState('relevance'); // Default sort
    const [language, setLanguage] = useState('en'); // Default language
    const authToken = localStorage.getItem('authToken');
    const searchInputRef = useRef();

    if (!authToken) {
        return (
            <div className="bg-[#F7F7F7] text-[#1F2833] font-bold text-5xl px-20 py-28 w-full h-[100vh] flex justify-center items-center">
                Unauthorized. Log in first to access this page...
            </div>
        );
    }

    const fetchPlaylists = () => {
        setLoading(true);
        fetch(`http://localhost:8000/api/learn/${query}/`, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${authToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                pageToken: pageToken,
                sortBy: sortBy,
                language: language,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (!data) {
                setError("No playlists found.");
                setPlaylists([]);
            } else {
                setPlaylists(data);
                setNextPageToken(data.nextPageToken || null); // Set the nextPageToken if it exists
                setError(null);
            }
            setLoading(false);
        })
        .catch(err => {
            setError("Failed to fetch learning resources");
            console.log(err)
            setLoading(false);
        });
    };

    useEffect(() => {
        fetchPlaylists();
    }, [query, pageToken, sortBy, language]);

    const handleSearch = () => {
        const newQuery = searchInputRef.current.value.trim();
        if (newQuery && newQuery !== query) {
            setQuery(newQuery);
            setPageToken(null); // Reset to first page
        }
    };

    const handleNextPage = () => {
        if (nextPageToken) {
            setPageToken(nextPageToken);
        }
    };

    if (loading) {
        return (
            <div className="bg-[#F7F7F7] text-[#1F2833] font-bold text-5xl px-20 py-28 w-full h-[100vh] flex justify-center items-center">
                Loading resources...
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-[#F7F7F7] text-red-500 font-bold text-5xl px-20 py-28 w-full h-[100vh] flex justify-center items-center">
                <span className="text-3xl">{error}</span>
            </div>
        );
    }

    return (
        <div className="bg-[#F7F7F7] px-20 pt-28 pb-6 w-full min-h-screen">
            <h2 className="text-3xl font-bold text-[#1F2833] mb-4">Discover Free Resources</h2>

            {/* Search and Filter Options */}
            <div className="mb-6 flex items-center space-x-4">
                <input
                    type="text"
                    ref={searchInputRef}
                    placeholder="Search for playlists"
                    className="border border-gray-400 p-3 rounded-l-md w-full text-[#1F2833]"
                />
                <button
                    onClick={handleSearch}
                    className="bg-[#1F2833] text-white px-5 py-3 rounded-md font-semibold"
                >
                    Search
                </button>

                {/* Sort By Dropdown */}
                <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="border border-gray-400 p-3 rounded-md text-[#1F2833] bg-white"
                >
                    <option value="relevance">Sort by Relevance</option>
                    <option value="date">Sort by Date</option>
                    <option value="viewCount">Sort by View Count</option>
                    <option value="rating">Sort by Rating</option>
                </select>

                {/* Language Dropdown */}
                <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="border border-gray-400 p-3 rounded-md text-[#1F2833] bg-white"
                >
                    <option value="en">English</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                    {/* Add more languages as needed */}
                </select>
            </div>

            {/* Info message */}
            <p className="text-lg font-medium text-gray-600 mb-6">
                {query === 'java'
                    ? "Showing AI-recommended courses for 'java'."
                    : `Showing search results for "${query}".`}
            </p>

            {/* Playlist Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8 w-full">
                {playlists.map((playlist, index) => (
                    <PlaylistCard
                        key={index}
                        title={playlist.snippet.title}
                        thumbnail={playlist.snippet.thumbnails.high.url}
                        channelTitle={playlist.snippet.channelTitle}
                        publishedAt={playlist.snippet.publishedAt}
                        link={`https://www.youtube.com/playlist?list=${playlist.id.playlistId}`}
                    />
                ))}
            </div>

            {/* Next Page Button */}
            {nextPageToken && (
                <div className="flex justify-center mt-8">
                    <button
                        onClick={handleNextPage}
                        className="bg-[#1F2833] text-white px-6 py-3 rounded-md font-semibold"
                    >
                        Next Page
                    </button>
                </div>
            )}
        </div>
    );
}

export default Playlist;
