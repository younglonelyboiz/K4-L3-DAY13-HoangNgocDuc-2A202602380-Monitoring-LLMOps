import json
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdates

def draw_dashboard():
    log_file = "data/logs.jsonl"
    if not os.path.exists(log_file):
        print(f"File {log_file} not found!")
        return

    data = []
    with open(log_file, "r") as f:
        for line in f:
            if not line.strip(): continue
            data.append(json.loads(line))

    df = pd.DataFrame(data)
    
    # Filter for response_sent and request_failed to calculate metrics
    df['ts'] = pd.to_datetime(df['ts'])
    df = df.sort_values('ts')
    df.set_index('ts', inplace=True)

    requests = df[df['event'].isin(['request_received'])]
    responses = df[df['event'].isin(['response_sent', 'request_failed'])]
    
    # Resample per minute or 10 seconds based on data range
    time_agg = '10S'
    
    # 1. Error Rate
    errors = df[df['event'] == 'request_failed'].resample(time_agg).size()
    total = requests.resample(time_agg).size()
    error_rate = (errors / total).fillna(0) * 100

    # 2. Latency (p95, p99)
    latency_df = df[df['event'] == 'response_sent']['latency_ms'].dropna()
    p95 = latency_df.resample(time_agg).quantile(0.95).fillna(0)
    p99 = latency_df.resample(time_agg).quantile(0.99).fillna(0)

    # 3. Request Count
    req_count = requests.resample(time_agg).size()

    # 4. Token Usage
    tokens = df[df['event'] == 'response_sent'][['tokens_in', 'tokens_out']].dropna()
    tokens_in = tokens['tokens_in'].resample(time_agg).sum()
    tokens_out = tokens['tokens_out'].resample(time_agg).sum()

    # 5. Cost
    cost = df[df['event'] == 'response_sent']['cost_usd'].dropna()
    cost_total = cost.resample(time_agg).sum()

    # 6. Cache Hit Ratio (Mocked as 0 for this lab since cache is not implemented)
    cache_hits = pd.Series(0, index=req_count.index)
    
    # Plotting
    fig, axs = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle('LLMOps Monitoring Dashboard', fontsize=16)

    # Panel 1: Request Count
    axs[0, 0].bar(req_count.index, req_count.values, width=0.0001, color='blue')
    axs[0, 0].set_title('Request Count')
    axs[0, 0].set_ylabel('Count')

    # Panel 2: Error Rate
    axs[0, 1].plot(error_rate.index, error_rate.values, color='red', marker='o')
    axs[0, 1].axhline(y=5, color='r', linestyle='--', label='SLO < 5%')
    axs[0, 1].set_title('Error Rate (%)')
    axs[0, 1].set_ylabel('%')
    axs[0, 1].legend()

    # Panel 3: Latency
    axs[1, 0].plot(p95.index, p95.values, color='orange', label='p95')
    axs[1, 0].plot(p99.index, p99.values, color='red', label='p99')
    axs[1, 0].axhline(y=2000, color='r', linestyle='--', label='SLO < 2000ms')
    axs[1, 0].set_title('Latency (ms)')
    axs[1, 0].set_ylabel('ms')
    axs[1, 0].legend()

    # Panel 4: Token Usage
    axs[1, 1].bar(tokens_in.index, tokens_in.values, width=0.0001, label='Input Tokens', color='lightblue')
    axs[1, 1].bar(tokens_out.index, tokens_out.values, width=0.0001, bottom=tokens_in.values, label='Output Tokens', color='navy')
    axs[1, 1].set_title('Token Usage')
    axs[1, 1].legend()

    # Panel 5: Cost
    axs[2, 0].plot(cost_total.index, cost_total.values, color='green', marker='o')
    axs[2, 0].set_title('Cost (USD)')
    axs[2, 0].set_ylabel('USD')

    # Panel 6: Cache Hit Ratio
    axs[2, 1].plot(cache_hits.index, cache_hits.values, color='purple', marker='o')
    axs[2, 1].set_title('Cache Hit Ratio (%)')
    axs[2, 1].set_ylabel('%')
    axs[2, 1].set_ylim(-10, 100)

    for ax in axs.flat:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.tick_params(axis='x', rotation=45)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    out_file = "dashboard.png"
    plt.savefig(out_file)
    print(f"Dashboard saved successfully as {out_file}. Bạn hãy mở file này và chụp màn hình nhé!")

if __name__ == "__main__":
    draw_dashboard()
