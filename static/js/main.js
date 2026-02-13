// Configuration
const BACKEND_URL = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:5000';

document.addEventListener('DOMContentLoaded', function() {
    initializeLanguageFilter();
    initializeSearch();
    initializeNotifications();
    checkBackendStatus();
    setupEventListeners();
});

/**
 * Initialization of language filtering
 */
function initializeLanguageFilter() {
    const languageButtons = document.querySelectorAll('.language-btn');
    const articleCards = document.querySelectorAll('.article-card');
    const languageFilter = document.getElementById('languageFilter');
    
    if (languageFilter) {
        languageFilter.addEventListener('change', function() {
            const selectedLanguage = this.value;
            
            articleCards.forEach(card => {
                const cardLanguage = card.dataset.language;
                
                if (selectedLanguage === 'all' || cardLanguage === selectedLanguage) {
                    card.style.display = 'block';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 10);
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
            
            // Update URL without reload
            const url = new URL(window.location);
            if (selectedLanguage === 'all') {
                url.searchParams.delete('language');
            } else {
                url.searchParams.set('language', selectedLanguage);
            }
            window.history.pushState({}, '', url);
        });
    }
    
    // Language buttons (alternative UI)
    languageButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            languageButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Get selected language
            const selectedLanguage = this.dataset.language;
            
            // Filter articles
            articleCards.forEach(card => {
                const cardLanguage = card.dataset.language;
                
                if (selectedLanguage === 'all' || cardLanguage === selectedLanguage) {
                    card.style.display = 'block';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 10);
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
            
            // Update count
            updateArticleCount(selectedLanguage);
        });
    });
}

/**
 * Update article count display
 */
function updateArticleCount(language) {
    const articleCards = document.querySelectorAll('.article-card');
    let visibleCount = 0;
    
    articleCards.forEach(card => {
        const cardLanguage = card.dataset.language;
        if (language === 'all' || cardLanguage === language) {
            if (card.style.display !== 'none') {
                visibleCount++;
            }
        }
    });
    
    const countElement = document.getElementById('articleCount');
    if (countElement) {
        countElement.textContent = `${visibleCount} articles`;
    }
}

/**
 * Initialize search functionality
 */
