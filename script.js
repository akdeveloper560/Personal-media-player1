/**
 * NeonBeat - Online MP3 Streaming Engine with LocalStorage Playlists
 */

const AppState = {
    allSongsMap: new Map(),
    currentTrack: null,
    isPlaying: false,
    playlists: {}, // Format: { "PlaylistName": [songObjects] }
    selectedSongForMenu: null,
    currentView: 'search', // 'search' ya 'playlist'
    activePlaylistName: null
};

const DOM = {
    songsGrid: document.getElementById('songsGrid'),
    playPauseBtn: document.getElementById('playPauseBtn'),
    playerTitle: document.getElementById('playerTitle'),
    playerArtist: document.getElementById('playerArtist'),
    playerThumbnail: document.getElementById('playerThumbnail'),
    progressBar: document.getElementById('progressBar'),
    volumeBar: document.getElementById('volumeBar'),
    currentTimeLabel: document.getElementById('currentTime'),
    totalTimeLabel: document.getElementById('totalTime'),
    audioEngine: document.getElementById('main-audio-engine'),
    searchBtn: document.getElementById('searchBtn'),
    searchInput: document.getElementById('searchInput'),
    sectionTitle: document.getElementById('sectionTitle'),
    playlistList: document.getElementById('playlistList'),
    customDropdown: document.getElementById('customDropdown'),
    dropdownOptions: document.getElementById('dropdownOptions'),
    modalOverlay: document.getElementById('modalOverlay'),
    closeModalBtn: document.getElementById('closeModalBtn'),
    playlistInput: document.getElementById('playlistInput'),
    savePlaylistBtn: document.getElementById('savePlaylistBtn'),
    btnOnlineSearch: document.getElementById('btn-online-search')
};

// --- PLAYLIST LOCALSTORAGE UTILITIES ---
function loadPlaylistsFromStorage() {
    const stored = localStorage.getItem('neonbeat_playlists');
    if (stored) {
        AppState.playlists = JSON.parse(stored);
    } else {
        AppState.playlists = {};
    }
    renderSidebarPlaylists();
}

function savePlaylistsToStorage() {
    localStorage.setItem('neonbeat_playlists', JSON.stringify(AppState.playlists));
    renderSidebarPlaylists();
}

// --- RENDER FUNCTIONS ---
function renderSongsGrid(songs) {
    DOM.songsGrid.innerHTML = '';
    
    if(AppState.currentView === 'search') {
        AppState.allSongsMap.clear();
    }

    if(!songs || songs.length === 0) {
        DOM.songsGrid.innerHTML = `<p style="color: var(--text-muted); padding: 20px;">Yahan koi gaana nahi hai boss!</p>`;
        return;
    }

    songs.forEach(song => {
        AppState.allSongsMap.set(song.id, song);
        const card = document.createElement('div');
        card.className = 'song-card';
        card.innerHTML = `
            <div class="card-img"><img src="${song.thumbnail || 'https://via.placeholder.com/150'}" alt="thumbnail"></div>
            <div class="card-info">
                <h4>${song.title}</h4>
                <p>${song.artist}</p>
            </div>
        `;
        
        card.onclick = (e) => {
            playTrack(song.id);
        };

        card.oncontextmenu = (e) => {
            e.preventDefault();
            showContextMenu(e, song);
        };

        DOM.songsGrid.appendChild(card);
    });
}

function renderSidebarPlaylists() {
    DOM.playlistList.innerHTML = '';
    Object.keys(AppState.playlists).forEach(name => {
        const li = document.createElement('li');
        li.innerHTML = `<i class="fa-solid fa-music"></i> ${name}`;
        if(AppState.currentView === 'playlist' && AppState.activePlaylistName === name) {
            li.className = 'active';
        }
        li.onclick = () => {
            openPlaylistView(name);
        };
        DOM.playlistList.appendChild(li);
    });
}

