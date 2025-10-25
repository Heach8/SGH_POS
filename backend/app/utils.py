from decimal import Decimal
from typing import List, Dict, Any
from lxml import etree
from .settings import settings

def apply_campaigns(cart: List[Dict[str, Any]], campaigns: List[Dict[str, Any]]):
    lines = []
    gross = Decimal("0")
    discount = Decimal("0")
    for item in cart:
        qty = Decimal(str(item["qty"]))
        unit = Decimal(str(item["unit_price"]))
        brand = item.get("brand","")
        product_id = item.get("product_id","")
        line_gross = qty * unit
        line_disc = Decimal("0")
        applied_id = ""

        for c in campaigns:
            if not c.get("is_active", True):
                continue
            if c.get("brand") and c["brand"] != brand:
                continue
            if c.get("product_id") and c["product_id"] != product_id:
                continue
            min_qty = Decimal(str(c.get("min_qty",1)))
            min_amount = Decimal(str(c.get("min_amount",0)))
            if qty < min_qty and line_gross < min_amount:
                continue
            ctype = c["type"]
            if ctype == "PercentOff":
                percent = Decimal(str(c.get("percent",0))) / Decimal("100")
                disc = (line_gross * percent)
                if disc > line_disc: line_disc = disc; applied_id = c.get("id","")
            elif ctype == "FlatAmount":
                amt = Decimal(str(c.get("amount_off",0)))
                if line_gross >= min_amount and amt > line_disc: line_disc = amt; applied_id = c.get("id","")
            elif ctype == "BuyXPayY":
                x = int(c.get("min_qty",3)); y = max(1, x-1)
                if qty >= x:
                    free_units = qty - (qty // x) * y
                    disc = free_units * unit
                    if disc > line_disc: line_disc = disc; applied_id = c.get("id","")
        net = line_gross - line_disc
        gross += line_gross
        discount += line_disc
        lines.append({**item,"applied_campaign_id": applied_id,"line_gross": float(line_gross),"discount": float(line_disc),"line_net": float(net)})
    net_total = gross - discount
    return lines, float(gross), float(discount), float(net_total)

def xml_for_sale(sale: dict, lines: List[dict], payments: List[dict]) -> bytes:
    NS = settings.XML_NAMESPACE
    nsmap = {None: NS}
    root = etree.Element("SaleInvoice", nsmap=nsmap)
    header = etree.SubElement(root, "Header")
    etree.SubElement(header, "SaleID").text = sale["id"]
    etree.SubElement(header, "StoreID").text = sale["store_id"]
    etree.SubElement(header, "SalespersonID").text = sale["salesperson_id"]
    etree.SubElement(header, "Date").text = sale["date"]
    lines_el = etree.SubElement(root, "Lines")
    for ln in lines:
        l = etree.SubElement(lines_el, "Line")
        etree.SubElement(l, "LineID").text = str(ln["id"])
        etree.SubElement(l, "ProductID").text = ln["product_id"]
        etree.SubElement(l, "Qty").text = str(ln["qty"])
        etree.SubElement(l, "UnitPrice").text = str(ln["unit_price"])
        etree.SubElement(l, "Discount").text = str(ln["discount_amount"])
        etree.SubElement(l, "Net").text = str(ln["line_amount"])
        if ln.get("applied_campaign_id"):
            etree.SubElement(l, "AppliedCampaignID").text = ln["applied_campaign_id"]
    pays_el = etree.SubElement(root, "Payments")
    for p in payments:
        el = etree.SubElement(pays_el, "Payment")
        etree.SubElement(el, "Type").text = p["type"]
        etree.SubElement(el, "Amount").text = str(p["amount"])
        if p.get("reference"): etree.SubElement(el, "Reference").text = p["reference"]
    totals_el = etree.SubElement(root, "Totals")
    etree.SubElement(totals_el, "Gross").text = str(sale["gross_total"])
    etree.SubElement(totals_el, "DiscountTotal").text = str(sale["discount_total"])
    etree.SubElement(totals_el, "Net").text = str(sale["net_total"])
    etree.SubElement(root, "Status").text = "AwaitingSAPInfo"
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")