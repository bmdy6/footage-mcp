"""Run from repository root: python3 video/scripts/fetch-gemini4-media.py.
Uses the authorized local Pixabay key without printing it or storing it in this repo.
"""
import json, os, subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2]
env=os.environ.copy()
if not env.get('PIXABAY_API_KEY'):
    vault=json.loads((Path.home()/'.config/ai-vault/vault.json').read_text())
    env['PIXABAY_API_KEY']=vault['personal-infra']['pixabay']['PIXABAY_API_KEY']['value']
for clip,start,duration,note in [
    ('commons:File:Breaking News 5 by Sascha Ende.ogg',18,170,'Gemini4Race music: offset 18s, volume 0.12, fades; CC BY 4.0'),
    ('pixabay:7260',1,12,'Gemini4Race leaderboard backdrop; separate NYC bridge footage used once'),
    ('pixabay:1044',2,4,'Gemini4Race line 7: New York city illustration, NOT IPO event footage'),
]:
    subprocess.run(['uvx','--from','.','footage-mcp','download',clip,'--start',str(start),'--duration',str(duration),
        '--out-dir','video/public/footage','--note',note],cwd=root,env=env,check=True)
