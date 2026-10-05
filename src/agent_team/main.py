import argparse,asyncio
from .integrations import discover_integrations
from .resource_guard import ResourceGuard
def doctor():
 r=discover_integrations(); print('LocalAgentTeam integration status')
 for x in r.all(): print(f"- {x.provider}: {'AVAILABLE' if x.available else 'NOT INSTALLED'}"+(f' ({x.reason})' if x.reason else ''))
 s=ResourceGuard().snapshot(); print(f"CPU: {s['cpu_percent']:.1f}% | RAM: {s['ram_percent']:.1f}%")
def main():
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='command'); sub.add_parser('doctor'); run=sub.add_parser('run'); run.add_argument('--type',required=True); run.add_argument('--input-url'); a=p.parse_args()
 if a.command=='doctor': doctor(); return
 if a.command=='run' and a.type=='menuradar':
  from .pipeline import MenuRadarPipeline; print('\n'.join(f'{x.from_agent} -> {x.to_agent}: {x.next_action}' for x in MenuRadarPipeline().plan(a.input_url))); return
 if a.command=='run' and a.type=='crawl':
  from .adapters import Crawl4AIAdapter; print(asyncio.run(Crawl4AIAdapter().run(a.input_url))); return
 if a.command=='run' and a.type=='browser':
  from .adapters import BrowserUseAdapter; print(asyncio.run(BrowserUseAdapter().run(f'Open {a.input_url}'))); return
 if a.command=='run' and a.type=='coding':
  from .adapters import OpenHandsAdapter; print(asyncio.run(OpenHandsAdapter().run('Perform the requested coding task.'))); return
 p.print_help()
if __name__=='__main__': main()
