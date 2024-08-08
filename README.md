# Market Basket Analysis: Apriori and FP-Growth Algorithms

## Project Overview
This project focuses on applying market basket analysis techniques to uncover frequent itemsets within transactional data. The primary goal is to understand customer behavior and derive actionable insights to optimize business strategies. To achieve this, the project employs the Apriori and FP-Growth algorithms, comparing their effectiveness in extracting valuable patterns from the data.

## Key Objectives
Implement the Apriori and FP-Growth algorithms for market basket analysis.
Evaluate the performance of both algorithms in terms of efficiency and accuracy.
Identify frequent itemsets and generate association rules to uncover customer buying patterns.
Provide actionable insights for businesses to improve product placement, marketing strategies, and customer satisfaction.
Methodology

## Data Acquisition and Preparation:
Utilized a Kaggle dataset containing nearly 10K transactions.
Preprocessed the data using PySpark to create a suitable format for analysis.

## Apriori Algorithm Implementation:
Calculated single item frequency counts to determine support.
Generated candidate item pairs and filtered based on a minimum support threshold.
Calculated confidence for frequent item pairs and filtered rules based on a minimum confidence threshold.
Addressed the limitations of the Apriori algorithm regarding candidate set generation and multiple database scans.

## FP-Growth Algorithm Implementation:
Created an FP-Growth model with specified minimum support and confidence thresholds.
Fitted the model to the preprocessed data to extract frequent itemsets.
Exported frequent itemsets to a CSV file for further analysis.
Generated predictions using association rules derived from frequent itemsets.

## Results and Findings
Both Apriori and FP-Growth algorithms effectively identified frequent itemsets.
FP-Growth demonstrated superior efficiency in handling large datasets.
PySpark significantly improved computational performance and scalability.
Insights from frequent itemsets can be used to optimize product placement, marketing campaigns, and customer targeting.

This project successfully applied market basket analysis techniques to uncover valuable insights from transactional data. The findings highlight the importance of employing efficient algorithms like FP-Growth for large datasets. The derived knowledge can be leveraged by businesses to enhance their decision-making processes and improve overall performance.
