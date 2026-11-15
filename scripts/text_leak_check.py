"""CPU-only exact prompt/identifier audit and exhaustive nearest 5-word Jaccard.

Reads frozen data; writes a separate report. No model, tokenizer, network, or
approximate MinHash is needed: exact sparse Jaccard is fast at this dataset size.
"""
import argparse
from collections import Counter, defaultdict
from decimal import Decimal
import hashlib
import itertools
import json
from pathlib import Path
import re
import time
import unicodedata

ROOT=Path(__file__).resolve().parents[1]
FILES={
 'sft':'train_sft_240.jsonl', 'grpo1':'train_grpo_stage1.jsonl',
 'grpo2':'train_grpo_stage2.jsonl','validation':'val_train_80.jsonl',
 'synthetic':'holdout_synth_400_frozen.jsonl','repo_style':'holdout_repo_style_100_frozen.jsonl'}


def load(name):
    return [json.loads(line) for line in (ROOT/'data_v2'/FILES[name]).read_text().splitlines()]


def scalar(value):
    if value is None:return None
    if isinstance(value,(int,float)) or (isinstance(value,str) and re.fullmatch(r'[+-]?[\d.]+',value)):
        return str(Decimal(str(value)).normalize())
    return str(value).strip().casefold()


def tokens(text):
    # Keep Devanagari/Telugu combining marks in their words; \w alone drops them.
    text=unicodedata.normalize('NFC',text).casefold()
    return ''.join(c if unicodedata.category(c)[0] in 'LNM' or c in '_-' else ' ' for c in text).split()


def grams(text,n=5):
    ts=tokens(text)
    return {tuple(ts[i:i+n]) for i in range(len(ts)-n+1)}


def masker(all_rows):
    substitutions={}
    for row in all_rows:
        for field,label in [('service_name','SERVICE'),('param_name','PARAMETER'),('incident_id','INCIDENT')]:
            if row.get(field):substitutions[row[field].casefold()]=label
    for path in sorted((ROOT/'data_v2').glob('world_*.json')):
        w=json.loads(path.read_text())
        for field,label in [('services','SERVICE'),('employees','EMPLOYEE')]:
            for value in w[field]:substitutions[value.casefold()]=label
    pattern=re.compile(r'(?<![\w-])(?:'+'|'.join(re.escape(s) for s in sorted(substitutions,key=len,reverse=True))+r')(?![\w-])',re.I)
    return lambda text:pattern.sub(lambda m:substitutions[m[0].casefold()],text)


def model_prompt(row):
    return '\n'.join(message['role']+': '+message['content'] for message in row['prompt'])


def nearest(train,holdout,text):
    train_sets=[grams(text(r)) for r in train];lengths=[len(s) for s in train_sets]
    postings=defaultdict(list)
    for i,gs in enumerate(train_sets):
        for g in gs:postings[g].append(i)
    result=[]
    for r in holdout:
        query=grams(text(r));counts=Counter(i for g in query for i in postings.get(g,[]))
        best_i=0;best=0.
        for i,intersection in sorted(counts.items()):
            score=intersection/(len(query)+lengths[i]-intersection)
            if score>best:best=score;best_i=i
        shared=sorted(query&train_sets[best_i])[:5]
        result.append(dict(shared_5gram_examples=[' '.join(g) for g in shared],task_id=r['task_id'],case_id=r['case_id'],language=r['language'],kind=r['kind'],nearest_train_task_id=train[best_i]['task_id'],jaccard=best,holdout_5grams=len(query)))
    return result


def stats(results):
    import numpy as np
    a=np.array([x['jaccard'] for x in results])
    return dict(n=len(a),mean=float(a.mean()),median=float(np.median(a)),p90=float(np.percentile(a,90)),p95=float(np.percentile(a,95)),max=float(a.max()),
                at_least_0_5=int((a>=.5).sum()),at_least_0_8=int((a>=.8).sum()),equal_1=int((a==1).sum()))


