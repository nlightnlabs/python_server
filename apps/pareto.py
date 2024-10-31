
from flask import Flask, jsonify, request, render_template
import pandas as pd
import numpy as np
import seaborn as sns


class ParetoAnalysis:

  def __init__(self, data, feature = "category", aggregation_method = "count", groupTail = True, tailThreshold = 0.8, barLabelsFieldName ="category", barDataFieldName ="value"):
    self.data=data
    self.feature=feature
    self.aggregation_method=aggregation_method
    self.groupTail=groupTail
    self.tailThreshold=tailThreshold
    self.barLabelsFieldName=barLabelsFieldName
    self.barDataFieldName=barDataFieldName
    self.analysis = self.analyze()


  def abbreviate_value(self, value):
    multipliers = [
        {"threshold": 1000000000000, "divisor": 1/1000000000000, "suffix": "T", "digits": 1},
        {"threshold": 1000000000, "divisor": 1/1000000000, "suffix": "B", "digits": 1},
        {"threshold": 1000000, "divisor": 1/1000000, "suffix": "M", "digits": 1},
        {"threshold": 1000, "divisor": 1/1000, "suffix": "K", "digits": 1},
        {"threshold": 1, "divisor": 1, "suffix": "", "digits": 0},
        {"threshold": 0, "divisor": 1, "suffix": "", "digits": 2},
    ]
    formatted_value = [f'{round(value*row["divisor"],row["digits"])} {row["suffix"]}' for row in multipliers if np.abs(value) >= row["threshold"]][0]
    return formatted_value

  def analyze(self):
    data = self.data
    barLabelsFieldName = self.barLabelsFieldName
    barDataFieldName = self.barDataFieldName
    feature = self.feature

    pareto = pd.DataFrame(data[barLabelsFieldName].value_counts())
    if self.aggregation_method == "sum" or self.aggregation_method == "average" or self.aggregation_method == "median":
      pareto["Amount"] = data.groupby(barLabelsFieldName)[barDataFieldName].sum()
      pareto.sort_values(by="Amount", ascending=False, inplace=True)
      pareto["% of Total"] = pareto["amount"] / data[barDataFieldName].sum()
      pareto["Running Total"] = pareto["amount"].cumsum()
      pareto["Running % of Total"] = pareto["amount"].cumsum() / data[barDataFieldName].sum()
      pareto["Average"] = data.groupby(barLabelsFieldName)[barDataFieldName].mean()
      pareto["Avg vs Overall Avg"] = (pareto["Average"] - pareto["Average"].mean())/pareto["Average"].mean()
      pareto["Median"] = data.groupby(barLabelsFieldName)[barDataFieldName].median()
      pareto["Median vs Overall Median"] = lambda pareto: (pareto["Median"] - pareto["Median"].median())/pareto["Median"].median() if pareto["Median"].median() != 0 else 0
    else:
      pareto["Amount"] = data.groupby(barLabelsFieldName)[barDataFieldName].count()
      pareto["% of Total"] = pareto["Amount"]/data[barLabelsFieldName].count()
      pareto["Running Total"] = pareto["Amount"].cumsum()
      pareto["Running % of Total"] = pareto["Amount"].cumsum()/data[barLabelsFieldName].count()
      pareto["Average"] = None
      pareto["Avg vs Overall Avg"] = None
      pareto["Median"] = None
      pareto["Median vs Overall Median"] = None

    pareto.reset_index(feature,inplace=True)

    avg = pareto["Amount"].mean()
    std = pareto["Amount"].std()
    min_count = pareto["Amount"].min()
    max_count = pareto["Amount"].max()
    median = pareto["Amount"].quantile(.50)
    bottom_quartile = pareto["Amount"].quantile(0.25)
    top_quartile = pareto["Amount"].quantile(0.75)

    #Group Tail into a single element
    tailThreshold = 0.8
    top_items = pareto[pareto["Running % of Total"] <= tailThreshold]
    tail_items = pareto[pareto["Running % of Total"] > tailThreshold]
    number_of_top_items= top_items.shape[0]
    number_of_tail_items = tail_items.shape[0]
    total_items = pareto.shape[0]

    if self.aggregation_method != "count":
      tail_average = tail_items[pareto.columns[6]].mean()
      avg_vs_overall_avg = (tail_average - pareto["Average"].mean())/pareto["Average"].mean()
      tail_median = tail_items[pareto.columns[8]].median()
      median_vs_overall_median = lambda pareto: (tail_median - pareto["Median"].median())/pareto["Median"].median() if pareto["Median"].median() != 0 else 0
    else:
      tail_average = None
      avg_vs_overall_avg = None
      tail_median = None
      median_vs_overall_median = None

    total_tail = {
        feature: f'Other Tail {number_of_tail_items} items',
        "Count": tail_items[pareto.columns[1]].sum(),
        "Amount": tail_items[pareto.columns[2]].sum(),
        "% of Total": tail_items[pareto.columns[3]].sum(),
        "Running Total": tail_items[pareto.columns[4]].sum(),
        "Running % of Total": 1,
        "Average": tail_average,
        "Avg vs Overall Avg": avg_vs_overall_avg
    }
    total_tail = pd.DataFrame(total_tail, index=[0])

    pareto_with_tail = pd.concat([top_items, total_tail], axis=0, ignore_index=True)
    pct_of_total_value_with_top_items = round(top_items["% of Total"].sum(),2)
    pct_of_total_value_with_tail_items = round(tail_items["% of Total"].sum(),2)

    top_items_pct_of_total_items = round(number_of_top_items/total_items*100,2)
    tail_items_pct_of_total_items = round(number_of_tail_items/total_items*100,2)

    if self.subTitle is None:
      top_items_summary = f"{number_of_top_items} ({round(number_of_top_items/total_items*100,2)}%) make up the top {pct_of_total_value_with_top_items*100:0.1f}%"
    else:
      top_items_summary = self.subTitle

    tail_items_summary = f"{number_of_tail_items} ({round(number_of_tail_items/total_items*100,2)}%) make up the tail {pct_of_total_value_with_tail_items*100:0.1f}%"


    summary = {
      "feature":self.feature,
      "total_unique_items":total_items,
      "top_items_summary": top_items_summary,
      "tail_items_summary": tail_items_summary,
      "number_of_top_items":number_of_top_items,
      "number_of_tail_items":number_of_tail_items,
      "top_items_pct_of_total_items":top_items_pct_of_total_items,
      "tail_items_pct_of_total_items":tail_items_pct_of_total_items,
      "avg":avg,
      "std":std,
      "min_count":min_count,
      "max_min":max_count,
      "median":median,
      "bottom_quartile":bottom_quartile,
      "top_quartile":top_quartile,
      "full_pareto_table":pareto,
      "pareto_with_tail":pareto_with_tail,
      "top_items": top_items,
      "tail_items": tail_items,
      "total_tail": total_tail
    }

    return summary
    