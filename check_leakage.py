"""
Check for evaluation leakage in TF-IDF recommendations.
"""
import pandas as pd
import numpy as np
from src.models.tfidf import TfidfRecommender

# Load data
items = pd.read_csv('data/processed/items.csv')
train = pd.read_csv('data/processed/train.csv')
test = pd.read_csv('data/processed/test.csv')

# Filter to OULAD
items = items[items['item_id'].str.startswith('oulad_', na=False)]
train = train[train['item_id'].str.startswith('oulad_', na=False)]
test = test[test['item_id'].str.startswith('oulad_', na=False)]

# Fit TF-IDF
tfidf = TfidfRecommender()
tfidf.fit(items)

# Sample evaluation
item_lookup = items.set_index('item_id')
k = 10
leakage_count = 0
total_users = 0
train_item_recommendations = []
test_overlap_stats = []

for user_id in test['user_id'].unique()[:200]:  # Sample 200 users
    user_train = train[train['user_id'] == user_id]
    user_test = test[test['user_id'] == user_id]
    
    if len(user_train) == 0 or len(user_test) == 0:
        continue
    
    total_users += 1
    
    # Check train-test item overlap
    train_items_set = set(user_train['item_id'].tolist())
    test_items_set = set(user_test['item_id'].tolist())
    overlap = train_items_set & test_items_set
    test_overlap_stats.append(len(overlap) / len(test_items_set) if len(test_items_set) > 0 else 0)
    
    # Build query from training (as in evaluation code)
    train_items = user_train['item_id'].tolist()
    goal_text = " ".join(
        item_lookup.loc[item_id, "title"]
        for item_id in train_items[:3]
        if item_id in item_lookup.index
    )
    
    if not goal_text.strip():
        continue
    
    # Get recommendations
    recs_df = tfidf.recommend(goal_text, k=k)
    recs = set(recs_df['item_id'].tolist())
    
    # Check how many recommendations are training items
    train_overlap = recs & train_items_set
    train_item_recommendations.append(len(train_overlap))
    
    if len(train_overlap) > 0:
        leakage_count += 1

print("=" * 60)
print("EVALUATION LEAKAGE ANALYSIS")
print("=" * 60)
print(f"\nUsers evaluated: {total_users}")
print(f"Users with training items in recommendations: {leakage_count} ({leakage_count/total_users*100:.1f}%)")
print(f"Average training items per recommendation list: {np.mean(train_item_recommendations):.2f}")
print(f"Max training items in a recommendation list: {max(train_item_recommendations) if train_item_recommendations else 0}")

print(f"\nTrain-Test Item Overlap:")
print(f"  Average overlap ratio: {np.mean(test_overlap_stats)*100:.1f}%")
print(f"  Users with >50% overlap: {(np.array(test_overlap_stats) > 0.5).sum()}/{len(test_overlap_stats)}")
print(f"  Users with 100% overlap: {(np.array(test_overlap_stats) == 1.0).sum()}/{len(test_overlap_stats)}")

print("\n" + "=" * 60)
print("CONCLUSION:")
if np.mean(test_overlap_stats) > 0.5:
    print("⚠️  HIGH LEAKAGE DETECTED!")
    print("   Users interact with same items in train and test.")
    print("   TF-IDF recommends training items, which appear in test.")
    print("   This inflates NDCG scores artificially.")
else:
    print("✓ Low overlap detected. Leakage may be from other sources.")
