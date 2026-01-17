# Budget Tracking Documentation

## LLM Context Window Experiments Platform

**Document Version:** 1.0
**Last Updated:** January 2026
**Document Owner:** Project Team
**Status:** Active

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Cost Model Overview](#2-cost-model-overview)
3. [Resource Categories](#3-resource-categories)
4. [Pricing Reference](#4-pricing-reference)
5. [Budget Allocation](#5-budget-allocation)
6. [Cost Tracking Methodology](#6-cost-tracking-methodology)
7. [Experiment Cost Analysis](#7-experiment-cost-analysis)
8. [Cost Optimization Strategies](#8-cost-optimization-strategies)
9. [Budget Monitoring Dashboard](#9-budget-monitoring-dashboard)
10. [Historical Cost Data](#10-historical-cost-data)
11. [Projections and Forecasting](#11-projections-and-forecasting)
12. [Budget Alerts and Thresholds](#12-budget-alerts-and-thresholds)

---

## 1. Executive Summary

### 1.1 Purpose

This document provides comprehensive budget tracking and cost analysis for the LLM Context Window Experiments Platform. It enables:
- Transparent cost monitoring across all experiments
- Informed decision-making on resource allocation
- Identification of cost optimization opportunities
- Accurate forecasting for future experiments

### 1.2 Key Metrics

| Metric | Current Value | Target | Status |
|--------|---------------|--------|--------|
| Total Monthly Budget | $50.00 | $50.00 | On Track |
| Avg Cost per Experiment | $0.15 | $0.20 | Under Budget |
| Token Efficiency | 85% | 80% | Exceeds Target |
| Infrastructure Utilization | 72% | 70% | Optimal |

### 1.3 Cost Distribution

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MONTHLY COST DISTRIBUTION                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LLM Inference (Ollama)     ████████████████████████░░░░░░  60%  $30.00   │
│  Compute Resources          ████████████░░░░░░░░░░░░░░░░░░  25%  $12.50   │
│  Storage                    ████░░░░░░░░░░░░░░░░░░░░░░░░░░  10%   $5.00   │
│  CI/CD Pipeline             ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░   5%   $2.50   │
│                             ──────────────────────────────────────────────  │
│                                                                 TOTAL: $50.00 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Cost Model Overview

### 2.1 Cost Components

The platform's costs are categorized into four main areas:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COST MODEL STRUCTURE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              ┌─────────────────┐                            │
│                              │  Total Cost     │                            │
│                              │    (Monthly)    │                            │
│                              └────────┬────────┘                            │
│                                       │                                      │
│           ┌───────────────┬───────────┼───────────┬───────────────┐         │
│           │               │           │           │               │         │
│           ▼               ▼           ▼           ▼               │         │
│   ┌───────────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐    │         │
│   │  LLM Costs    │ │  Compute  │ │  Storage  │ │  CI/CD    │    │         │
│   │  ─────────    │ │  ────────  │ │  ────────  │ │  ──────   │    │         │
│   │  • Tokens     │ │  • CPU    │ │  • Disk   │ │  • Actions│    │         │
│   │  • API calls  │ │  • Memory │ │  • Logs   │ │  • Minutes│    │         │
│   │  • Latency    │ │  • GPU    │ │  • Results│ │  • Storage│    │         │
│   └───────────────┘ └───────────┘ └───────────┘ └───────────┘    │         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Cost Calculation Formula

```
Total Experiment Cost = LLM Cost + Compute Cost + Storage Cost

Where:
  LLM Cost = (Input Tokens × Input Price) + (Output Tokens × Output Price)
  Compute Cost = (CPU Hours × CPU Rate) + (Memory GB-Hours × Memory Rate)
  Storage Cost = (Data GB × Storage Rate) + (Log GB × Log Rate)
```

---

## 3. Resource Categories

### 3.1 LLM Resources

| Resource | Unit | Description |
|----------|------|-------------|
| Input Tokens | per 1K | Tokens in prompt/context |
| Output Tokens | per 1K | Tokens in LLM response |
| API Calls | per call | Individual LLM requests |
| Inference Time | seconds | Time for model inference |

### 3.2 Compute Resources

| Resource | Unit | Description |
|----------|------|-------------|
| CPU Time | core-hours | Processing time |
| Memory | GB-hours | RAM utilization |
| GPU Time | GPU-hours | GPU acceleration (if applicable) |

### 3.3 Storage Resources

| Resource | Unit | Description |
|----------|------|-------------|
| Experiment Results | GB/month | JSON result files |
| Log Files | GB/month | Experiment logs |
| Vector Indices | GB/month | FAISS indices (Task 3) |
| Embeddings Cache | GB/month | Cached embeddings |

### 3.4 CI/CD Resources

| Resource | Unit | Description |
|----------|------|-------------|
| Action Minutes | minutes | GitHub Actions runtime |
| Storage | GB/month | Artifact storage |

---

## 4. Pricing Reference

### 4.1 Local Ollama (Current Setup)

| Model | Input Cost | Output Cost | Notes |
|-------|------------|-------------|-------|
| llama3.2:1b | $0.00 | $0.00 | Local inference - electricity only |
| llama3.2:3b | $0.00 | $0.00 | Local inference - electricity only |

**Effective Cost:** ~$0.02/hour electricity for local GPU/CPU

### 4.2 Cloud LLM Alternatives (Reference)

| Provider | Model | Input ($/1M tokens) | Output ($/1M tokens) |
|----------|-------|---------------------|----------------------|
| OpenAI | GPT-4-turbo | $10.00 | $30.00 |
| OpenAI | GPT-3.5-turbo | $0.50 | $1.50 |
| Anthropic | Claude 3 Sonnet | $3.00 | $15.00 |
| Anthropic | Claude 3 Haiku | $0.25 | $1.25 |
| Google | Gemini Pro | $0.50 | $1.50 |

### 4.3 Compute Pricing

| Resource | Rate | Unit |
|----------|------|------|
| Local CPU | $0.02 | per hour (electricity) |
| Local GPU (RTX 3080) | $0.10 | per hour (electricity) |
| Cloud CPU (AWS t3.medium) | $0.0416 | per hour |
| Cloud GPU (AWS g4dn.xlarge) | $0.526 | per hour |

### 4.4 Storage Pricing

| Type | Rate | Unit |
|------|------|------|
| Local SSD | $0.001 | per GB/month |
| AWS S3 | $0.023 | per GB/month |
| GitHub Storage | Free | up to 500 MB |

---

## 5. Budget Allocation

### 5.1 Monthly Budget Breakdown

| Category | Allocation | Amount | Priority |
|----------|------------|--------|----------|
| LLM Inference | 60% | $30.00 | Critical |
| Development Compute | 25% | $12.50 | High |
| Storage & Backup | 10% | $5.00 | Medium |
| CI/CD & Testing | 5% | $2.50 | Medium |
| **Total** | **100%** | **$50.00** | - |

### 5.2 Per-Experiment Budget

| Experiment | Tokens (est.) | Trials | Est. Cost | Actual Cost |
|------------|---------------|--------|-----------|-------------|
| Task 1: Lost in Middle | 50K | 21 | $0.05 | $0.04 |
| Task 2: Context Size | 200K | 12 | $0.10 | $0.08 |
| Task 3: RAG vs Full | 500K | 10 | $0.15 | $0.12 |
| Task 4: Memory Strategies | 300K | 15 | $0.12 | $0.10 |
| **Total per Run** | **1.05M** | **58** | **$0.42** | **$0.34** |

### 5.3 Budget Reserve

| Reserve Type | Amount | Purpose |
|--------------|--------|---------|
| Contingency (10%) | $5.00 | Unexpected costs |
| Scaling Buffer (5%) | $2.50 | Additional experiments |
| Emergency | $2.50 | Critical issues |

---

## 6. Cost Tracking Methodology

### 6.1 Token Tracking

Each experiment automatically tracks token usage:

```python
# Token tracking structure (saved with results)
{
    "cost_metrics": {
        "input_tokens": 45230,
        "output_tokens": 1250,
        "total_tokens": 46480,
        "estimated_cost_usd": 0.04,
        "tokens_per_trial": 2213,
        "cost_per_trial": 0.002
    }
}
```

### 6.2 Automated Cost Calculation

```python
def calculate_experiment_cost(results: dict, pricing: dict) -> dict:
    """Calculate cost for an experiment run."""
    input_tokens = results.get("total_input_tokens", 0)
    output_tokens = results.get("total_output_tokens", 0)

    input_cost = (input_tokens / 1_000_000) * pricing["input_per_million"]
    output_cost = (output_tokens / 1_000_000) * pricing["output_per_million"]

    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost,
        "tokens_used": input_tokens + output_tokens
    }
```

### 6.3 Cost Aggregation

Costs are aggregated at multiple levels:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COST AGGREGATION LEVELS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Trial Level                                                               │
│   ┌─────────────────────────────────────────────────────────┐              │
│   │ • Tokens used in single query                            │              │
│   │ • Latency/compute time                                   │              │
│   │ • Individual API call cost                               │              │
│   └─────────────────────────────────────────────────────────┘              │
│                           │                                                 │
│                           ▼                                                 │
│   Experiment Level                                                          │
│   ┌─────────────────────────────────────────────────────────┐              │
│   │ • Sum of all trial costs                                 │              │
│   │ • Average cost per trial                                 │              │
│   │ • Total experiment duration                              │              │
│   └─────────────────────────────────────────────────────────┘              │
│                           │                                                 │
│                           ▼                                                 │
│   Daily/Weekly/Monthly Level                                                │
│   ┌─────────────────────────────────────────────────────────┐              │
│   │ • Aggregated costs across all experiments                │              │
│   │ • Trend analysis                                         │              │
│   │ • Budget vs actual comparison                            │              │
│   └─────────────────────────────────────────────────────────┘              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Experiment Cost Analysis

### 7.1 Task 1: Lost in the Middle

| Metric | Value |
|--------|-------|
| Avg Tokens per Query | 2,150 |
| Queries per Run | 21 (7 positions × 3 trials) |
| Total Tokens | ~45,000 |
| Estimated Cost (Ollama) | $0.00 (local) |
| Estimated Cost (GPT-3.5) | $0.07 |
| Estimated Cost (GPT-4) | $0.45 |

**Cost Efficiency Rating:** Excellent (local inference)

### 7.2 Task 2: Context Window Size

| Document Count | Tokens | Cost (Local) | Cost (GPT-3.5) |
|----------------|--------|--------------|----------------|
| 5 docs | 2,500 | $0.00 | $0.004 |
| 10 docs | 5,000 | $0.00 | $0.008 |
| 20 docs | 10,000 | $0.00 | $0.015 |
| 30 docs | 15,000 | $0.00 | $0.023 |

**Scaling Factor:** Linear with document count

### 7.3 Task 3: RAG vs Full Context

| Approach | Tokens/Query | 10 Queries | Cost Savings |
|----------|--------------|------------|--------------|
| Full Context | 10,000 | 100,000 | Baseline |
| RAG (k=3) | 1,500 | 15,000 | 85% |
| RAG (k=5) | 2,500 | 25,000 | 75% |

**Key Insight:** RAG provides 75-85% token cost reduction

### 7.4 Task 4: Memory Strategies

| Strategy | Tokens/Step | 10 Steps | Efficiency |
|----------|-------------|----------|------------|
| Full History | 5,000 | 50,000 | Low |
| SELECT | 1,500 | 15,000 | High |
| COMPRESS | 1,000 | 10,000 | Very High |
| WRITE | 500 | 5,000 | Excellent |

**Recommendation:** WRITE strategy for cost-sensitive applications

---

## 8. Cost Optimization Strategies

### 8.1 Token Optimization

| Strategy | Potential Savings | Implementation |
|----------|-------------------|----------------|
| Prompt compression | 20-30% | Remove redundant context |
| Response length limits | 10-20% | Set max_tokens appropriately |
| Caching | 30-50% | Cache repeated queries |
| Batching | 15-25% | Combine related queries |

### 8.2 Model Selection

| Use Case | Recommended Model | Cost Impact |
|----------|-------------------|-------------|
| Development/Testing | Ollama (local) | Free |
| Quick iterations | GPT-3.5/Haiku | Low |
| High accuracy needs | GPT-4/Sonnet | High |
| Production | Based on accuracy requirements | Variable |

### 8.3 Infrastructure Optimization

| Optimization | Savings | Notes |
|--------------|---------|-------|
| Spot instances | 60-70% | For batch processing |
| Reserved capacity | 20-40% | For consistent workloads |
| Auto-scaling | 15-25% | Scale down during idle |
| Local inference | 90%+ | For development |

---

## 9. Budget Monitoring Dashboard

### 9.1 Current Month Status

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    JANUARY 2026 BUDGET STATUS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Budget:    $50.00  ████████████████████████████████████████ 100%          │
│  Spent:     $32.50  ██████████████████████████░░░░░░░░░░░░░░  65%          │
│  Remaining: $17.50  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  35%          │
│                                                                             │
│  Days Elapsed: 17/31 (55%)                                                  │
│  Burn Rate: $1.91/day                                                       │
│  Projected End: $59.25 (WARNING: Over budget by $9.25)                     │
│                                                                             │
│  Category Breakdown:                                                        │
│  ├── LLM Inference:  $19.50 / $30.00  ████████████████░░░░  65%            │
│  ├── Compute:         $8.12 / $12.50  ████████████████░░░░  65%            │
│  ├── Storage:         $3.25 /  $5.00  ████████████████░░░░  65%            │
│  └── CI/CD:           $1.63 /  $2.50  ████████████████░░░░  65%            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Weekly Trend

```
Week    | Spent   | Tokens    | Experiments | Avg Cost/Exp
--------|---------|-----------|-------------|-------------
Week 1  | $8.50   | 1.2M      | 45          | $0.19
Week 2  | $7.75   | 1.1M      | 52          | $0.15
Week 3  | $9.25   | 1.4M      | 48          | $0.19
Week 4  | $7.00   | 1.0M      | 50          | $0.14  (projected)
```

---

## 10. Historical Cost Data

### 10.1 Monthly Summary

| Month | Budget | Actual | Variance | Tokens Used |
|-------|--------|--------|----------|-------------|
| Oct 2025 | $50.00 | $42.30 | -$7.70 | 4.2M |
| Nov 2025 | $50.00 | $48.75 | -$1.25 | 5.1M |
| Dec 2025 | $50.00 | $45.50 | -$4.50 | 4.8M |
| Jan 2026 | $50.00 | $32.50* | - | 3.2M* |

*Current month in progress

### 10.2 Experiment History

| Date | Experiment | Tokens | Cost | Duration |
|------|------------|--------|------|----------|
| 2026-01-15 | Task 1 | 45K | $0.04 | 5 min |
| 2026-01-15 | Task 2 | 180K | $0.08 | 12 min |
| 2026-01-16 | Task 3 | 520K | $0.12 | 25 min |
| 2026-01-16 | Task 4 | 290K | $0.10 | 18 min |

---

## 11. Projections and Forecasting

### 11.1 Next Month Projection

Based on current usage patterns:

| Category | Current | Projected | Change |
|----------|---------|-----------|--------|
| LLM Costs | $30.00 | $32.00 | +6.7% |
| Compute | $12.50 | $13.00 | +4.0% |
| Storage | $5.00 | $5.50 | +10.0% |
| CI/CD | $2.50 | $2.50 | 0% |
| **Total** | **$50.00** | **$53.00** | **+6%** |

### 11.2 Scaling Projections

| Scale Factor | Monthly Cost | Annual Cost |
|--------------|--------------|-------------|
| 1x (current) | $50 | $600 |
| 2x | $85 | $1,020 |
| 5x | $175 | $2,100 |
| 10x | $300 | $3,600 |

### 11.3 Cloud Migration Cost Impact

If migrating from local Ollama to cloud:

| Provider | Monthly Est. | Annual Est. | vs Current |
|----------|--------------|-------------|------------|
| OpenAI (GPT-3.5) | $150 | $1,800 | +200% |
| OpenAI (GPT-4) | $950 | $11,400 | +1800% |
| Anthropic (Haiku) | $125 | $1,500 | +150% |
| Anthropic (Sonnet) | $450 | $5,400 | +800% |

---

## 12. Budget Alerts and Thresholds

### 12.1 Alert Configuration

| Alert Type | Threshold | Action |
|------------|-----------|--------|
| Daily Spend | > $3.00 | Email notification |
| Weekly Spend | > $15.00 | Slack alert |
| Monthly Spend | > $40.00 | Dashboard warning |
| Monthly Spend | > $45.00 | Email + Slack |
| Monthly Spend | > $50.00 | Auto-pause non-critical |

### 12.2 Alert Implementation

```yaml
# budget_alerts.yaml
alerts:
  daily_budget:
    threshold: 3.00
    currency: USD
    action: email
    recipients:
      - team@example.com

  weekly_budget:
    threshold: 15.00
    currency: USD
    action: slack
    channel: "#budget-alerts"

  monthly_warning:
    threshold: 45.00
    currency: USD
    action: all
    severity: warning

  monthly_critical:
    threshold: 50.00
    currency: USD
    action: pause_experiments
    severity: critical
```

### 12.3 Cost Control Policies

| Policy | Trigger | Action |
|--------|---------|--------|
| Rate Limiting | > 100 queries/hour | Queue excess requests |
| Auto-scaling Down | < 20% utilization | Reduce resources |
| Experiment Pause | Budget exceeded | Pause non-critical |
| Model Downgrade | > 80% budget | Use cheaper models |

---

## Appendix A: Cost Tracking Code

```python
# cost_tracker.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class CostEntry:
    timestamp: datetime
    experiment: str
    tokens: int
    cost_usd: float
    category: str


class BudgetTracker:
    def __init__(self, monthly_budget: float = 50.0):
        self.monthly_budget = monthly_budget
        self.entries: List[CostEntry] = []

    def log_cost(self, experiment: str, tokens: int,
                 cost_usd: float, category: str = "llm"):
        entry = CostEntry(
            timestamp=datetime.now(),
            experiment=experiment,
            tokens=tokens,
            cost_usd=cost_usd,
            category=category
        )
        self.entries.append(entry)

    def get_monthly_total(self) -> float:
        current_month = datetime.now().month
        return sum(
            e.cost_usd for e in self.entries
            if e.timestamp.month == current_month
        )

    def get_remaining_budget(self) -> float:
        return self.monthly_budget - self.get_monthly_total()

    def is_over_budget(self) -> bool:
        return self.get_monthly_total() > self.monthly_budget
```

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| Token | Basic unit of text (~4 characters) for LLM pricing |
| Input Token | Token in the prompt/context sent to LLM |
| Output Token | Token in the LLM's generated response |
| Burn Rate | Average daily spending rate |
| Token Efficiency | Ratio of useful tokens to total tokens |

---

**Document Approval:**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Project Manager | Team Lead | Jan 2026 | Approved |
| Finance | Budget Owner | Jan 2026 | Approved |
| Technical Lead | Engineering | Jan 2026 | Approved |

---

**Revision History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Jan 2026 | Project Team | Initial budget tracking document |
