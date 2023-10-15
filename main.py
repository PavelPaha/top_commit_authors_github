import asyncio

import git_hunter

hunter = git_hunter.GitHunterAsync('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', 'naumen')

statistic = asyncio.run(hunter.gather_data())

print(type(list(statistic)))