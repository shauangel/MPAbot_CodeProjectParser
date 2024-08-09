from pymongo import MongoClient
from collections import Counter
import csv

client = MongoClient("mongodb://localhost:50004/")
DB = client['CPService']
POSTS_COLLECTION = DB['Posts']


if __name__ == "__main__":
    data = [p for p in POSTS_COLLECTION.find()]
    real_num = Counter()
    for p in data:
        for ans in p['answers']:
            reputation = ans['user_reputation']
            real_num[reputation] += 1

    # Calculate percentiles for each element
    percentiles = []
    count = 0
    total_count = sum(real_num.values())
    print(total_count)
    keys = []
    values = []
    for item, item_count in sorted(real_num.items(), reverse=False):
        # Calculate the current percentile based on the cumulative count
        count += item_count
        percentile = (count / total_count) * 100
        percentiles.append(percentile)
        keys.append(item)
        values.append(item_count)

    with open('reputation_range.csv', 'w') as csvfile:
        fieldnames = ['Score', 'count', 'percentile']
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        for item, item_count, percentile in zip(keys, values, percentiles):
            #print(f"Item: {item}, Count: {item_count}, Percentile: {percentile:.2f}%")
            writer.writerow([item, item_count, percentile])