function openPlaylistView(name) {
    AppState.currentView = 'playlist';
    AppState.activePlaylistName = name;
    if(DOM.btnOnlineSearch) DOM.btnOnlineSearch.classList.remove('active');
    renderSidebarPlaylists();
    
    DOM.sectionTitle.innerText = `Playlist: ${name}`;
    const playlistSongs = AppState.playlists[name] || [];
    renderSongsGrid(playlistSongs);
}

function showContextMenu(e, song) {
    AppState.selectedSongForMenu = song;
    DOM.customDropdown.style.top = `${e.pageY}px`;
    DOM.customDropdown.style.left = `${e.pageX}px`;
    DOM.customDropdown.classList.add('active');

    DOM.dropdownOptions.innerHTML = `<li id="ctx-create-pl"><b>+ Create New Playlist</b></li>`;
    
    Object.keys(AppState.playlists).forEach(plName => {
        DOM.dropdownOptions.innerHTML += `<li class="ctx-add-to-pl" data-name="${plName}">Add to "${plName}"</li>`;
    });
}

function hideContextMenu() {
    DOM.customDropdown.classList.remove('active');
}

// --- PLAYER ENGINE LOGIC ---
function playTrack(songId) {
    const track = AppState.allSongsMap.get(songId);
    if (!track) return;

    AppState.currentTrack = track;
    DOM.playerTitle.innerText = track.title;
    DOM.playerArtist.innerText = track.artist;
    DOM.playerThumbnail.src = track.thumbnail || 'https://via.placeholder.com/150';

    DOM.audioEngine.src = track.source;
    DOM.audioEngine.play()
        .then(() => {
            AppState.isPlaying = true;
            DOM.playPauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
        })
        .catch(err => {
            console.error("Playback error:", err);
            alert("Is track ka link expire ho gaya h, ek baar fir se search karke play kijiye!");
        });
}

function togglePlayPause() {
    if (!AppState.currentTrack) return;
    if (AppState.isPlaying) {
        DOM.audioEngine.pause();
        DOM.playPauseBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
    } else {
        DOM.audioEngine.play();
        DOM.playPauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
    }
    AppState.isPlaying = !AppState.isPlaying;
}

function formatTime(secs) {
    if (isNaN(secs)) return "0:00";
    const minutes = Math.floor(secs / 60);
    const seconds = Math.floor(secs % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
}

function initAudioEngineListeners() {
    DOM.audioEngine.ontimeupdate = () => {
        if(DOM.audioEngine.duration) {
            const pct = (DOM.audioEngine.currentTime / DOM.audioEngine.duration) * 100;
            DOM.progressBar.value = pct;
            DOM.currentTimeLabel.innerText = formatTime(DOM.audioEngine.currentTime);
        }
    };

    DOM.audioEngine.onloadedmetadata = () => {
        DOM.totalTimeLabel.innerText = formatTime(DOM.audioEngine.duration);
    };

    DOM.audioEngine.onended = () => {
        if (AppState.currentView === 'playlist' && AppState.activePlaylistName && AppState.currentTrack) {
            const currentPlaylistSongs = AppState.playlists[AppState.activePlaylistName] || [];
            const currentIndex = currentPlaylistSongs.findIndex(song => song.id === AppState.currentTrack.id);
            
            if (currentIndex !== -1 && currentIndex < currentPlaylistSongs.length - 1) {
                const nextSong = currentPlaylistSongs[currentIndex + 1];
                playTrack(nextSong.id);
                return;
            }
        }
        AppState.isPlaying = false;
        DOM.playPauseBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
        DOM.progressBar.value = 0;
        DOM.currentTimeLabel.innerText = "0:00";
    };

    DOM.progressBar.oninput = (e) => {
        if(DOM.audioEngine.duration) {
            DOM.audioEngine.currentTime = (e.target.value / 100) * DOM.audioEngine.duration;
        }
    };

    DOM.volumeBar.oninput = (e) => {
        DOM.audioEngine.volume = e.target.value / 100;
    };
}

async function handleSearch() {
    const query = DOM.searchInput.value.trim();
    if(!query) return;

    AppState.currentView = 'search';
    AppState.activePlaylistName = null;
    if(DOM.btnOnlineSearch) DOM.btnOnlineSearch.classList.add('active');
    renderSidebarPlaylists();

    DOM.sectionTitle.innerText = `Searching online for "${query}"...`;
    DOM.songsGrid.innerHTML = `<p style="color: var(--text-muted); padding: 20px;">Searching music...</p>`;
    
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const songs = await response.json();
        DOM.sectionTitle.innerText = `Online Results for: "${query}"`;
        renderSongsGrid(songs);
    } catch (err) {
        console.error("Search failed:", err);
        DOM.sectionTitle.innerText = "Error fetching results";
    }
}

