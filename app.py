"""
Globe News Frontend - Complete Version
Connected to Backend v6.1 with Full Content Extraction
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
from datetime import datetime
import html
import re
import os

app = Flask(__name__)

# Backend API configuration
BACKEND_URL = os.environ.get('BACKEND_URL', 'https://p01--backend-api--5pt6gkpwq49b.code.run')
API_VERSION = "v1"

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%b %d, %Y %H:%M'):
    """Format datetime string."""
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return dt.strftime(format)
    except:
        return value

@app.template_filter('truncate')
def truncate(text, length=200):
    """Truncate text to specified length."""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length] + "..."

@app.template_filter('time_ago')
def time_ago(value):
    """Convert datetime to relative time."""
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"
    except:
        return value

@app.template_filter('safe_html')
def safe_html(text):
    """Safely render HTML content."""
    if not text:
        return ""
    # Allow safe HTML tags for previews
    allowed_tags = ['div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                   'ul', 'ol', 'li', 'strong', 'em', 'b', 'i', 'u', 'a', 
                   'img', 'br', 'hr', 'table', 'tr', 'td', 'th', 'style']
    
    # Remove script tags and other dangerous elements
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    return text

@app.template_filter('category_color')
def category_color(category):
    """Get color for category."""
    colors = {
        'World': '#3b82f6',
        'Technology': '#8b5cf6',
        'Business': '#10b981',
        'Science': '#06b6d4',
        'Health': '#ec4899',
        'Sports': '#f97316',
        'Entertainment': '#ef4444',
        'Politics': '#6b7280',
        'General': '#6366f1'
    }
    return colors.get(category, '#6366f1')

@app.template_filter('category_icon')
def category_icon(category):
    """Get icon for category."""
    icons = {
        'World': '🌍',
        'Technology': '💻',
        'Business': '📈',
        'Science': '🔬',
        'Health': '🏥',
        'Sports': '⚽',
        'Entertainment': '🎬',
        'Politics': '🏛️',
        'General': '📰'
    }
    return icons.get(category, '📄')

# ==================== API HELPER FUNCTIONS ====================

def fetch_articles(params=None):
    """Fetch articles from backend API."""
    try:
        url = f"{BACKEND_URL}/api/{API_VERSION}/articles"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching articles: {e}")
        return {"articles": [], "total": 0}

def fetch_article(article_id):
    """Fetch single article from backend API."""
    try:
        url = f"{BACKEND_URL}/api/{API_VERSION}/articles/{article_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article {article_id}: {e}")
        return None

def fetch_categories():
    """Fetch categories from backend API."""
    try:
        url = f"{BACKEND_URL}/api/{API_VERSION}/categories"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching categories: {e}")
        return []

def fetch_breaking_articles():
    """Fetch breaking news articles."""
    try:
        url = f"{BACKEND_URL}/api/{API_VERSION}/articles/breaking/"
        response = requests.get(url, params={"limit": 10}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching breaking articles: {e}")
        return {"articles": []}

def fetch_preview(article_id):
    """Fetch content preview for article."""
    try:
        url = f"{BACKEND_URL}/api/{API_VERSION}/preview/articles/{article_id}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching preview for article {article_id}: {e}")
        return None

def generate_preview(article_id):
    """Generate new preview for article."""
    try:
        url = f"{BACKEND_URL}/api/{API_VERSION}/preview/articles/{article_id}/generate"
        response = requests.post(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error generating preview for article {article_id}: {e}")
        return None

def trigger_fetch():
    """Trigger manual news fetch."""
    try:
        url = f"{BACKEND_URL}/api/{API_VERSION}/fetcher/fetch-now"
        response = requests.post(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error triggering fetch: {e}")
        return {"message": "Error triggering fetch"}

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Homepage - Latest news."""
    # Get language preference
    language = request.args.get('language', 'all')
    
    # Fetch latest articles
    params = {
        'limit': 24,
        'language': language
    }
    
    articles_data = fetch_articles(params)
    articles = articles_data.get('articles', [])
    
    # Fetch breaking news
    breaking_data = fetch_breaking_articles()
    breaking_articles = breaking_data.get('articles', [])[:5]
    
    # Fetch categories for sidebar
    categories = fetch_categories()
    
    # Calculate total articles per category
    for category in categories:
        cat_params = {'category': category['name'], 'limit': 1}
        cat_data = fetch_articles(cat_params)
        category['article_count'] = cat_data.get('total', 0)
    
    return render_template(
        'index.html',
        articles=articles,
        breaking_articles=breaking_articles,
        categories=categories,
        language=language,
        total_articles=articles_data.get('total', 0)
    )

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    """Article detail page with preview."""
    # Fetch article
    article = fetch_article(article_id)
    
    if not article:
        return render_template('error.html', 
                            message="Article not found",
                            error_code=404), 404
    
    # Fetch preview
    preview_data = fetch_preview(article_id)
    
    # Check if article has full content
    has_full_content = article.get('has_full_content', False)
    content_length = article.get('content_length', 0)
    
    # Check if preview needs regeneration
    needs_regeneration = False
    if preview_data and not preview_data.get('has_preview', False):
        needs_regeneration = True
    elif not preview_data:
        needs_regeneration = True
    
    # If preview exists, use it
    preview_html = None
    if preview_data and preview_data.get('has_preview'):
        preview_html = preview_data.get('preview')
    elif article.get('preview_content'):
        preview_html = article.get('preview_content')
    
    # Show content warning if no full content
    content_warning = None
    if not has_full_content and content_length < 500:
        content_warning = "⚠️ Limited content available - only RSS summary was fetched"
    
    return render_template(
        'article_detail.html',
        article=article,
        preview_html=preview_html,
        needs_regeneration=needs_regeneration,
        has_full_content=has_full_content,
        content_warning=content_warning,
        content_length=content_length
    )

