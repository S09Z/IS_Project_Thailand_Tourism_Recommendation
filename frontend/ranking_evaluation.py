import numpy as np
from sklearn.metrics import ndcg_score
import matplotlib.pyplot as plt
import seaborn as sns

# ✅ คำนวณ NDCG@K
def calculate_ndcg(true_relevance, predicted_ranking, k=5):
    return ndcg_score([true_relevance], [predicted_ranking], k=k)

# ✅ Precision@K และ Recall@K
def precision_at_k(recommended, relevant, k):
    recommended_at_k = recommended[:k]
    return len(set(recommended_at_k) & set(relevant)) / k

def recall_at_k(recommended, relevant, k):
    recommended_at_k = recommended[:k]
    return len(set(recommended_at_k) & set(relevant)) / len(relevant)

# ✅ คำนวณ Mean Reciprocal Rank (MRR)
def mean_reciprocal_rank(results, relevant_items):
    mrr_score = 0
    for result in results:
        for idx, item in enumerate(result):
            if item in relevant_items:
                mrr_score += 1 / (idx + 1)
                break
    return mrr_score / len(results)

# ✅ ฟังก์ชัน Visualization
def plot_evaluation_metrics(metrics):
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(8, 5))
    
    metric_names = list(metrics.keys())
    metric_values = list(metrics.values())

    sns.barplot(x=metric_names, y=metric_values, palette="Blues", ax=ax)
    ax.set_ylabel("Score")
    ax.set_title("Ranking Recommendation Evaluation")
    plt.xticks(rotation=15)
    
    return fig  # ✅ ส่ง fig กลับเพื่อใช้ใน Streamlit