// --- INITIALIZATION AND GLOBAL EVENTS ---
document.addEventListener('DOMContentLoaded', () => {
    if(DOM.playPauseBtn) DOM.playPauseBtn.onclick = togglePlayPause;
    if(DOM.searchBtn) DOM.searchBtn.onclick = handleSearch;
    if(DOM.searchInput) DOM.searchInput.onkeypress = (e) => { if(e.key === 'Enter') handleSearch(); };
    
    if(DOM.btnOnlineSearch) {
        DOM.btnOnlineSearch.onclick = () => {
            AppState.currentView = 'search';
            DOM.btnOnlineSearch.className = 'active';
            renderSidebarPlaylists();
            DOM.sectionTitle.innerText = "Search Anything Online";
            DOM.songsGrid.innerHTML = '';
        };
    }

    document.addEventListener('click', (e) => {
        if (DOM.customDropdown && !DOM.customDropdown.contains(e.target)) {
            hideContextMenu();
        }
    });

    if(DOM.customDropdown) {
        DOM.customDropdown.addEventListener('click', (e) => {
            const target = e.target;
            if (target.id === 'ctx-create-pl' || target.closest('#ctx-create-pl')) {
                hideContextMenu();
                DOM.modalOverlay.classList.add('active');
                DOM.playlistInput.focus();
            }
            if (target.classList.contains('ctx-add-to-pl')) {
                const plName = target.getAttribute('data-name');
                if (AppState.selectedSongForMenu && AppState.playlists[plName]) {
                    const exists = AppState.playlists[plName].some(s => s.id === AppState.selectedSongForMenu.id);
                    if (!exists) {
                        AppState.playlists[plName].push(AppState.selectedSongForMenu);
                        savePlaylistsToStorage();
                        alert(`"${AppState.selectedSongForMenu.title}" playlist "${plName}" mein add ho gaya!`);
                    } else {
                        alert("Yeh gaana pehle se playlist me h bhai!");
                    }
                }
                hideContextMenu();
            }
        });
    }

    if(DOM.closeModalBtn) DOM.closeModalBtn.onclick = () => DOM.modalOverlay.classList.remove('active');
    
    if(DOM.savePlaylistBtn) {
        DOM.savePlaylistBtn.onclick = () => {
            const plName = DOM.playlistInput.value.trim();
            if (plName) {
                if (!AppState.playlists[plName]) {
                    AppState.playlists[plName] = [];
                    if(AppState.selectedSongForMenu) {
                        AppState.playlists[plName].push(AppState.selectedSongForMenu);
                    }
                    savePlaylistsToStorage();
                    DOM.playlistInput.value = '';
                    DOM.modalOverlay.classList.remove('active');
                } else {
                    alert("Is naam ki playlist pehle se bani hui hai!");
                }
            }
        };
    }

    loadPlaylistsFromStorage();
    initAudioEngineListeners();
    if(DOM.volumeBar && DOM.audioEngine) DOM.audioEngine.volume = DOM.volumeBar.value / 100;
});