@app.route('/article/<int:article_id>/regenerate-preview')
def regenerate_preview(article_id):
    """Regenerate preview for article."""
    result = generate_preview(article_id)
    
    if result and result.get('success'):
        return redirect(url_for('article_detail', article_id=article_id))
    else:
        article = fetch_article(article_id)
        return render_template(
            'article_detail.html',
            article=article,
            preview_html=None,
            error_message="Failed to regenerate preview. Please try again.",
            needs_regeneration=True
        )

@app.route('/categories')
def categories():
    """Categories listing page."""
    categories_list = fetch_categories()
    
    # Get article count for each category
    for category in categories_list:
        params = {'category': category['name'], 'limit': 1}
        data = fetch_articles(params)
        category['article_count'] = data.get('total', 0)
    
    return render_template('category.html', 
                         categories=categories_list)

@app.route('/category/<category_name>')
def category_detail(category_name):
    """Individual category page."""
    # Get language preference
    language = request.args.get('language', 'all')
    page = request.args.get('page', 1, type=int)
    limit = 20
    skip = (page - 1) * limit
    
    # Fetch articles for this category
    params = {
        'category': category_name,
        'language': language,
        'limit': limit,
        'skip': skip
    }
    
    articles_data = fetch_articles(params)
    articles = articles_data.get('articles', [])
    total = articles_data.get('total', 0)
    
    # Calculate pagination
    total_pages = (total + limit - 1) // limit
    
    # Get category info
    categories_list = fetch_categories()
    current_category = next((c for c in categories_list if c['name'] == category_name), None)
    
    if not current_category:
        return render_template('error.html', 
                            message="Category not found",
                            error_code=404), 404
    
    return render_template(
        'category_detail.html',
        category=current_category,
        articles=articles,
        language=language,
        page=page,
        total_pages=total_pages,
        total_articles=total
    )

@app.route('/breaking')
def breaking_news():
    """Breaking news page."""
    # Get breaking articles
    breaking_data = fetch_breaking_articles()
    articles = breaking_data.get('articles', [])
    
    # Extract unique sources from articles
    sources = list(set(article.get('source', 'Unknown') for article in articles))
    
    return render_template(
        'breaking.html',
        articles=articles,
        sources=sources,
        article_count=len(articles),
        source_count=len(sources)
    )

