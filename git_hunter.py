import aiohttp
import asyncio
from collections import Counter
import requests


# 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

class GitHunterAsync:
    repos_statistic = []

    def __init__(self, token, org):
        self.headers = {"Authorization": f"Bearer {token}"}
        self.org = org
        # asyncio.run(self.gather_data())

    async def get_org_repos(self):
        url = f"https://api.github.com/orgs/{self.org}/repos"
        repos = []
        async with aiohttp.ClientSession() as session:
            while url:
                async with session.get(url, headers=self.headers) as response:
                    repos_part = await response.json()
                    repos.extend(repos_part)
                    url = response.links.get('next', {}).get('url')
        return repos

    async def get_all_commits(self, session, repo):
        url = f"https://api.github.com/repos/{self.org}/{repo}/commits"
        commits = Counter()
        while url:
            async with session.get(url, headers=self.headers, params={"per_page": 100}) as response:
                commits_part = await response.json()
                await self.get_commits_without_merge_pull_request(commits, commits_part)
                next_url = response.links.get('next', {}).get('url')

                if next_url is None:
                    break
                next_url_host = next_url.host
                response_url_host = response.url.host
                url = next_url if next_url_host == response_url_host else None

        self.repos_statistic+=[(repo, commits)]
        return commits

    async def get_commits_without_merge_pull_request(self, commits, commits_part):
        for commit_information in commits_part:
            commit = commit_information.get("commit")
            if commit:
                message = commit["message"]
                if "Merge pull request #" not in message:
                    email = commit["author"]["email"]
                    commits[email] += 1

    async def gather_data(self):
        repos = await self.get_org_repos()
        frequency_commits = Counter()
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_all_commits(session, repo["name"]) for repo in repos]
            all_repos_commits = await asyncio.gather(*tasks)
            for commits in all_repos_commits:
                frequency_commits += commits
        return frequency_commits.most_common()

class GitHunterSync:
    def __init__(self, token, org):
        self.headers = {"Authorization": f"Bearer {token}"}
        self.org = org

    def get_org_repos(self):
        url = f"https://api.github.com/orgs/{self.org}/repos"

        repos = []
        response = requests.get(url, headers=self.headers)
        repos_part = response.json()
        repos.extend(repos_part)
        while 'next' in response.links:
            url = response.links['next']['url']
            response = requests.get(url, headers=self.headers)
            repos_part = response.json()
            repos.extend(repos_part)
        return repos

    def get_all_commits(self, repo):
        url = f"https://api.github.com/repos/{self.org}/{repo}/commits"
        commits = Counter()
        response = requests.get(url, headers=self.headers, params={"per_page": 100})
        commits_part = response.json()
        self.get_commits_without_merge_pull_request(commits, commits_part)

        while 'next' in response.links:
            url = response.links['next']['url']
            response = requests.get(url, headers=self.headers, params={"per_page": 100})
            commits_part = response.json()
            self.get_commits_without_merge_pull_request(commits, commits_part)
        return commits

    def get_frequency_one_repo(self, repo):
        data = self.get_all_commits(repo)

    def get_commits_without_merge_pull_request(self, commits, commits_part):
        for commit_information in commits_part:
            commit = commit_information.get("commit")
            if commit:
                message = commit["message"]
                if "Merge pull request #" not in message:
                    email = commit["author"]["email"]
                    commits[email]+=1

    def gather_data(self):
        repos = self.get_org_repos()

        frequency_commits = Counter()
        print(f"Found {len(repos)} repos")
        for repo in repos:
            commits = self.get_all_commits(repo["name"])
            frequency_commits+=commits
        return frequency_commits.most_common()


def check_solutions(org_names):
    global token
    for org in org_names:
        hunter_sync = GitHunterSync(token, org)
        top_commit_authors_sync = hunter_sync.gather_data()

        hunter_async = GitHunterAsync(token, org)
        top_commit_authors_async = asyncio.run(hunter_async.gather_data())

        if len(top_commit_authors_async) != len(top_commit_authors_sync):
            print("Не равные длины")
            return False

        # print(top_commit_authors_sync)

        print(top_commit_authors_async)
        for i in range(len(top_commit_authors_sync)):
            if top_commit_authors_sync[i] != top_commit_authors_async[i]:
                print(f'{top_commit_authors_sync[i]} != {top_commit_authors_async[i]}')
                return False
        #
        # print(len(hunter_async.repos_statistic))
        # print(hunter_async.repos_statistic)
    print("OK")
    return True

token = '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'

check_solutions(['naumen'])
# hunter_async = GitHunterAsync(token, 'naumen')
# top_commit_authors_async = asyncio.run(hunter_async.gather_data())
# print(top_commit_authors_async)