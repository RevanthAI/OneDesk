"""Balanced active groups with temperature exploration and saturated-kind fallback."""
import inspect,math,random,statistics

class NoActiveAdvantage(RuntimeError):pass

class BalancedActiveSampler:
    kinds=('consistent','incident','conflict','abstain')
    def __init__(self,tasks,seed=42):
        self.rng=random.Random(seed);self.buckets={};self.draws={};self.accepted=0;self.saturated=set();self.current_temperature=.8
        self.accepted_by_kind={kind:0 for kind in self.kinds}
        for kind in self.kinds:
            self.buckets[kind]={language:[t for t in tasks if t['kind']==kind and t['language']==language] for language in sorted({t['language'] for t in tasks if t['kind']==kind})}
            if not self.buckets[kind]:raise ValueError('every task kind is required for stratified active GRPO')
            self.draws[kind]=0
            for rows in self.buckets[kind].values():self.rng.shuffle(rows)
    def next_active(self,sample_group,group_size=4,threshold=1e-6,max_attempts=32,on_attempt=None):
        if group_size<2 or max_attempts<1:raise ValueError('invalid active-sampling budget')
        requested=self.kinds[self.accepted%len(self.kinds)]
        remaining=[k for k in self.kinds if k not in self.saturated]
        # Preserve fairness among still-active kinds after a fallback.
        remaining.sort(key=lambda k:(self.accepted_by_kind[k],(self.kinds.index(k)-self.kinds.index(requested))%4))
        signature=inspect.signature(sample_group)
        accepts_temperature='temperature' in signature.parameters or any(p.kind==inspect.Parameter.VAR_KEYWORD for p in signature.parameters.values())
        for kind in remaining:
            languages=sorted(self.buckets[kind])
            for attempt in range(1,max_attempts+1):
                index=self.draws[kind];language=languages[index%len(languages)];bucket=self.buckets[kind][language]
                task=bucket[(index//len(languages))%len(bucket)];self.draws[kind]+=1
                temperature=.8 if attempt<=16 else .95;self.current_temperature=temperature
                group=sample_group([task]*group_size,temperature=temperature) if accepts_temperature else sample_group([task]*group_size)
                if len(group)!=group_size:raise ValueError('incomplete sampled group')
                rewards=[float(r['reward']) for r in group]
                if not all(math.isfinite(r) for r in rewards):raise FloatingPointError('non-finite rollout reward')
                std=statistics.stdev(rewards);skipped=std<threshold
                exhausted=skipped and attempt==max_attempts
                event=dict(task_id=task['task_id'],kind=kind,requested_kind=requested,language=language,sampling_attempt=attempt,sampling_temperature=temperature,reward_std=std,zero_variance_skipped=skipped,optimizer_update_eligible=not skipped,kind_saturated_fallback=exhausted or kind!=requested)
                if exhausted:self.saturated.add(kind)
                if on_attempt:on_attempt(task,group,event)
                if not skipped:
                    self.accepted+=1;self.accepted_by_kind[kind]+=1
                    return [task]*group_size,group,event
        raise NoActiveAdvantage('All four task-kind pools exhausted their exploration budgets without a non-zero-variance group; preserve the last adapter and report early termination.')
