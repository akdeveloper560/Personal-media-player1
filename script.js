// 100% PERMANENT: Saavn Database Engine (Kabhi Block Nahi Hoga)
async function handleSearch() {
    if (!DOM.searchInput) return;
    const query = DOM.searchInput.value.trim();
    if (!query) return;

    AppState.currentView = 'search';
    AppState.activePlaylistName = null;
    if (DOM.btnOnlineSearch) DOM.btnOnlineSearch.classList.add('active');
    renderSidebarPlaylists();

    if (DOM.sectionTitle) DOM.sectionTitle.innerText = `Searching "${query}" on High-Speed Server...`;
    
    try {
        // Public Free Music API for JioSaavn Database (No CORS, No Blockers)
        const response = await fetch(`https://saavn.dev/api/search/songs?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data && data.success && data.data && data.data.results.length > 0) {
            let songs = data.data.results.map(track => {
                // High quality thumbnail selection
                const thumb = track.image && track.image.length > 0 
                    ? track.image[track.image.length - 1].url 
                    : 'https://via.placeholder.com/150';

                // Best quality audio url extraction
                const audio = track.downloadUrl && track.downloadUrl.length > 0
                    ? track.downloadUrl[track.downloadUrl.length - 1].url
                    : '';

                return {
                    id: track.id,
                    title: track.name,
                    artist: track.artists.primary && track.artists.primary.length > 0 ? track.artists.primary[0].name : 'Unknown Artist',
                    thumbnail: thumb,
                    audioUrl: audio // Direct MP3 stream from CDN
                };
            });
            
            if (DOM.sectionTitle) DOM.sectionTitle.innerText = `Results for: "${query}"`;
            renderSongsGrid(songs);
        } else {
            if (DOM.sectionTitle) DOM.sectionTitle.innerText = "Gaana nahi mila. Kuch aur search karein!";
        }
    } catch (err) {
        console.error("Search Fail:", err);
        if (DOM.sectionTitle) DOM.sectionTitle.innerText = "Server busy hai, ek baar aur click karo!";
    }
}

// Direct CDN Playback (No Buffering, No YouTube Limits)
async function playTrack(songId) {
    const track = AppState.allSongsMap.get(songId);
    if (!track || !DOM.audioEngine || !track.audioUrl) {
        if(DOM.sectionTitle) DOM.sectionTitle.innerText = "Error: Stream link not available!";
        return;
    }

    AppState.currentTrack = track;
    if (DOM.playerTitle) DOM.playerTitle.innerText = track.title;
    if (DOM.playerArtist) DOM.playerArtist.innerText = track.artist;
    if (DOM.playerThumbnail) DOM.playerThumbnail.src = track.thumbnail;
    if (DOM.sectionTitle) DOM.sectionTitle.innerText = `Playing: ${track.title}`;

    DOM.audioEngine.src = track.audioUrl;
    DOM.audioEngine.play()
        .then(() => {
            AppState.isPlaying = true;
            if (DOM.playPauseBtn) DOM.playPauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
        })
        .catch(err => {
            console.error("Playback failed:", err);
            if (DOM.sectionTitle) DOM.sectionTitle.innerText = "Click again to play!";
        });
}
