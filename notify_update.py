from github import Github
from discord import TextChannel, Embed

# GitHub Configuration
async def notify_user(channel: TextChannel):
    GITHUB_TOKEN = "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"  # Replace with your GitHub token
    REPO_NAME = "luxkatana/cautious-computing-machine"  # Replace with your repository (e.g., "octocat/Hello-World")

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    latest_commit = repo.get_commits()[0]

    commit_message = latest_commit.commit.message
    commit_author = latest_commit.commit.author.name

    embed = Embed.from_dict({
        "title": "Last update has been migrated",
        "description": f"**{commit_message}**",
        "color": 0x7289da,  # Discord blue color
        "fields": [
            {"name": "Author", "value": commit_author, "inline": True},
        ],
        "footer": {"text": f"Repository: {REPO_NAME}"},
    })


    await channel.send(embed=embed)

