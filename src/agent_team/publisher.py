import os

class GitHubPublisher:
    def __init__(self, token=None, repo_name=None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.repo_name = repo_name or os.getenv('GITHUB_REPO')
        if not self.token: raise RuntimeError('GITHUB_TOKEN is not configured')
        if not self.repo_name: raise RuntimeError('GITHUB_REPO is not configured')

    def _repo(self):
        try:
            from github import Github
        except ImportError as e:
            raise RuntimeError('PyGithub is not installed') from e
        return Github(self.token).get_repo(self.repo_name)

    def upsert_text(self, path, content, message, branch='main'):
        repo = self._repo()
        try:
            current = repo.get_contents(path, ref=branch)
            result = repo.update_file(path, message, content, current.sha, branch=branch)
            return {'status':'updated','path':path,'commit':result['commit'].sha}
        except Exception as exc:
            if '404' not in str(exc): raise
            result = repo.create_file(path, message, content, branch=branch)
            return {'status':'created','path':path,'commit':result['commit'].sha}