from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import csv,json,re,unicodedata
from guide_acceptance import load_inputs,evaluate,status_text
root=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self,s):
  super().__init__();self.ids=set();self.names={};self.h=None;self.word=[];self.i=None;self.feed(s)
 def handle_starttag(self,t,a):
  d=dict(a)
  if d.get('id'):self.ids.add(d['id'])
  if re.fullmatch(r'h[1-6]',t):self.h=t;self.i=d.get('id');self.word=[]
 def handle_data(self,s):
  if self.h:self.word.append(s)
 def handle_endtag(self,t):
  if t==self.h:
   if self.i:self.names[''.join(self.word).strip().lstrip('#').strip()]=self.i
   self.h=None
cache={}
def norm(s):return ''.join(c.lower() for c in s if unicodedata.category(c)[0] in 'LN')
operational={}
ops_file=root/'artifacts/guide-operational-checks.csv'
if ops_file.exists():
 for item in csv.DictReader(ops_file.open()):operational[item['Feature ID']]=item['Verification result']
asset_gaps={}
gaps_file=root/'artifacts/annotation-asset-gaps.csv'
if gaps_file.exists():
 for item in csv.DictReader(gaps_file.open()):
  if item.get('Status','').startswith('未完成'):asset_gaps[item['Feature ID']]=item
rows=[];issues=[];ids=set()
files=sorted((root/'artifacts').glob('coverage-*.csv'))
for p in files:
 part=list(csv.DictReader(p.open()))
 for x in part:
  fid=x['Feature ID'];assert fid not in ids,fid;ids.add(fid)
  target=x['Documentation path and section'];path,_,fragment=target.partition('#');doc=root/path
  if not path.startswith('docs/zh/guides/'):
   rows.append(x);continue
  if not doc.exists():issues.append(fid+': missing '+path);rows.append(x);continue
  html=root/'doc_build'/Path(path).relative_to('docs').with_suffix('.html')
  if html not in cache:cache[html]=Page(html.read_text())
  page=cache[html];frag=unquote(fragment)
  if frag and frag not in page.ids:
   found=page.names.get(frag)
   if not found:
    found=next((i for name,i in page.names.items() if norm(name)==norm(frag) or norm(i)==norm(frag)),None)
   if found:x['Documentation path and section']=path+'#'+found
   else:issues.append(fid+': missing section '+target)
  x['Content status']=x['Content status'].replace('待网站检查','网站静态检查已通过')
  extra=operational.get(fid)
  if extra:x['Operational verification status']=extra
  gap=asset_gaps.get(fid)
  if gap:x['Asset status']='基础素材已制；专属素材未完成：'+gap['Specific asset gap']
  rows.append(x)
scopes,evidence=load_inputs(root,rows)
acceptance=[]
for x in rows:
 fid=x['Feature ID']
 path=x['Documentation path and section'].partition('#')[0]
 website_ok=path.startswith('docs/zh/guides/') and not any(issue.startswith(fid+':') for issue in issues)
 result=evaluate(root,x,scopes,evidence,asset_gap=fid in asset_gaps,website_ok=website_ok)
 acceptance.append(result)
 x['Acceptance status']=status_text(result)
 if result['required_scopes']:
  progress='；作用域证据：'+('已验收 '+','.join(result['accepted_scopes']) if result['accepted_scopes'] else '尚无完整发行作用域通过')
  x['Operational verification status']+=progress
cols=list(rows[0])
with (root/'artifacts/guide-coverage.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
(root/'artifacts/coverage-anchor-check.json').write_text(json.dumps({'rows':len(rows),'unique_ids':len(ids),'errors':issues},ensure_ascii=False,indent=2)+'\n')
(root/'artifacts/guide-acceptance-evaluation.json').write_text(json.dumps({'schema_version':1,'strict_complete':sum(x['complete'] for x in acceptance),'items':acceptance},ensure_ascii=False,indent=2)+'\n')
print(len(rows),'rows,',len(issues),'anchor issues');print('\n'.join(issues[:65]))
