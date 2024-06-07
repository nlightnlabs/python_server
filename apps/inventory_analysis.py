import pandas as pd
import numpy as np
from getData import getData
import json

def summary():

    data = getData(table="inventory_items", dbName="bes")
    data = json.loads(data)
    data = pd.DataFrame(data)
    
    overall_summary = {
        "number_of_items": int(data["item_name"].nunique()),
        "total_value": float(data["value"].sum()),
        "quantity_in_stock": int(data["quantity_in_stock"].sum()),
        "average_dio": float(data["days_in_inventory"].mean()),
        "average_lead_time": float(data["lead_time"].mean()),
        "total_suppliers": int(data["supplier"].nunique()),
        "total_contracts": int(data["supplier"].nunique())
    }
    
    category_summary = {
        "category": list(data.groupby('category').groups.keys()),
        "number_of_items": data.groupby('category')["item_name"].nunique().tolist(),
        "quantity_in_stock": data.groupby('category')["quantity_in_stock"].sum().tolist(),
        "average_dio": data.groupby('category')["days_in_inventory"].mean().tolist(),
        "average_lead_time": data.groupby('category')["lead_time"].mean().tolist(), 
        "total_value": data.groupby('category')["value"].sum().tolist(), 
        "number_of_suppliers": data.groupby('category')["supplier"].nunique().tolist(), 
        "number_of_contracts": data.groupby('category')["contract"].nunique().tolist()
    }

    subcategory_summary = {
       "category": list(data.groupby('category').groups.keys()),
        "number_of_items": data.groupby('category')["item_name"].nunique().tolist(),
        "quantity_in_stock": data.groupby('category')["quantity_in_stock"].sum().tolist(),
        "average_dio": data.groupby('category')["days_in_inventory"].mean().tolist(),
        "average_lead_time": data.groupby('category')["lead_time"].mean().tolist(), 
        "total_value": data.groupby('category')["value"].sum().tolist(), 
        "number_of_suppliers": data.groupby('category')["supplier"].nunique().tolist(), 
        "number_of_contracts": data.groupby('category')["contract"].nunique().tolist()
    }

    item_summary = {
        "category": list(data.groupby('category').groups.keys()),
        "number_of_items": data.groupby('category')["item_name"].nunique().tolist(),
        "quantity_in_stock": data.groupby('category')["quantity_in_stock"].sum().tolist(),
        "average_dio": data.groupby('category')["days_in_inventory"].mean().tolist(),
        "average_lead_time": data.groupby('category')["lead_time"].mean().tolist(), 
        "total_value": data.groupby('category')["value"].sum().tolist(), 
        "number_of_suppliers": data.groupby('category')["supplier"].nunique().tolist(), 
        "number_of_contracts": data.groupby('category')["contract"].nunique().tolist()
    }

    supplier_summary = {
       "category": list(data.groupby('category').groups.keys()),
        "number_of_items": data.groupby('category')["item_name"].nunique().tolist(),
        "quantity_in_stock": data.groupby('category')["quantity_in_stock"].sum().tolist(),
        "average_dio": data.groupby('category')["days_in_inventory"].mean().tolist(),
        "average_lead_time": data.groupby('category')["lead_time"].mean().tolist(), 
        "total_value": data.groupby('category')["value"].sum().tolist(), 
        "number_of_suppliers": data.groupby('category')["supplier"].nunique().tolist(), 
        "number_of_contracts": data.groupby('category')["contract"].nunique().tolist()
    }


    result = json.dumps({
        "overall_summary":overall_summary,
        "category_summary": category_summary,
        "subcategory_summary": subcategory_summary,
        "item_summary": item_summary,
        "supplier_summary": supplier_summary
    })

    return result

summary()