
import React, { useState } from 'react';
import { LinearProgress } from '@mui/material';

const FileUploadComponent = () => {
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState('');
    const [isLoading, setIsLoading] = useState(false); // Track loading state
    const [searchString, setSearchString] = useState('');
    const [earliestTime, setEarliestTime] = useState('');
    const [latestTime, setLatestTime] = useState('');
    const [results, setResults] = useState([]);

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            setStatus('Please select a .tgz file to upload.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file); // 'file' is the key for the file in the backend

        setIsLoading(true); // Show the progress bar

        try {
            const response = await fetch('http://127.0.0.1:8000/upload/process-tgz/', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                setStatus(`Files processed successfully: ${data.files_processed}`);
                setResults(data.results || []);
            } else {
                setStatus(`Error: ${data.error || 'An error occurred while processing the file.'}`);
            }
        } catch (error) {
            setStatus(`Error: ${error.message}`);
        } finally {
            setIsLoading(false); // Hide the progress bar
        }
    };

    const handleSearch = async () => {
                const params = new URLSearchParams();
                if (searchString) params.append('searchstring', searchString);
                if (earliestTime) params.append('EarliestTime', earliestTime);
                if (latestTime) params.append('LatestTime', latestTime);
        
                try {
                    const response = await fetch(`http://127.0.0.1:8000/upload/search-logs/?${params.toString()}`);
                    const data = await response.json();
        
                    if (response.ok) {
                        if (data.results && data.results.length > 0) {
                            setResults(data.results);
                            setStatus('Search completed successfully.');
                        } else {
                            setStatus('No results found.');
                            setResults([]);
                        }
                    } else {
                        // Handle specific error messages from backend response
                        if (data.status === "error" && data.message) {
                            let errorMessages = '';
                            // Loop through the message object to concatenate error messages
                            for (let key in data.message) {
                                if (data.message.hasOwnProperty(key)) {
                                    errorMessages += `${key}: ${data.message[key].join(', ')}\n`;
                                }
                            }
                            // Set the status and error messages
                            setStatus(`Error: ${errorMessages || 'An error occurred during the search.'}`);
                        } else {
                            // Fallback error handling if the expected structure is not found
                            setStatus(`Error: ${data.error || data.message || 'An error occurred during the search.'}`);
                        }
                        setResults([]);
                    }
                    
                } catch (error) {
                    setStatus(`Error: ${error.message}`);
                    setResults([]);
                }
            };

    return (
        <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px', borderRadius: '8px', boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)', backgroundColor: '#f9f9f9' }}>
            <h3 style={{ textAlign: 'center', marginBottom: '20px' }}>Upload .tgz File</h3>

            {/* File Upload */}
            <div style={{ marginBottom: '20px' }}>
                <input
                    type="file"
                    onChange={handleFileChange}
                    accept=".tgz"
                    style={{ display: 'block', marginBottom: '10px' }}
                />
                <button
                    onClick={handleUpload}
                    style={{
                        padding: '10px 15px',
                        backgroundColor: '#007BFF',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer',
                    }}
                >
                    Upload
                </button>
            </div>

            {/* Progress Bar */}
            {isLoading && <LinearProgress style={{ marginBottom: '20px' }} />}

            {/* Status Message */}
            {status && (
                <div
                    style={{
                        backgroundColor: status.includes('Error') ? '#ff4d4d' : '#4CAF50',
                        color: '#fff',
                        padding: '10px',
                        borderRadius: '5px',
                        marginBottom: '20px',
                        textAlign: 'center',
                    }}
                >
                    {status}
                </div>
            )}

            {/* Search Fields */}
            <div style={{ marginBottom: '20px' }}>
                <input
                    type="text"
                    placeholder="Search (e.g., account-id=264684)"
                    value={searchString}
                    onChange={(e) => setSearchString(e.target.value)}
                    style={{
                        width: '100%',
                        padding: '10px',
                        marginBottom: '10px',
                        borderRadius: '5px',
                        border: '1px solid #ccc',
                    }}
                />
                <input
                    type="number"
                    placeholder="Earliest Time (Epoch)"
                    value={earliestTime}
                    onChange={(e) => setEarliestTime(e.target.value)}
                    style={{
                        width: '100%',
                        padding: '10px',
                        marginBottom: '10px',
                        borderRadius: '5px',
                        border: '1px solid #ccc',
                    }}
                />
                <input
                    type="number"
                    placeholder="Latest Time (Epoch)"
                    value={latestTime}
                    onChange={(e) => setLatestTime(e.target.value)}
                    style={{
                        width: '100%',
                        padding: '10px',
                        marginBottom: '10px',
                        borderRadius: '5px',
                        border: '1px solid #ccc',
                    }}
                />
                <button
                    onClick={handleSearch}
                    style={{
                        padding: '10px 15px',
                        backgroundColor: '#28a745',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer',
                    }}
                >
                    Search Logs
                </button>
            </div>

            {/* Search Results */}
            {results.length > 0 && (
                <div>
                    <h4>Search Results:</h4>
                    <ul style={{ paddingLeft: '20px' }}>
                        {results.map((result, index) => (
                            <li key={index} style={{ marginBottom: '10px' }}>
                                <pre>{JSON.stringify(result, null, 2)}</pre>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default FileUploadComponent;
