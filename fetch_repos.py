import requests
import json
import time

MAX_ISSUES_PER_REPO = 100

CATEGORIES = [
    {
        "id": "programming",
        "name": "Programming",
        "color": "#1f77b4",
        "keywords": ["programming", "pncti", "practicas-primero", "matcom-tester", "programming-languages", "programming-cp"],
        "subcategories": [
            {"id": "prog-courses", "name": "Courses"},
            {"id": "prog-tools", "name": "Tools"},
            {"id": "prog-practice", "name": "Practice"}
        ]
    },
    {
        "id": "ml-ai",
        "name": "ML/AI",
        "color": "#ff7f0e",
        "keywords": ["ml", "ai", "ia-", "metaheuristics", "master-ml", "programming-for-data-science", "sim2025"],
        "subcategories": [
            {"id": "ml-courses", "name": "Courses"},
            {"id": "ml-projects", "name": "Projects"},
            {"id": "ml-advanced", "name": "Advanced"}
        ]
    },
    {
        "id": "compilers",
        "name": "Compilers",
        "color": "#2ca02c",
        "keywords": ["cool-compiler", "compilers", "hulk"],
        "subcategories": [
            {"id": "comp-cool", "name": "COOL"},
            {"id": "comp-other", "name": "Other"}
        ]
    },
    {
        "id": "networks-distributed",
        "name": "Networks/Distributed",
        "color": "#d62728",
        "keywords": ["computer-networks", "distributed-systems", "sistemas-distribuidos", "matcon-sd", "matcom-sist-dist", "scr_", "matcon", "computer_networks"],
        "subcategories": [
            {"id": "net-courses", "name": "Courses"},
            {"id": "net-projects", "name": "Projects"},
            {"id": "net-scr", "name": "SCR"}
        ]
    },
    {
        "id": "algorithms",
        "name": "Algorithms",
        "color": "#9467bd",
        "keywords": ["algos", "dm", "codex", "cs"],
        "subcategories": [
            {"id": "alg-theory", "name": "Theory"},
            {"id": "alg-structures", "name": "Data Structures"}
        ]
    },
    {
        "id": "tools-projects",
        "name": "Tools/Projects",
        "color": "#8c564b",
        "keywords": ["moogle", "dashboard", "autoexam", "simspider", "gym", "adminbot", "templates", "forms", "domino", "research", "covid", "horarios", "covidsim"],
        "subcategories": [
            {"id": "tools-academic", "name": "Academic"},
            {"id": "tools-infra", "name": "Infrastructure"},
            {"id": "tools-sim", "name": "Simulation"}
        ]
    },
    {
        "id": "documentation",
        "name": "Documentation",
        "color": "#e377c2",
        "keywords": ["matcom.github.io", ".github", "thesis", "tesis-"],
        "subcategories": [
            {"id": "doc-main", "name": "Main Site"},
            {"id": "doc-thesis", "name": "Thesis"}
        ]
    }
]

def get_repo_category(repo_name):
    repo_lower = repo_name.lower()
    for cat in CATEGORIES:
        for kw in cat["keywords"]:
            if kw.lower() in repo_lower:
                return cat
    return CATEGORIES[5]

def get_repo_subcategory(repo_name, category):
    repo_lower = repo_name.lower()
    if category["id"] == "programming":
        if "programming" in repo_lower and "cp" not in repo_lower:
            return "prog-courses"
        elif "pncti" in repo_lower or "matcom-tester" in repo_lower:
            return "prog-tools"
        else:
            return "prog-practice"
    elif category["id"] == "ml-ai":
        if "ml-" in repo_lower or "master-ml" in repo_lower:
            return "ml-courses"
        elif "proj" in repo_lower or "ia-sim" in repo_lower:
            return "ml-projects"
        else:
            return "ml-advanced"
    elif category["id"] == "compilers":
        return "comp-cool" if "cool" in repo_lower else "comp-other"
    elif category["id"] == "networks-distributed":
        if "scr_" in repo_lower:
            return "net-scr"
        elif "projects" in repo_lower or "proy" in repo_lower:
            return "net-projects"
        else:
            return "net-courses"
    elif category["id"] == "algorithms":
        if "codex" in repo_lower or "cs" in repo_lower:
            return "alg-structures"
        else:
            return "alg-theory"
    elif category["id"] == "tools-projects":
        if "moogle" in repo_lower or "dashboard" in repo_lower or "autoexam" in repo_lower:
            return "tools-academic"
        elif "simspider" in repo_lower or "covid" in repo_lower:
            return "tools-sim"
        else:
            return "tools-infra"
    elif category["id"] == "documentation":
        return "doc-thesis" if "tesis" in repo_lower or "thesis" in repo_lower else "doc-main"
    return category["subcategories"][0]["id"]

