import requests
import os
import json
from datetime import datetime

def generate_svg_badge(rank, level, streak, username):
    """Generate an SVG badge with TryHackMe stats"""
    
    svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="120" viewBox="0 0 400 120">
    <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#212c42;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#2d3748;stop-opacity:1" />
        </linearGradient>
    </defs>
    
    <!-- Background -->
    <rect width="400" height="120" rx="15" fill="url(#grad1)" stroke="#4a5568" stroke-width="2"/>
    
    <!-- TryHackMe Logo Area -->
    <rect x="10" y="10" width="80" height="100" rx="10" fill="#c53030"/>
    <text x="50" y="35" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="12" font-weight="bold">THM</text>
    <text x="50" y="75" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="10">HACKER</text>
    
    <!-- Stats -->
    <text x="110" y="30" fill="#e2e8f0" font-family="Arial, sans-serif" font-size="16" font-weight="bold">{username}</text>
    
    <text x="110" y="55" fill="#cbd5e0" font-family="Arial, sans-serif" font-size="14">Rank: {rank}</text>
    <text x="110" y="75" fill="#cbd5e0" font-family="Arial, sans-serif" font-size="14">Level: {level}</text>
    <text x="110" y="95" fill="#cbd5e0" font-family="Arial, sans-serif" font-size="14">Streak: {streak} days</text>
    
    <!-- Last Updated -->
    <text x="390" y="110" text-anchor="end" fill="#718096" font-family="Arial, sans-serif" font-size="10">Updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</text>
</svg>"""
    
    return svg_template

def fetch_tryhackme_stats(username):
    """Fetch user stats from TryHackMe API using username"""
    try:
        # TryHackMe public API endpoint - using username instead of userPublicId
        url = f"https://tryhackme.com/api/v2/badges/public-profile?userPublicId={username}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"API Response Status: {response.status_code}")
        print(f"API Response: {response.text[:500]}...")  # Debug output
        
        if response.status_code == 200:
            # The response might be HTML/SVG content, let's try a different approach
            # Let's try the user profile API instead
            profile_url = f"https://tryhackme.com/api/user/public-profile/{username}"
            profile_response = requests.get(profile_url, headers=headers, timeout=10)
            
            print(f"Profile API Response Status: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                try:
                    data = profile_response.json()
                    print(f"Profile data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    # Try to extract stats from the profile response
                    rank = data.get('globalRanking', 'N/A')
                    level = data.get('userRank', data.get('level', 'N/A'))
                    streak = data.get('currentStreak', 0)
                    
                    return {
                        'rank': rank,
                        'level': level,
                        'streak': streak,
                        'success': True
                    }
                except json.JSONDecodeError:
                    print("Failed to parse JSON response")
                    return {'success': False, 'error': 'Invalid JSON response'}
            else:
                return {'success': False, 'error': f'Profile API HTTP {profile_response.status_code}'}
        else:
            return {'success': False, 'error': f'Badge API HTTP {response.status_code}'}
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {'success': False, 'error': str(e)}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {'success': False, 'error': str(e)}

def main():
    username = os.environ.get('THM_USERNAME', 'anishalx')
    
    print(f"Fetching stats for username: {username}")
    
    # Fetch current stats
    stats = fetch_tryhackme_stats(username)
    
    if stats.get('success'):
        print(f"Successfully fetched stats: Rank {stats['rank']}, Level {stats['level']}, Streak {stats['streak']}")
        
        # Generate SVG badge
        svg_content = generate_svg_badge(stats['rank'], stats['level'], stats['streak'], username)
        
        # Ensure assets directory exists
        os.makedirs('assets', exist_ok=True)
        
        # Save the badge
        with open('assets/tryhackme-badge.svg', 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print("Badge updated successfully!")
        
        # Also save stats as JSON for debugging
        with open('assets/thm-stats.json', 'w') as f:
            json.dump({
                **stats,
                'username': username,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
            
    else:
        print(f"Failed to fetch stats: {stats.get('error', 'Unknown error')}")
        
        # Create a fallback badge
        svg_content = generate_svg_badge("Error", "N/A", 0, username)
        os.makedirs('assets', exist_ok=True)
        
        with open('assets/tryhackme-badge.svg', 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print("Created fallback badge due to API error")

if __name__ == "__main__":
    main()
