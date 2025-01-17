import math
from collections import defaultdict
import sys


def read_qrels(qrels_file):
    relevance_dict = defaultdict(dict)
    with open(qrels_file, "r") as f:
        for line in f:
            topic_id, _, docno, judgment = line.split()
            topic_id = int(topic_id)
            relevance_dict[topic_id][docno] = int(judgment)
    return relevance_dict


def read_results(results_file):
    results_dict = defaultdict(list)
    improper_format = False

    with open(results_file, "r") as f:
        for line_num, line in enumerate(f, start=1):
            parts = line.split()
            if len(parts) != 6:
                improper_format = True
                continue

            topic_id, _, docno, rank, score, run_name = parts

            try:
                topic_id = int(topic_id)
                rank = int(rank)
                score = float(score)
            except ValueError:
                improper_format = True
                continue

            results_dict[topic_id].append((docno, rank, score))

        if improper_format:
            print(
                f"Warning: The file {results_file} is improperly formatted and will not be analyzed."
            )
            return None

        for topic in results_dict:
            results_dict[topic] = sorted(
                results_dict[topic], key=lambda x: (-x[2], x[0])
            )

    return results_dict


def compute_precision_at_k(relevance_dict, results_dict, k=10):
    precision_at_k = {}
    for topic, docs in results_dict.items():
        relevant_count = 0
        for i, (docno, _, _) in enumerate(docs[:k]):
            if (
                docno in relevance_dict.get(topic, {})
                and relevance_dict[topic][docno] > 0
            ):
                relevant_count += 1
        precision_at_k[topic] = relevant_count / k
    return precision_at_k


def compute_average_precision(relevance_dict, results_dict):
    average_precision = {}
    for topic, docs in results_dict.items():
        relevant_docs = relevance_dict.get(topic, {})
        num_relevant = sum(1 for judgment in relevant_docs.values() if judgment > 0)
        if num_relevant == 0:
            average_precision[topic] = 0
            continue

        num_hits = 0
        ap_sum = 0.0
        for i, (docno, rank, _) in enumerate(docs[:1000]):  # consider top 1000
            if docno in relevant_docs and relevant_docs[docno] > 0:
                num_hits += 1
                ap_sum += num_hits / (i + 1)

        average_precision[topic] = ap_sum / num_relevant if num_relevant > 0 else 0
    return average_precision


def compute_dcg(relevance_list):
    dcg = 0.0
    for i, rel in enumerate(relevance_list):
        if rel > 0:
            dcg += rel / math.log2(i + 2)
    return dcg


def compute_ndcg(relevance_dict, results_dict, k=10):
    ndcg = {}
    for topic, docs in results_dict.items():
        relevance_list = [
            relevance_dict[topic].get(docno, 0) for docno, _, _ in docs[:k]
        ]
        dcg = compute_dcg(relevance_list)

        ideal_relevance_list = sorted(
            [rel for rel in relevance_dict[topic].values() if rel > 0], reverse=True
        )[:k]
        idcg = compute_dcg(ideal_relevance_list)

        ndcg[topic] = dcg / idcg if idcg > 0 else 0
    return ndcg


def main(qrels_file, results_file, output_file):
    relevance_dict = read_qrels(qrels_file)
    results_dict = read_results(results_file)

    precision_at_10 = compute_precision_at_k(relevance_dict, results_dict, k=10)
    average_precision = compute_average_precision(relevance_dict, results_dict)
    ndcg_at_10 = compute_ndcg(relevance_dict, results_dict, k=10)
    ndcg_at_1000 = compute_ndcg(relevance_dict, results_dict, k=1000)

    with open(output_file, "w") as f:
        for topic in sorted(average_precision.keys()):
            f.write(
                f"ap                    \t{topic}\t{average_precision[topic]:.4f}\n"
            )
        for topic in sorted(ndcg_at_10.keys()):
            f.write(f"ndcg_cut_10            \t{topic}\t{ndcg_at_10[topic]:.4f}\n")
        for topic in sorted(ndcg_at_1000.keys()):
            f.write(f"ndcg_cut_1000          \t{topic}\t{ndcg_at_1000[topic]:.4f}\n")
        for topic in sorted(precision_at_10.keys()):
            f.write(f"P_10                   \t{topic}\t{precision_at_10[topic]:.4f}\n")
    print(f"Evaluation results written to {output_file}")

    mean_map = (
        sum(average_precision.values()) / len(average_precision)
        if average_precision
        else 0
    )
    mean_p10 = (
        sum(precision_at_10.values()) / len(precision_at_10) if precision_at_10 else 0
    )
    mean_ndcg10 = sum(ndcg_at_10.values()) / len(ndcg_at_10) if ndcg_at_10 else 0
    mean_ndcg1000 = (
        sum(ndcg_at_1000.values()) / len(ndcg_at_1000) if ndcg_at_1000 else 0
    )

    print("\nMean Evaluation Metrics:")
    print(f"Mean Average Precision (MAP): {mean_map:.4f}")
    print(f"Mean P@10: {mean_p10:.4f}")
    print(f"Mean NDCG@10: {mean_ndcg10:.4f}")
    print(f"Mean NDCG@1000: {mean_ndcg1000:.4f}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python evaluate.py <qrels_file> <results_file> <output_file>")
        sys.exit(1)

    qrels_file = sys.argv[1]
    results_file = sys.argv[2]
    output_file = sys.argv[3]
    main(qrels_file, results_file, output_file)