def fetch_matcom_repos():
    url = "https://api.github.com/orgs/matcom/repos"
    headers = {"User-Agent": "matcom-repos-graph"}
    params = {"per_page": 100, "sort": "pushed"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def fetch_repo_issues(repo_name, token):
    issues = []
    page = 1
    headers = {
        "Authorization": "token " + token,
        "Accept": "application/vnd.github.v3+json"
    }
    while len(issues) < MAX_ISSUES_PER_REPO:
        url = "https://api.github.com/repos/matcom/" + repo_name + "/issues"
        params = {"state": "open", "per_page": 100, "page": page}
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                print("  Error: " + str(response.status_code))
                break
            batch = response.json()
            if not batch:
                break
            issues.extend([i for i in batch if "pull_request" not in i])
            if len(batch) < 100:
                break
            page += 1
            time.sleep(0.1)
        except Exception as e:
            print("  Error: " + str(e))
            break
    return issues[:MAX_ISSUES_PER_REPO]

def generate_graph_data(repos, token):
    nodes = []
    edges = []

    # Level 0: matcom
    nodes.append({
        "id": "matcom",
        "name": "matcom",
        "level": 0,
        "url": "https://github.com/matcom",
        "stars": 0,
        "language": "Organization",
        "description": "School of Math and Computer Science, University of Havana",
        "category_id": None,
        "subcategory_id": None,
        "color": "#ff0000"
    })

    # Level 1: Categories
    for cat in CATEGORIES:
        cat_id = "cat-" + cat["id"]
        nodes.append({
            "id": cat_id,
            "name": cat["name"],
            "level": 1,
            "url": None,
            "stars": 0,
            "language": "Category",
            "description": cat["name"] + " repositories",
            "category_id": cat["id"],
            "subcategory_id": None,
            "color": cat["color"]
        })
        edges.append({"source": "matcom", "target": cat_id})

    # Level 2: Subcategories
    for cat in CATEGORIES:
        cat_id = "cat-" + cat["id"]
        for subcat in cat["subcategories"]:
            subcat_id = "subcat-" + subcat["id"]
            nodes.append({
                "id": subcat_id,
                "name": subcat["name"],
                "level": 2,
                "url": None,
                "stars": 0,
                "language": "Subcategory",
                "description": cat["name"] + " - " + subcat["name"],
                "category_id": cat["id"],
                "subcategory_id": subcat["id"],
                "color": cat["color"]
            })
            edges.append({"source": cat_id, "target": subcat_id})

    # Level 3: Repos + Level 4: Issues
    total_issues = 0
    for repo in repos:
        cat = get_repo_category(repo["name"])
        subcat_id = get_repo_subcategory(repo["name"], cat)

        repo_id = repo["name"]
        nodes.append({
            "id": repo_id,
            "name": repo_id,
            "level": 3,
            "url": repo["html_url"],
            "stars": repo["stargazers_count"],
            "language": repo["language"] or "Unknown",
            "description": repo["description"] or "No description",
            "category_id": cat["id"],
            "subcategory_id": subcat_id.replace("subcat-", ""),
            "color": cat["color"]
        })
        edges.append({"source": "subcat-" + subcat_id, "target": repo_id})

        # Fetch issues for repos that have them
        if repo.get("has_issues") and repo.get("open_issues_count", 0) > 0:
            print("  Fetching issues for " + repo["name"] + "...")
            issues = fetch_repo_issues(repo["name"], token)
            total_issues += len(issues)
            for issue in issues:
                issue_id = "issue-" + repo["name"] + "-" + str(issue["number"])
                nodes.append({
                    "id": issue_id,
                    "name": "#" + str(issue["number"]),
                    "level": 4,
                    "url": issue["html_url"],
                    "title": issue["title"],
                    "state": issue["state"],
                    "labels": [l["name"] for l in issue.get("labels", [])],
                    "repo": repo["name"],
                    "category_id": cat["id"],
                    "subcategory_id": subcat_id.replace("subcat-", ""),
                    "color": "#e67e22"
                })
                edges.append({"source": repo_id, "target": issue_id})

    print("Total issues fetched: " + str(total_issues))
    return {"nodes": nodes, "edges": edges, "categories": CATEGORIES}

if __name__ == "__main__":
    import os
    token = os.environ.get("GITHUB_TOKEN", "YOUR_TOKEN_HERE")

    print("Fetching matcom repositories...")
    repos = fetch_matcom_repos()
    print("Found " + str(len(repos)) + " repositories")

    print("\nGenerating 5-level graph data (with issues)...")
    graph_data = generate_graph_data(repos, token)

    output_path = "docs/repos_data.json"
    with open(output_path, "w") as f:
        json.dump(graph_data, f, indent=2)

    print("\nGraph data saved to " + output_path)
    print("Total nodes: " + str(len(graph_data["nodes"])))
    print("Total edges: " + str(len(graph_data["edges"])))
    print("  - Level 0 (matcom): " + str(len([n for n in graph_data["nodes"] if n["level"]==0])))
    print("  - Level 1 (categories): " + str(len([n for n in graph_data["nodes"] if n["level"]==1])))
    print("  - Level 2 (subcategories): " + str(len([n for n in graph_data["nodes"] if n["level"]==2])))
    print("  - Level 3 (repos): " + str(len([n for n in graph_data["nodes"] if n["level"]==3])))
    print("  - Level 4 (issues): " + str(len([n for n in graph_data["nodes"] if n["level"]==4])))
