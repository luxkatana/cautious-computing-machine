from github import Github
import httpx

# GitHub Configuration
async def notify_user():
    asyncclient = httpx.AsyncClient()
    GITHUB_TOKEN = "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"  # Replace with your GitHub token
    REPO_NAME = "luxkatana/cautious-computing-machine"  # Replace with your repository (e.g., "octocat/Hello-World")

# Discord Webhook URL
    DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1324078613578125415/vd1Sef3zmzehSWoz4zlQe7PSR6LkqOC-RHMYjHaSwKNQcyLsFkMv1xq_hOwy5VQ8893c"  # Replace with your Discord webhook URL

# Step 1: Fetch the latest commit using PyGithub
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    latest_commit = repo.get_commits()[0]

    commit_message = latest_commit.commit.message
    commit_author = latest_commit.commit.author.name

# Step 2: Create the Discord embed payload
    embed = {
        "title": "Applying update, please wait",
        "description": f"**{commit_message}**",
        "color": 0x7289da,  # Discord blue color
        "fields": [
            {"name": "Author", "value": commit_author, "inline": True},
        ],
        "footer": {"text": f"Repository: {REPO_NAME}"},
    }

    payload = {"embeds": [embed]}

    await asyncclient.post(DISCORD_WEBHOOK_URL, json=payload)

