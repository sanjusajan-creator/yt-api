"""
Response Formatter Utilities
Formats API responses in different formats (JSON, XML, CSV)
"""
from typing import Dict, Any, List
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import csv
from io import StringIO


def format_json(data: Any, pretty: bool = True) -> str:
    """Format data as JSON"""
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)


def dict_to_xml(data: Dict[str, Any], root_name: str = "response") -> str:
    """Convert dictionary to XML string"""
    
    def build_xml(parent: ET.Element, data: Any):
        if isinstance(data, dict):
            for key, value in data.items():
                # Sanitize key name for XML
                key = str(key).replace(" ", "_")
                child = ET.SubElement(parent, key)
                build_xml(child, value)
        elif isinstance(data, list):
            for item in data:
                item_elem = ET.SubElement(parent, "item")
                build_xml(item_elem, item)
        else:
            parent.text = str(data) if data is not None else ""
    
    root = ET.Element(root_name)
    build_xml(root, data)
    
    # Pretty print
    xml_str = ET.tostring(root, encoding='unicode')
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent="  ")


def list_to_csv(data: List[Dict[str, Any]]) -> str:
    """Convert list of dictionaries to CSV string"""
    if not data:
        return ""
    
    output = StringIO()
    
    # Get all unique keys from all dictionaries
    all_keys = set()
    for item in data:
        all_keys.update(flatten_dict(item).keys())
    
    fieldnames = sorted(all_keys)
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for item in data:
        flattened = flatten_dict(item)
        writer.writerow(flattened)
    
    return output.getvalue()


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert list to comma-separated string
            items.append((new_key, ', '.join(str(x) for x in v)))
        else:
            items.append((new_key, v))
    return dict(items)


def format_response(data: Any, format_type: str = "json", pretty: bool = True) -> str:
    """
    Format response data in the specified format
    
    Args:
        data: Data to format
        format_type: Output format (json, xml, csv)
        pretty: Whether to prettify output
    
    Returns:
        Formatted string
    """
    format_type = format_type.lower()
    
    if format_type == "json":
        return format_json(data, pretty)
    
    elif format_type == "xml":
        if isinstance(data, dict):
            return dict_to_xml(data)
        elif isinstance(data, list):
            return dict_to_xml({"items": data}, "response")
        else:
            return dict_to_xml({"value": data}, "response")
    
    elif format_type == "csv":
        if isinstance(data, list):
            return list_to_csv(data)
        elif isinstance(data, dict):
            return list_to_csv([data])
        else:
            return str(data)
    
    else:
        # Default to JSON
        return format_json(data, pretty)