def audit():
    start=time.perf_counter();data={name:load(name) for name in FILES};train=data['sft']+data['grpo1']+data['grpo2'];holdout=data['synthetic']+data['repo_style']
    assert len(train)==1120 and len(holdout)==500
    inputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data_v2').iterdir() if p.is_file()}
    pairs=[]
    for a,b in itertools.combinations(data,2):
        def keys(rs,field):return {r[field] for r in rs if r.get(field) is not None}
        config=lambda rs:{(r['service_name'],r['param_name']) for r in rs}
        row=dict(splits=[a,b],case_id_overlap=len(keys(data[a],'case_id')&keys(data[b],'case_id')),
                 service_parameter_overlap=len(config(data[a])&config(data[b])),incident_id_overlap=len(keys(data[a],'incident_id')&keys(data[b],'incident_id')))
        assert row['case_id_overlap']==row['service_parameter_overlap']==row['incident_id_overlap']==0
        pairs.append(row)
    exact_set={r['question'] for r in train};exact=[r['task_id'] for r in holdout if r['question'] in exact_set]
    full_set={model_prompt(r) for r in train};exact_full=[r['task_id'] for r in holdout if model_prompt(r) in full_set]
    mask=masker(sum(data.values(),[]));masked={mask(r['question']) for r in train}
    masked_duplicates=[r['task_id'] for r in holdout if mask(r['question']) in masked]
    similarities={}
    for key,method in [('raw_question',lambda r:r['question']),('entity_parameter_masked_question',lambda r:mask(r['question'])),('model_visible_prompt_with_shared_system',model_prompt),('entity_parameter_masked_model_visible_prompt',lambda r:mask(model_prompt(r)))]:
        rr=nearest(train,holdout,method)
        similarities[key]=dict(overall=stats(rr),by_split={name:stats([r for r in rr if r['task_id'] in {t['task_id'] for t in data[name]}]) for name in ['synthetic','repo_style']},nearest_matches=rr)
    train_values={scalar(r['gold_value']) for r in train if r['gold_value'] is not None}
    collisions=[r for r in holdout if r['gold_value'] is not None and scalar(r['gold_value']) in train_values]
    nonnull=[r for r in holdout if r['gold_value'] is not None]
    examples=[]
    for value in sorted({scalar(r['gold_value']) for r in collisions},key=Decimal):
        a=next(r for r in train if scalar(r['gold_value'])==value);b=next(r for r in collisions if scalar(r['gold_value'])==value)
        examples.append(dict(value=value,train_task_id=a['task_id'],train_kind=a['kind'],train_service=a['service_name'],train_parameter=a['param_name'],holdout_task_id=b['task_id'],holdout_kind=b['kind'],holdout_service=b['service_name'],holdout_parameter=b['param_name']))
    train_facts={(r['service_name'],r['param_name'],scalar(r['gold_value'])) for r in train if r['gold_value'] is not None}
    fact_overlap=[r['task_id'] for r in nonnull if (r['service_name'],r['param_name'],scalar(r['gold_value'])) in train_facts]
    assert not exact and not exact_full and not fact_overlap
    result=dict(method='Exhaustive exact 5-word shingle Jaccard nearest-neighbor search, using inverted postings; no approximate MinHash.',normalization='NFC + casefold + Unicode letter/mark/number words; retain internal hyphens and underscores; no stopword removal.',scope='Train = SFT + both GRPO pools; validation excluded from text comparisons; all six splits included in 15 pairwise identifier checks.',train_rows=len(train),train_cases=len({r['case_id'] for r in train}),holdout_rows=500,holdout_cases=len({r['case_id'] for r in holdout}),
        exact_question_overlap=dict(count=len(exact),denominator=500,task_ids=exact),exact_model_visible_prompt_overlap=dict(count=len(exact_full),denominator=500,task_ids=exact_full),
        exact_entity_masked_question_overlap=dict(count=len(masked_duplicates),denominator=500,task_ids=masked_duplicates),
        split_pairwise_checks=pairs,similarity=similarities,
        gold_scalar_overlap=dict(count=len(collisions),denominator_nonnull=len(nonnull),fraction_nonnull=len(collisions)/len(nonnull),null_holdout_rows=500-len(nonnull),unique_repeated_values=len(examples),by_kind=dict(Counter(r['kind'] for r in collisions)),task_ids=[r['task_id'] for r in collisions],examples=examples),
        service_parameter_gold_fact_overlap=dict(count=len(fact_overlap),denominator_nonnull=len(nonnull),task_ids=fact_overlap),
        interpretation='Identifier separation and zero exact prompt duplicates hold. Natural-language templates and common system/tool instructions recur; similarity is not proof of semantic independence. Repeated scalar answers on different entities/parameters or incident calculations are reported explicitly, not declared zero leakage.',input_sha256=inputs,seconds=time.perf_counter()-start)
    assert inputs=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data_v2').iterdir() if p.is_file()}
    return result


def summary(result):
    raw=result['similarity']['raw_question']['overall'];masked=result['similarity']['entity_parameter_masked_question']['overall'];gold=result['gold_scalar_overlap'];full=result['similarity']['model_visible_prompt_with_shared_system']['overall']
    return (f"The CPU text audit found **0/500 exact holdout prompt duplicates**, with mean nearest-train 5-word Jaccard **{raw['mean']:.6f} raw / {masked['mean']:.6f} entity-masked**; including shared system/tool instructions raises raw similarity to **{full['mean']:.6f}**. "
            f"All 15 split pairs have zero shared case IDs, service/parameter pairs or incident IDs, but **{gold['count']}/{gold['denominator_nonnull']} non-null holdout scalar answers recur** ({gold['unique_repeated_values']} numbers) on different facts; no service/parameter/gold-value tuple overlaps.")


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'reports/submission/TEXT_LEAK_AUDIT.json');args=p.parse_args()
    result=audit();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(summary(result));print(json.dumps({k:result[k] for k in ['train_rows','holdout_rows','seconds']}))

if __name__=='__main__':main()
