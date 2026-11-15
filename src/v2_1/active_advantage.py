"""Positive-anchor groups, weighted accepted-update rotation, bounded exploration."""
import inspect,math,random,statistics
class NoActiveAdvantage(RuntimeError):pass
class PositiveAnchorSampler:
    kinds=('conflict','incident','consistent','abstain')
    cycle=('conflict','incident','consistent','conflict','incident','conflict','incident','abstain')
    def __init__(self,tasks,seed=42,offset=0,temperature=.8,retry_temperature=.95):
        self.temperature=temperature;self.retry_temperature=retry_temperature;self.rng=random.Random(seed);self.offset=offset;self.accepted=0;self.accepted_by_kind=dict.fromkeys(self.kinds,0);self.draws=dict.fromkeys(self.kinds,0);self.buckets={};self.fallbacks=0
        for k in self.kinds:
            self.buckets[k]={l:[t for t in tasks if t['kind']==k and t['language']==l] for l in sorted({t['language'] for t in tasks if t['kind']==k})}
            if not self.buckets[k]:raise ValueError('All four task kinds required')
            for b in self.buckets[k].values():self.rng.shuffle(b)
    def next_active(self,sample_group,group_size=4,threshold=1e-6,max_attempts=32,on_attempt=None):
        if group_size not in (4,6):raise ValueError('Audited false-abstention advantage guarantee supports G=4 or G=6')
        requested=self.cycle[(self.offset+self.accepted)%8]
        order=[requested]+[k for k in self.kinds if k!=requested and k!='abstain']
        for k in order:
            langs=sorted(self.buckets[k])
            for attempt in range(1,max_attempts+1):
                n=self.draws[k];lang=langs[n%len(langs)];bucket=self.buckets[k][lang];task=bucket[(n//len(langs))%len(bucket)];self.draws[k]+=1
                temp=self.temperature if attempt<=16 else self.retry_temperature;group=sample_group([task]*group_size,temperature=temp)
                if len(group)!=group_size:raise ValueError('Partial group')
                rewards=[float(r['reward']) for r in group]
                if not all(math.isfinite(r) for r in rewards):raise FloatingPointError('Nonfinite reward')
                std=statistics.stdev(rewards);zero=std<=threshold;negative=k!='abstain' and max(rewards)<=0.;eligible=not zero and not negative
                event=dict(task_id=task['task_id'],kind=k,requested_kind=requested,language=lang,sampling_attempt=attempt,sampling_temperature=temp,reward_std=std,max_reward=max(rewards),zero_variance_skipped=zero,all_negative_skipped=negative,optimizer_update_eligible=eligible,kind_saturated_fallback=(not eligible and attempt==max_attempts) or k!=requested)
                if on_attempt:on_attempt(task,group,event)
                if eligible:
                    self.accepted+=1;self.accepted_by_kind[k]+=1;self.fallbacks+=int(k!=requested)
                    return [task]*group_size,group,event
        raise NoActiveAdvantage('All eligible task-kind pools exhausted the bounded positive-anchor exploration budget; preserve best validation and stop without fake updates.')
BalancedActiveSampler=PositiveAnchorSampler