function initializeSearch() {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    
    if (searchForm) {
        searchForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const query = searchInput.value.trim();
            if (!query) return;
            
            try {
                const response = await fetch(`${BACKEND_URL}/api/v1/articles/?search=${encodeURIComponent(query)}&limit=50`);
                const data = await response.json();
                
                if (searchResults) {
                    if (data.articles && data.articles.length > 0) {
                        let html = `<h3>Search Results for "${query}" (${data.articles.length})</h3>`;
                        
                        data.articles.forEach(article => {
                            const languageBadge = article.language === 'en' 
                                ? '<span class="language-en">EN</span>' 
                                : '<span class="language-rw">RW</span>';
                            
                            html += `
                                <div class="search-result-item">
                                    <div class="search-result-content">
                                        <h4>
                                            <a href="${FRONTEND_URL}/article/${article.id}">
                                                ${article.title}
                                            </a>
                                        </h4>
                                        <p>${article.description || ''}</p>
                                        <div class="search-result-meta">
                                            ${languageBadge}
                                            <span class="source">${article.source}</span>
                                            <span class="category">${article.category_name}</span>
                                            <span class="time">${formatTimeAgo(article.published_at)}</span>
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                        
                        searchResults.innerHTML = html;
                        searchResults.style.display = 'block';
                    } else {
                        searchResults.innerHTML = `
                            <div class="no-results">
                                <i class="fas fa-search"></i>
                                <h3>No results found for "${query}"</h3>
                                <p>Try different keywords or browse by category.</p>
                            </div>
                        `;
                        searchResults.style.display = 'block';
                    }
                }
            } catch (error) {
                console.error('Search error:', error);
                showNotification('Error performing search. Please try again.', 'error');
            }
        });
    }
}

/**
 * Check backend status
 */
async function checkBackendStatus() {
    const statusElement = document.getElementById('backendStatus');
    
    if (statusElement) {
        try {
            const response = await fetch(`${BACKEND_URL}/api/v1/health/status`);
            const data = await response.json();
            
            statusElement.innerHTML = `
                <i class="fas fa-server"></i> Backend: Online
                <span class="status-detail">${data.message}</span>
            `;
            statusElement.className = 'status-indicator online';
            
            // Update stats if available
            updateStats();
            
        } catch (error) {
            statusElement.innerHTML = `
                <i class="fas fa-server"></i> Backend: Offline
                <span class="status-detail">Cannot connect to server</span>
            `;
            statusElement.className = 'status-indicator offline';
        }
    }
}

/**
 * Update statistics
 */
async function updateStats() {
    try {
        const response = await fetch(`${BACKEND_URL}/api/v1/fetcher/stats`);
        const data = await response.json();
        
        // Update stats display
        const statsElements = {
            'totalArticles': document.getElementById('totalArticles'),
            'englishArticles': document.getElementById('englishArticles'),
            'kinyarwandaArticles': document.getElementById('kinyarwandaArticles')
        };
        
        if (statsElements.totalArticles) {
            statsElements.totalArticles.textContent = data.total_articles;
        }
        if (statsElements.englishArticles) {
            statsElements.englishArticles.textContent = data.english_articles;
        }
        if (statsElements.kinyarwandaArticles) {
            statsElements.kinyarwandaArticles.textContent = data.kinyarwanda_articles;
        }
        
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Fetch News Button
    const fetchNewsBtn = document.getElementById('fetchNewsBtn');
    if (fetchNewsBtn) {
        fetchNewsBtn.addEventListener('click', async function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Fetching...';
            this.disabled = true;
            
            try {
                const response = await fetch(`${BACKEND_URL}/api/v1/fetcher/fetch-now`, {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                showNotification('Started fetching latest news! This may take a moment.', 'success');
                
                // Update button to show progress
                let countdown = 30;
                const interval = setInterval(() => {
                    this.innerHTML = `<i class="fas fa-sync-alt"></i> Refreshing in ${countdown}s`;
                    countdown--;
                    
                    if (countdown < 0) {
                        clearInterval(interval);
                        window.location.reload();
                    }
                }, 1000);
                
            } catch (error) {
                console.error('Fetch error:', error);
                this.innerHTML = originalText;
                this.disabled = false;
                showNotification('Error starting news fetch. Please try again.', 'error');
            }
        });
    }
    
    // Load More Button
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', async function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            this.disabled = true;
            
            try {
                // Get current page from URL or default to 2
                const urlParams = new URLSearchParams(window.location.search);
                let currentPage = parseInt(urlParams.get('page')) || 1;
                currentPage++;
                
                // Load more articles
                const response = await fetch(`${FRONTEND_URL}/api/articles?page=${currentPage}`);
                const data = await response.json();
                
                if (data.articles && data.articles.length > 0) {
                    // Add new articles to the grid
                    const articlesGrid = document.querySelector('.articles-grid');
                    
                    data.articles.forEach(article => {
                        const articleElement = createArticleCard(article);
                        articlesGrid.appendChild(articleElement);
                    });
                    
                    // Update URL
                    urlParams.set('page', currentPage);
                    window.history.pushState({}, '', `?${urlParams.toString()}`);
                    
                    // Hide button if no more articles
                    if (data.articles.length < 20) {
                        this.style.display = 'none';
                    }
                } else {
                    this.style.display = 'none';
                }
                
                this.innerHTML = originalText;
                this.disabled = false;
                
            } catch (error) {
                console.error('Load more error:', error);
                this.innerHTML = originalText;
                this.disabled = false;
                showNotification('Error loading more articles.', 'error');
            }
        });
    }
}

/**
 * Create article card element
 */
function createArticleCard(article) {
    const languageBadge = article.language === 'en' 
        ? '<span class="language-en">English</span>' 
        : '<span class="language-rw">Kinyarwanda</span>';
    
    const card = document.createElement('div');
    card.className = 'article-card';
    card.dataset.language = article.language;
    card.innerHTML = `
        <div class="language-indicator ${article.language === 'en' ? 'language-en-indicator' : 'language-rw-indicator'}">
            ${article.language.toUpperCase()}
        </div>
        
        <img src="${article.url_to_image || 'https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=60'}" 
             alt="${article.title}" 
             class="article-image">
        
        <div class="article-content">
            <div class="article-meta">
                <span class="article-category">${article.category_name}</span>
                <span class="article-source">${article.source}</span>
                <span class="article-time">${formatTimeAgo(article.published_at)}</span>
            </div>
            
            <h3 class="article-title">
                <a href="${FRONTEND_URL}/article/${article.id}">
                    ${article.title}
                </a>
            </h3>
            
            <p class="article-description">
                ${article.description ? article.description.substring(0, 150) + '...' : ''}
            </p>
            
            <div class="article-footer">
                ${languageBadge}
                <a href="${FRONTEND_URL}/article/${article.id}" class="read-more">
                    Read More <i class="fas fa-arrow-right"></i>
                </a>
            </div>
        </div>
    `;
    
    return card;
}

/**
 * Format time ago
 */
function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'just now';
    
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;
    
    return date.toLocaleDateString();
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Initialize notification system
 */
function initializeNotifications() {
    // Add CSS for notifications if not present
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                display: flex;
                align-items: center;
                justify-content: space-between;
                min-width: 300px;
                max-width: 400px;
                z-index: 10000;
                animation: slideIn 0.3s ease;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            .notification.success {
                background: linear-gradient(135deg, #4CAF50, #45a049);
            }
            
            .notification.error {
                background: linear-gradient(135deg, #f44336, #d32f2f);
            }
            
            .notification.info {
                background: linear-gradient(135deg, #2196F3, #1976D2);
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .notification-close {
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                font-size: 1.2rem;
                padding: 0;
                margin-left: 15px;
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Make functions available globally
window.showNotification = showNotification;