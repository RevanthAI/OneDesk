"""Deterministic fact-first worlds. No model participates in ground truth."""
from __future__ import annotations
import random

PARAMS = ('timeout_sec', 'max_retries', 'rate_limit_rpm', 'batch_size_mb', 'sla_hours', 'circuit_breaker_pct')
TRAIN_SERVICES = 'upi-gateway auth-proxy cart-ledger webhook-dispatcher order-router payment-worker search-indexer profile-store email-relay inventory-sync session-cache audit-stream metrics-agent billing-api checkout-api media-worker coupon-engine loyalty-api shipment-router product-catalog event-router notification-hub tax-engine refund-worker identity-broker'.split()
TEST_SERVICES = 'kyc-verifier settlement-engine fraud-sentinel invoice-mailer consent-vault payout-router mandate-engine statement-worker receipt-store reconciliation-api risk-scorer wallet-bridge dispute-manager merchant-registry token-vault clearing-agent remittance-api escrow-ledger chargeback-worker compliance-gateway beneficiary-store transfer-worker sanctions-checker treasury-router ledger-exporter'.split()

def generate_world(seed=42, split='train', version=1):
    if version==2:
        from .v2_world import make_world
        return make_world(seed,split)
    if version!=1: raise ValueError('unsupported world version')
    if split not in ('train', 'test_synth'):
        raise ValueError(split)
    rng = random.Random(seed)
    train = split == 'train'
    prefix = 'TR' if train else 'TS'
    services = TRAIN_SERVICES if train else TEST_SERVICES
    employees = [f'@{prefix.lower()}_engineer_{i:02d}' for i in range(40)]
    pairs = [(s, p) for s in services for p in PARAMS]
    changed = set(rng.sample(range(len(pairs)), 90))
    facts, incidents = [], []
    # Odd train values and even test values ensure global config-value disjointness,
    # without teaching absurd retry counts just to separate numeric ranges.
    for i, (s, p) in enumerate(pairs):
        scale = {'timeout_sec': 10, 'max_retries': 1, 'rate_limit_rpm': 100,
                 'batch_size_mb': 20, 'sla_hours': 2, 'circuit_breaker_pct': 5}[p]
        old = 2 * rng.randint(1, 4) * scale + (1 if train else 0)
        new = old + 2 * scale if i in changed else old
        source = 'github-mcp' if i % 2 == 0 else 'slack-mcp'
        facts.append(dict(service_name=s, param_name=p, initial_value=old, current_value=new,
            initial_date='2026-02-10T09:00:00+00:00', updated_date='2026-09-18T09:00:00+00:00' if i in changed else '2026-02-10T09:00:00+00:00',
            was_updated=i in changed, notion_page_id=f'NOTION-{prefix}-{i:03d}',
            source_id=f'{"PR" if source == "github-mcp" else "SLACK"}-{prefix}-{i:03d}',
            source_server=source, owner_handle=employees[(i // 6) % 40], db_id=f'DB-{prefix}-{i//6:02d}'))
    for i in range(50):
        s = services[i % len(services)]
        duration = (i % 5 + 1) * (3 if train else 4)
        incidents.append(dict(incident_id=f'INC-{prefix}-{i:02d}', service_name=s,
            started_at='2026-10-01T00:00:00+00:00', resolved_at=f'2026-10-01T{duration:02d}:00:00+00:00',
            root_cause_pr=f'PR-{prefix}-{6*i:03d}', penalty_rate_per_hour=11 if train else 14,
            weight_kg=21 if train else 24))
    return dict(seed=seed, split=split, services=services, employees=employees, facts=facts, incidents=incidents)
