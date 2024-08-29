console.log('app.js loaded');

const API_KEY = 'eae1697ca09c4fdaafece7974d60b33e'; // Make sure this is your actual API key
const BASE_URL = 'https://api.football-data.org/v4';

let selectedLeague = 'PL'; // Default to Premier League

async function fetchData(endpoint) {
    const corsProxy = 'https://cors-anywhere.herokuapp.com/';
    try {
        console.log(`Fetching data from: ${corsProxy}${BASE_URL}${endpoint}`);
        const response = await fetch(`${corsProxy}${BASE_URL}${endpoint}`, {
            headers: { 
                'X-Auth-Token': API_KEY,
                'Origin': 'http://localhost:8080'
            }
        });
        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Received data:', data);
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error;
    }
}

async function displayLatestResults() {
    try {
        console.log('Displaying latest results...');
        // Fetch more matches to ensure we have the most recent day
        const data = await fetchData(`/competitions/${selectedLeague}/matches?status=FINISHED&limit=20`);
        const resultsContainer = document.getElementById('latest-results');
        console.log('Latest Results:', data);
        
        if (data.matches && data.matches.length > 0) {
            // Sort matches by date, most recent first
            const sortedMatches = data.matches.sort((a, b) => new Date(b.utcDate) - new Date(a.utcDate));
            
            // Get the date of the most recent match
            const mostRecentDate = new Date(sortedMatches[0].utcDate).toDateString();
            
            // Filter matches from the most recent day
            const recentMatches = sortedMatches.filter(match => 
                new Date(match.utcDate).toDateString() === mostRecentDate
            );

            const matchesHtml = recentMatches.map(match => `
                <div class="bg-dark-accent rounded-lg p-4 mb-4 flex justify-between items-center">
                    <div class="flex items-center">
                        <span class="font-semibold">${match.homeTeam.name}</span>
                    </div>
                    <div class="text-2xl font-bold text-light-text">
                        ${match.score.fullTime.home ?? '-'} - ${match.score.fullTime.away ?? '-'}
                    </div>
                    <div class="flex items-center">
                        <span class="font-semibold">${match.awayTeam.name}</span>
                    </div>
                </div>
            `).join('');
            
            resultsContainer.innerHTML = `
                <h3 class="text-xl font-semibold mb-4">Results for ${mostRecentDate}</h3>
                ${matchesHtml}
            `;
        } else {
            resultsContainer.innerHTML = '<p class="text-center">No recent matches found.</p>';
        }
    } catch (error) {
        console.error('Error in displayLatestResults:', error);
        document.getElementById('latest-results').innerHTML = `Error loading results: ${error.message}`;
    }
}

async function displayLeagueStandings() {
    try {
        console.log('Displaying league standings...');
        const data = await fetchData(`/competitions/${selectedLeague}/standings`);
        const standingsContainer = document.getElementById('league-standings');
        console.log('League Standings:', data);
        
        if (data.standings && data.standings[0].table) {
            const standingsHtml = `
                <table class="w-full">
                    <thead>
                        <tr class="text-left">
                            <th class="py-2">Position</th>
                            <th>Team</th>
                            <th>Played</th>
                            <th>Won</th>
                            <th>Drawn</th>
                            <th>Lost</th>
                            <th>Points</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.standings[0].table.map(team => `
                            <tr class="border-t border-dark-accent">
                                <td class="py-2">${team.position}</td>
                                <td>${team.team.name}</td>
                                <td>${team.playedGames}</td>
                                <td>${team.won}</td>
                                <td>${team.draw}</td>
                                <td>${team.lost}</td>
                                <td>${team.points}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            standingsContainer.innerHTML = standingsHtml;
        } else {
            standingsContainer.innerHTML = '<p class="text-center">No standings data available.</p>';
        }
    } catch (error) {
        console.error('Error in displayLeagueStandings:', error);
        document.getElementById('league-standings').innerHTML = `Error loading standings: ${error.message}`;
    }
}

async function displayUpcomingMatches() {
    try {
        console.log('Displaying upcoming matches...');
        const data = await fetchData(`/competitions/${selectedLeague}/matches?status=SCHEDULED&limit=5`);
        const upcomingContainer = document.getElementById('upcoming-matches');
        console.log('Upcoming Matches:', data);
        
        if (data.matches && data.matches.length > 0) {
            const matchesHtml = data.matches.slice(0, 5).map(match => `
                <div class="bg-dark-accent rounded-lg p-4 mb-4">
                    <div class="flex justify-between items-center">
                        <span class="font-semibold">${match.homeTeam.name}</span>
                        <span class="text-light-text">vs</span>
                        <span class="font-semibold">${match.awayTeam.name}</span>
                    </div>
                    <div class="text-center mt-2 text-sm">
                        ${new Date(match.utcDate).toLocaleString()}
                    </div>
                </div>
            `).join('');
            upcomingContainer.innerHTML = matchesHtml;
        } else {
            upcomingContainer.innerHTML = '<p class="text-center">No upcoming matches found.</p>';
        }
    } catch (error) {
        console.error('Error in displayUpcomingMatches:', error);
        document.getElementById('upcoming-matches').innerHTML = `Error loading upcoming matches: ${error.message}`;
    }
}

async function updateData() {
    displayLatestResults();
    displayLeagueStandings();
    displayUpcomingMatches();
}

document.addEventListener('DOMContentLoaded', () => {
    const leagueSelect = document.getElementById('league-select');
    leagueSelect.addEventListener('change', (event) => {
        selectedLeague = event.target.value;
        updateData();
    });

    updateData(); // Initial data load

    // Update data every 5 minutes (300000 milliseconds)
    setInterval(updateData, 300000);
    
        const refreshButton = document.getElementById('refresh-button');
        refreshButton.addEventListener('click', updateData);
});