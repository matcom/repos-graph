import requests
import json

# Category definitions with keywords for matching
CATEGORIES = [
    {
        "id": "programming",
        "name": "Programming",
        "color": "#1f77b4",
        "keywords": ["programming", "pncti", "practicas-primero", "matcom-tester", "programming-languages", "programming-cp"]
    },
    {
        "id": "ml-ai",
        "name": "ML/AI",
        "color": "#ff7f0e",
        "keywords": ["ml", "ai", "ia-", "metaheuristics", "master-ml", "programming-for-data-science", "sim2025"]
    },
    {
        "id": "compilers",
        "name": "Compilers",
        "color": "#2ca02c",
        "keywords": ["cool-compiler", "compilers", "hulk"]
    },
    {
        "id": "networks-distributed",
        "name": "Networks/Distributed",
        "color": "#d62728",
        "keywords": ["computer-networks", "distributed-systems", "sistemas-distribuidos", "matcon-sd", "matcom-sist-dist", "scr_", "matcon", "computer_networks"]
    },
    {
        "id": "algorithms",
        "name": "Algorithms",
        "color": "#9467bd",
        "keywords": ["algos", "dm", "codex", "cs"]
    },
    {
        "id": "tools-projects",
        "name": "Tools/Projects",
        "color": "#8c564b",
        "keywords": ["moogle", "dashboard", "autoexam", "simspider", "gym", "adminbot", "templates", "forms", "domino", "research", "covid", "horarios", "covidsim"]
    },
    {
        "id": "documentation",
        "name": "Documentation",
        "color": "#e377c2",
        "keywords": ["matcom.github.io", ".github", "thesis", "tesis-"]
    }
]

def get_repo_category(repo_name):
    """Categorize a repo based on its name"""
    repo_lower = repo_name.lower()
    for cat in CATEGORIES:
        for kw in cat["keywords"]:
            if kw.lower() in repo_lower:
                return cat
    return CATEGORIES[5]  # Fallback to Tools/Projects

def fetch_matcom_repos():
    """Fetch all public repos from matcom GitHub org"""
    url = "https://api.github.com/orgs/matcom/repos"
    headers = {"User-Agent": "matcom-repos-graph"}
    params = {"per_page": 100, "sort": "pushed"}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def generate_graph_data(repos):
    """Generate hierarchical graph data with 3 levels: matcom -> categories -> repos"""
    nodes = []
    edges = []

    # Level 0: matcom central node
    nodes.append({
        "id": "matcom",
        "name": "matcom",
        "level": 0,
        "url": "https://github.com/matcom",
        "stars": 0,
        "language": "Organization",
        "description": "School of Math and Computer Science, University of Havana",
        "category_id": None,
        "color": "#ff0000"
    })

    # Level 1: Category nodes
    for cat in CATEGORIES:
        cat_id = f"cat-{cat['id']}"
        nodes.append({
            "id": cat_id,
            "name": cat["name"],
            "level": 1,
            "url": None,
            "stars": 0,
            "language": "Category",
            "description": f"{cat['name']} repositories",
            "category_id": cat["id"],
            "color": cat["color"]
        })
        # Edge from matcom to category
        edges.append({"source": "matcom", "target": cat_id})

    # Level 2: Repository nodes
    for repo in repos:
        cat = get_repo_category(repo["name"])
        repo_id = repo["name"]
        nodes.append({
            "id": repo_id,
            "name": repo_id,
            "level": 2,
            "url": repo["html_url"],
            "stars": repo["stargazers_count"],
            "language": repo["language"] or "Unknown",
            "description": repo["description"] or "No description",
            "category_id": cat["id"],
            "color": cat["color"]
        })
        # Edge from category to repo
        edges.append({"source": f"cat-{cat['id']}", "target": repo_id})

    return {"nodes": nodes, "edges": edges, "categories": CATEGORIES}

if __name__ == "__main__":
    print("Fetching matcom repositories...")
    repos = fetch_matcom_repos()
    print(f"Found {len(repos)} repositories")

    print("Generating graph data...")
    graph_data = generate_graph_data(repos)

    output_path = "docs/repos_data.json"
    with open(output_path, "w") as f:
        json.dump(graph_data, f, indent=2)
    
    print(f"Graph data saved to {output_path}")