@app.route('/search')
def search():
    """Search results page."""
    query = request.args.get('q', '')
    language = request.args.get('language', 'all')
    page = request.args.get('page', 1, type=int)
    limit = 20
    skip = (page - 1) * limit
    
    if not query:
        return redirect(url_for('index'))
    
    # Search articles
    params = {
        'search': query,
        'language': language,
        'limit': limit,
        'skip': skip
    }
    
    articles_data = fetch_articles(params)
    articles = articles_data.get('articles', [])
    total = articles_data.get('total', 0)
    
    # Calculate pagination
    total_pages = (total + limit - 1) // limit
    
    return render_template(
        'search.html',
        query=query,
        articles=articles,
        language=language,
        page=page,
        total_pages=total_pages,
        total_results=total
    )

@app.route('/fetch-now', methods=['POST'])
def fetch_now():
    """Trigger manual news fetch."""
    result = trigger_fetch()
    return redirect(url_for('index'))

@app.route('/api/health')
def api_health():
    """API health check."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/{API_VERSION}/health/status", timeout=5)
        backend_status = response.json() if response.status_code == 200 else {"status": "unreachable"}
        
        return jsonify({
            "frontend": "healthy",
            "backend": backend_status,
            "timestamp": datetime.now().isoformat()
        })
    except requests.exceptions.RequestException:
        return jsonify({
            "frontend": "healthy",
            "backend": {"status": "unreachable"},
            "timestamp": datetime.now().isoformat()
        }), 200

@app.errorhandler(404)
def page_not_found(e):
    """404 error handler."""
    return render_template('error.html', 
                          message="Page not found",
                          error_code=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    """500 error handler."""
    return render_template('error.html', 
                          message="Internal server error",
                          error_code=500), 500

@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml with all pages and articles"""
    from flask import Response
    import requests
    from urllib.parse import quote
    
    base_url = 'https://globe-news-jade.vercel.app'
    
    # Start XML
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <!-- Static Pages -->
  <url><loc>https://globe-news-jade.vercel.app/</loc><changefreq>hourly</changefreq><priority>1.0</priority></url>
  <url><loc>https://globe-news-jade.vercel.app/breaking</loc><changefreq>hourly</changefreq><priority>0.9</priority></url>
  <url><loc>https://globe-news-jade.vercel.app/categories</loc><changefreq>daily</changefreq><priority>0.8</priority></url>
  <url><loc>https://globe-news-jade.vercel.app/search</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>
'''
    
    # Add Categories (from your backend)
    try:
        cats = requests.get('https://p01--backend-api--5pt6gkpwq49b.code.run/api/v1/categories', timeout=3).json()
        for cat in cats:
            if cat.get('name'):
                cat_name = quote(cat['name'])
                xml += f'  <url><loc>{base_url}/category/{cat_name}</loc><changefreq>daily</changefreq><priority>0.7</priority></url>\n'
    except:
        pass  # Skip categories if backend fails
    
    # Add Latest Articles (from your homepage)
    try:
        # Get latest 100 articles from your backend
        articles = requests.get('https://p01--backend-api--5pt6gkpwq49b.code.run/api/v1/articles?limit=100', timeout=3).json()
        for article in articles.get('articles', []):
            article_id = article.get('id')
            if article_id:
                xml += f'  <url><loc>{base_url}/article/{article_id}</loc><changefreq>weekly</changefreq><priority>0.6</priority></url>\n'
    except:
        pass  # Skip articles if backend fails
    
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    """Serve robots.txt for search engines"""
    from flask import Response
    
    robots_txt = """User-agent: *
Allow: /
Sitemap: https://globe-news-jade.vercel.app/sitemap.xml
"""
    return Response(robots_txt, mimetype='text/plain')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 GLOBE NEWS FRONTEND - Starting Server")
    print("="*60)
    print(f"📱 Frontend: http://localhost:5000")
    print(f"🔗 Backend: {BACKEND_URL}")
    print(f"📊 Version: 2.0.0")
    print("="*60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
