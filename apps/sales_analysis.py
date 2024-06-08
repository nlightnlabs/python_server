import pandas as pd
import numpy as np
from .getData import getData
import json

def main():

    arugments = {
        "table": "opportunities",
        "dbName": "bes"
    }
    data = getData(json.dumps(arugments))
    data = json.loads(data)
    data = pd.DataFrame(data)
    
    overall_summary = [
        {"title": "Number of Items","value": int(data["item_name"].nunique())},
        {"title": "Total Value","value": float(data["value"].sum())},
        {"title": "Quantity In Stock","value": int(data["quantity_in_stock"].sum())},
        {"title": "Average DIO","value": float(data["days_in_inventory"].mean())},
        {"title": "Average Lead Time","value": float(data["lead_time"].mean())},
        {"title": "Total Suppliers","value": int(data["supplier"].nunique())},
        {"title": "Total Contracts","value": int(data["contract"].nunique())}
    ]

    category_summary = [
        {"title": "Category","list": list(data.groupby('category').groups.keys())},
        {"title": "Total Value","list": data.groupby('category')["value"].sum().tolist()},
        {"title": "Number of Items","list": data.groupby('category')["item_name"].nunique().tolist()},        
        {"title": "Quantity In Stock","list": data.groupby('category')["quantity_in_stock"].sum().tolist()},
        {"title": "Average DIO","list": data.groupby('category')["days_in_inventory"].mean().tolist()},
        {"title": "Average Lead Time","list": data.groupby('category')["lead_time"].mean().tolist()},
        {"title": "Total Suppliers","list": data.groupby('category')["supplier"].nunique().tolist()},
        {"title": "Total Contracts","list": data.groupby('category')["contract"].nunique().tolist()}
    ]

    subcategory_summary = [
        {"title": "Subcategory","list": list(data.groupby('subcategory').groups.keys())},
        {"title": "Total Value","list": data.groupby('subcategory')["value"].sum().tolist()},
        {"title": "Number of Items","list": data.groupby('subcategory')["item_name"].nunique().tolist()},        
        {"title": "Quantity In Stock","list": data.groupby('subcategory')["quantity_in_stock"].sum().tolist()},
        {"title": "Average DIO","list": data.groupby('subcategory')["days_in_inventory"].mean().tolist()},
        {"title": "Average Lead Time","list": data.groupby('subcategory')["lead_time"].mean().tolist()},
        {"title": "Total Suppliers","list": data.groupby('subcategory')["supplier"].nunique().tolist()},
        {"title": "Total Contracts","list": data.groupby('subcategory')["contract"].nunique().tolist()}
    ]

    item_summary = [
        {"title": "Item","list": list(data.groupby('item_name').groups.keys())},
        {"title": "Total Value","list": data.groupby('item_name')["value"].sum().tolist()},
        {"title": "Number of Items","list": data.groupby('item_name')["item_name"].nunique().tolist()},        
        {"title": "Quantity In Stock","list": data.groupby('item_name')["quantity_in_stock"].sum().tolist()},
        {"title": "Average DIO","list": data.groupby('item_name')["days_in_inventory"].mean().tolist()},
        {"title": "Average Lead Time","list": data.groupby('item_name')["lead_time"].mean().tolist()},
        {"title": "Total Suppliers","list": data.groupby('item_name')["supplier"].nunique().tolist()},
        {"title": "Total Contracts","list": data.groupby('item_name')["contract"].nunique().tolist()}
    ]

    supplier_summary = [
        {"title": "Supplier","list": list(data.groupby('supplier').groups.keys())},
        {"title": "Total Value","list": data.groupby('supplier')["value"].sum().tolist()},
        {"title": "Number of Items","list": data.groupby('supplier')["item_name"].nunique().tolist()},        
        {"title": "Quantity In Stock","list": data.groupby('supplier')["quantity_in_stock"].sum().tolist()},
        {"title": "Average DIO","list": data.groupby('supplier')["days_in_inventory"].mean().tolist()},
        {"title": "Average Lead Time","list": data.groupby('supplier')["lead_time"].mean().tolist()},
        {"title": "Total Suppliers","list": data.groupby('supplier')["supplier"].nunique().tolist()},
        {"title": "Total Contracts","list": data.groupby('supplier')["contract"].nunique().tolist()}
    ]

    result = json.dumps({
        "data": [
            {"title": "Overall Summary", "data": overall_summary, "chart_type": "label"},
            {"title": "Category Summary", "data": category_summary, "chart_type": "bar"},
            {"title": "Subcategory Summary", "data": subcategory_summary, "chart_type": "bar"},
            {"title": "Item Summary", "data": item_summary, "chart_type": "bar"},
            {"title": "Supplier Summary", "data": supplier_summary, "chart_type": "bar"}
        ]
    })

    print(result)

main()