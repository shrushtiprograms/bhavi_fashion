import os
import sys
import django

# Set up Django environment
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bhavi_fashion.settings')
# django.setup()

# project_root = os.path.dirname(os.path.abspath(__file__))  # Current script directory
# sys.path.append(os.path.join(project_root))  # Add current directory
# sys.path.append(os.path.dirname(project_root))  # Add parent directory (project root)
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bhavi_fashion.settings')  # Point to settings.py
# django.setup()

# project_root = os.path.dirname(os.path.abspath(__file__))  # Current script directory: G:\bhavi back 12.4\bhavi_fashion
# sys.path.insert(0, project_root)  # Add current directory at the start
# sys.path.insert(0, os.path.dirname(project_root))  # Should not be needed, but adding for clarity
# # Explicitly set the settings module to the inner bhavi_fashion directory
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bhavi_fashion.settings')  # Points to bhavi_fashion_extracted/bhavi_fashion/bhavi_fashion/settings.py
# django.setup()

# project_root = r"G:\bhavi back 12.4\bhavi_fashion"  # Absolute path to your project root
# sys.path.insert(0, project_root)  # Add project root at the start
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bhavi_fashion.settings')  # Inner settings.py
# django.setup()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bhavi_fashion.settings')
django.setup()

import os
import sys
from fpdf import FPDF
from datetime import datetime
from django.conf import settings
import django
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns
import argparse
from django.utils import timezone
from datetime import timedelta
from report_manager.models import Report  # Add
from accounts.models import User, Address
from orders.models import Order, OrderItem
from custom_designs.models import CustomDesign
from bulk_orders.models import BulkOrder
from products.models import Product, Category
from tailor_jobs.models import TailorApplication

class PDFReport(FPDF):
    def header(self):
        logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo.png')
        if os.path.exists(logo_path):
            self.image(logo_path, x=10, y=8, w=30)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Bhavi Fashion - Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Crafting Elegance, One Stitch at a Time', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def add_table(self, headers, data, col_widths, row_colors=None):
        self.set_fill_color(128, 0, 0)  # Maroon header
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 10)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, 1, 0, 'C', fill=True)
        self.ln()
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 10)
        for i, row in enumerate(data):
            if row_colors and row_colors[i]:
                self.set_fill_color(*row_colors[i])
                fill = True
            else:
                fill = False
            for j, item in enumerate(row):
                self.cell(col_widths[j], 10, str(item), 1, 0, 'L', fill=fill)
            self.ln()

def create_bar_chart(data, title, xlabel, ylabel, filename):
    plt.figure(figsize=(6, 4))
    labels, values = zip(*data.items())
    sns.barplot(x=list(values), y=list(labels), palette='viridis')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def create_pie_chart(data, title, filename):
    plt.figure(figsize=(6, 4))
    labels, values = zip(*data.items())
    plt.pie(values, labels=labels, autopct='%1.1f%%', colors=sns.color_palette('viridis'))
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def create_line_chart(data, title, xlabel, ylabel, filename):
    plt.figure(figsize=(6, 4))
    dates, values = zip(*sorted(data.items()))
    plt.plot(dates, values, marker='o', color='maroon')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def create_stacked_bar_chart(categories, in_stock, low_stock, title, filename):
    plt.figure(figsize=(6, 4))
    bar_width = 0.35
    x = range(len(categories))
    plt.bar(x, in_stock, bar_width, label='In Stock', color='green')
    plt.bar([i + bar_width for i in x], low_stock, bar_width, label='Low Stock', color='red')
    plt.xticks([i + bar_width/2 for i in x], categories, rotation=45)
    plt.title(title)
    plt.xlabel('Category')
    plt.ylabel('Count')
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def generate_order_report(output_path, days=None):
    pdf = PDFReport()
    # Cover page
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 20, 'Bhavi Fashion Order Report', 0, 1, 'C')
    logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo.png')
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=80, y=50, w=50)
    pdf.ln(60)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
    pdf.cell(0, 10, 'Prepared by: Bhavi Fashion Team', 0, 1, 'C')
    
    # Content
    pdf.add_page()
    pdf.chapter_title('Order Report')

    orders = Order.objects.all().select_related('user', 'shipping_address')
    if days:
        start_date = timezone.now() - timedelta(days=days)
        orders = orders.filter(created_at__gte=start_date)

    total_orders = len(orders)
    total_amount = sum(order.total_amount for order in orders)
    avg_amount = total_amount / total_orders if total_orders else 0
    status_counts = Counter(order.get_order_status_display() for order in orders)
    most_common_status = status_counts.most_common(1)[0][0] if status_counts else 'N/A'

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, f'Summary (Last {days} Days)' if days else 'Summary', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f'Total Orders: {total_orders}', 0, 1)
    pdf.cell(0, 8, f'Average Order Value: INR {avg_amount:.2f}', 0, 1)
    pdf.cell(0, 8, f'Most Common Status: {most_common_status}', 0, 1)
    pdf.ln(5)

    headers = ['Order #', 'User', 'Total Amount', 'Status', 'Date']
    data = []
    row_colors = []
    for order in orders:
        data.append([
            order.order_number,
            order.user.username,
            f"INR {order.total_amount:.2f}",
            order.get_order_status_display(),
            order.created_at.strftime('%Y-%m-%d')
        ])
        row_colors.append((255, 255, 200) if order.order_status == 'pending' else None)
    pdf.add_table(headers, data, [40, 40, 30, 30, 40], row_colors)

    if status_counts:
        chart_path = 'temp_order_chart.png'
        create_bar_chart(status_counts, 'Orders by Status', 'Count', 'Status', chart_path)
        pdf.ln(10)
        pdf.cell(0, 10, 'Order Status Distribution', 0, 1, 'L')
        pdf.image(chart_path, w=100)
        os.remove(chart_path)

    date_totals = Counter()
    for order in orders:
        date = order.created_at.strftime('%Y-%m-%d')
        date_totals[date] += order.total_amount
    if date_totals:
        chart_path = 'temp_order_trend_chart.png'
        create_line_chart(date_totals, 'Order Totals Over Time', 'Date', 'Total (INR)', chart_path)
        pdf.ln(10)
        pdf.cell(0, 10, 'Order Trends', 0, 1, 'L')
        pdf.image(chart_path, w=100)
        os.remove(chart_path)

    for order in orders:
        pdf.ln(5)
        pdf.chapter_title(f'Order #{order.order_number} Details')
        items = order.items.select_related('product', 'variant')
        headers = ['Product', 'Variant', 'Quantity', 'Price', 'Total']
        data = []
        for item in items:
            variant = item.variant.__str__() if item.variant else 'N/A'
            data.append([
                item.product.name,
                variant,
                item.quantity,
                f"INR {item.price:.2f}",
                f"INR {item.total:.2f}"
            ])
        pdf.add_table(headers, data, [50, 40, 20, 30, 30])

    pdf.output(output_path)
    report_name = os.path.basename(output_path)  # e.g., 'order_report.pdf'
    Report.objects.get_or_create(
        file_name=report_name,
    #    defaults={'description': f'Order report generated on {datetime.now().strftime("%Y-%m-%d")}'}
    )

def generate_custom_design_report(output_path, days=None):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 20, 'Bhavi Fashion Custom Design Report', 0, 1, 'C')
    logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo.png')
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=80, y=50, w=50)
    pdf.ln(60)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
    pdf.cell(0, 10, 'Prepared by: Bhavi Fashion Team', 0, 1, 'C')
    pdf.add_page()
    pdf.chapter_title('Custom Design Requests')

    designs = CustomDesign.objects.all().select_related('user')
    if days:
        start_date = timezone.now() - timedelta(days=days)
        designs = designs.filter(created_at__gte=start_date)

    total_designs = len(designs)
    total_budget = sum(design.budget for design in designs)
    avg_budget = total_budget / total_designs if total_designs else 0
    status_counts = Counter(design.get_status_display() for design in designs)

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, f'Summary (Last {days} Days)' if days else 'Summary', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f'Total Designs: {total_designs}', 0, 1)
    pdf.cell(0, 8, f'Average Budget: INR {avg_budget:.2f}', 0, 1)
    pdf.ln(5)

    headers = ['Design ID', 'User', 'Design Type', 'Status', 'Budget', 'Created']
    data = []
    row_colors = []
    for design in designs:
        data.append([
            design.id,
            design.user.username,
            design.get_design_type_display_name(),
            design.get_status_display(),
            f"INR {design.budget:.2f}",
            design.created_at.strftime('%Y-%m-%d')
        ])
        row_colors.append((200, 255, 200) if design.status == 'completed' else None)
    pdf.add_table(headers, data, [20, 40, 30, 30, 30, 30], row_colors)

    if status_counts:
        chart_path = 'temp_design_chart.png'
        create_pie_chart(status_counts, 'Custom Designs by Status', chart_path)
        pdf.ln(10)
        pdf.cell(0, 10, 'Design Status Distribution', 0, 1, 'L')
        pdf.image(chart_path, w=100)
        os.remove(chart_path)

    pdf.output(output_path)
    report_name = os.path.basename(output_path)  # e.g., 'custom_design_report.pdf'
    Report.objects.get_or_create(
        file_name=report_name,
        # defaults={'description': f'Custom design report generated on {datetime.now().strftime("%Y-%m-%d")}'}
    )
# def generate_bulk_order_report(output_path, days=None):
#     pdf = PDFReport()
#     pdf.add_page()
#     pdf.set_font('Arial', 'B', 16)
#     pdf.cell(0, 20, 'Bhavi Fashion Bulk Order Report', 0, 1, 'C')
#     logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo.png')
#     if os.path.exists(logo_path):
#         pdf.image(logo_path, x=80, y=50, w=50)
#     pdf.ln(60)
#     pdf.set_font('Arial', '', 12)
#     pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
#     pdf.cell(0, 10, 'Prepared by: Bhavi Fashion Team', 0, 1, 'C')
#     pdf.add_page()
#     pdf.chapter_title('Bulk Order Inquiries')

#     bulk_orders = BulkOrder.objects.all().select_related('user')
#     if days:
#         start_date = timezone.now() - timedelta(days=days)
#         bulk_orders = bulk_orders.filter(created_at__gte=start_date)

#     total_orders = len(bulk_orders)
#     total_quantity = sum(order.quantity for order in bulk_orders)
#     status_counts = Counter(order.get_status_display() for order in bulk_orders)

#     pdf.set_font('Arial', 'B', 11)
#     pdf.cell(0, 10, f'Summary (Last {days} Days)' if days else 'Summary', 0, 1, 'L')
#     pdf.set_font('Arial', '', 10)
#     pdf.cell(0, 8, f'Total Bulk Orders: {total_orders}', 0, 1)
#     pdf.cell(0, 8, f'Total Quantity: {total_quantity}', 0, 1)
#     pdf.ln(5)

#     headers = ['Order ID', 'Business', 'Product Type', 'Quantity', 'Status', 'Created']
#     data = []
#     row_colors = []
#     for order in bulk_orders:
#         data.append([
#             order.id,
#             order.business_name,
#             order.product,
#             order.quantity,
#             order.get_status_display(),
#             order.created_at.strftime('%Y-%m-%d')
#         ])
#         row_colors.append((200, 255, 200) if order.status == 'accepted' else None)
#     pdf.add_table(headers, data, [20, 50, 30, 20, 30, 30], row_colors)

#     if status_counts:
#         chart_path = 'temp_bulk_order_chart.png'
#         create_bar_chart(status_counts, 'Bulk Orders by Status', 'Count', 'Status', chart_path)
#         pdf.ln(10)
#         pdf.cell(0, 10, 'Bulk Order Status Distribution', 0, 1, 'L')
#         pdf.image(chart_path, w=100)
#         os.remove(chart_path)

#     pdf.output(output_path)
#     report_name = os.path.basename(output_path)  # e.g., 'bulk_order_report.pdf'
#     Report.objects.get_or_create(
#         file_name=report_name,
#         # defaults={'description': f'Bulk order report generated on {datetime.now().strftime("%Y-%m-%d")}'}
#     )

def generate_bulk_order_report(output_path, days=None):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 20, 'Bhavi Fashion Bulk Order Report', 0, 1, 'C')
    logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo.png')
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=80, y=50, w=50)
    pdf.ln(60)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
    pdf.cell(0, 10, 'Prepared by: Bhavi Fashion Team', 0, 1, 'C')
    pdf.add_page()
    pdf.chapter_title('Bulk Order Inquiries')

    bulk_orders = BulkOrder.objects.all().select_related('user').prefetch_related('items')
    if days:
        start_date = timezone.now() - timedelta(days=days)
        bulk_orders = bulk_orders.filter(created_at__gte=start_date)

    total_orders = len(bulk_orders)
    total_quantity = sum(sum(item.quantity for item in order.items.all()) for order in bulk_orders)
    status_counts = Counter(order.get_status_display() for order in bulk_orders)

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, f'Summary (Last {days} Days)' if days else 'Summary', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f'Total Bulk Orders: {total_orders}', 0, 1)
    pdf.cell(0, 8, f'Total Items Ordered: {total_quantity}', 0, 1)
    pdf.ln(5)

    headers = ['Order ID', 'Business', 'Items', 'Status', 'Created']
    data = []
    row_colors = []
    for order in bulk_orders:
        item_descriptions = []
        total_items = 0
        for item in order.items.all():
            total_items += item.quantity
            if item.product:
                item_descriptions.append(f"{item.quantity}x {item.product.name}")
            elif item.custom_design_name:
                item_descriptions.append(f"{item.quantity}x {item.custom_design_name}")
        
        data.append([
            order.id,
            order.business_name,
            f"Total: {total_items} items\n" + "\n".join(item_descriptions) if item_descriptions else "N/A",
            order.get_status_display(),
            order.created_at.strftime('%Y-%m-%d')
        ])
        row_colors.append((200, 255, 200) if order.status == 'accepted' else None)
    
    pdf.add_table(headers, data, [20, 50, 80, 30, 30], row_colors)

    if status_counts:
        chart_path = 'temp_bulk_order_chart.png'
        plt.figure(figsize=(6, 4))
        labels, values = zip(*status_counts.items())
        sns.barplot(x=list(values), y=list(labels), hue=list(labels), palette='viridis', legend=False)
        plt.title('Bulk Orders by Status')
        plt.xlabel('Count')
        plt.ylabel('Status')
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        
        pdf.ln(10)
        pdf.cell(0, 10, 'Bulk Order Status Distribution', 0, 1, 'L')
        pdf.image(chart_path, w=100)
        os.remove(chart_path)

    pdf.output(output_path)
    report_name = os.path.basename(output_path)
    Report.objects.get_or_create(
        file_name=report_name,
    )

def generate_product_report(output_path, days=None):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 20, 'Bhavi Fashion Product Report', 0, 1, 'C')
    logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo.png')
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=80, y=50, w=50)
    pdf.ln(60)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
    pdf.cell(0, 10, 'Prepared by: Bhavi Fashion Team', 0, 1, 'C')
    pdf.add_page()
    pdf.chapter_title('Product Inventory')

    products = Product.objects.all().select_related('category')
    low_stock = [p for p in products if p.stock <= 10]
    total_products = len(products)
    avg_price = sum(p.current_price for p in products) / total_products if total_products else 0

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, 'Summary', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f'Total Products: {total_products}', 0, 1)
    pdf.cell(0, 8, f'Average Price: INR {avg_price:.2f}', 0, 1)
    pdf.cell(0, 8, f'Low Stock Products: {len(low_stock)}', 0, 1)
    pdf.ln(5)

    headers = ['Product ID', 'Name', 'Category', 'Price', 'Stock', 'Rating']
    data = []
    row_colors = []
    category_counts = Counter()
    in_stock = {}
    low_stock_counts = {}
    for product in products:
        data.append([
            product.id,
            product.name,
            product.category.name,
            f"INR {product.current_price:.2f}",
            product.stock,
            f"{product.avg_rating:.1f}/5"
        ])
        row_colors.append((255, 200, 200) if product.stock <= 10 else None)
        cat = product.category.name
        category_counts[cat] += 1
        if product.stock > 10:
            in_stock[cat] = in_stock.get(cat, 0) + 1
        else:
            low_stock_counts[cat] = low_stock_counts.get(cat, 0) + 1
    pdf.add_table(headers, data, [20, 70, 30, 30, 20, 20], row_colors)

    if category_counts:
        chart_path = 'temp_product_chart.png'
        create_bar_chart(category_counts, 'Products by Category', 'Count', 'Category', chart_path)
        pdf.ln(10)
        pdf.cell(0, 10, 'Product Category Distribution', 0, 1, 'L')
        pdf.image(chart_path, w=100)
        os.remove(chart_path)

    categories = list(category_counts.keys())
    in_stock_vals = [in_stock.get(cat, 0) for cat in categories]
    low_stock_vals = [low_stock_counts.get(cat, 0) for cat in categories]
    if categories:
        chart_path = 'temp_product_stock_chart.png'
        create_stacked_bar_chart(categories, in_stock_vals, low_stock_vals, 'Stock Status by Category', chart_path)
        pdf.ln(10)
        pdf.cell(0, 10, 'Stock Status Distribution', 0, 1, 'L')
        pdf.image(chart_path, w=100)
        os.remove(chart_path)

    pdf.output(output_path)
    report_name = os.path.basename(output_path)  # e.g., 'product_report.pdf'
    Report.objects.get_or_create(
        file_name=report_name,
        # defaults={'description': f'Product report generated on {datetime.now().strftime("%Y-%m-%d")}'}
    )

def generate_tailor_application_report(output_path, days=None):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 20, 'Bhavi Fashion Tailor Application Report', 0, 1, 'C')
    logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'logo.png')
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=80, y=50, w=50)
    pdf.ln(60)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
    pdf.cell(0, 10, 'Prepared by: Bhavi Fashion Team', 0, 1, 'C')
    pdf.add_page()
    pdf.chapter_title('Tailor Job Applications')

    applications = TailorApplication.objects.all().select_related('user')
    if days:
        start_date = timezone.now() - timedelta(days=days)
        applications = applications.filter(created_at__gte=start_date)

    total_apps = len(applications)
    approved = sum(1 for app in applications if app.status == 'approved')
    approval_rate = (approved / total_apps * 100) if total_apps else 0
    status_counts = Counter(app.get_status_display() for app in applications)

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, f'Summary (Last {days} Days)' if days else 'Summary', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f'Total Applications: {total_apps}', 0, 1)
    pdf.cell(0, 8, f'Approval Rate: {approval_rate:.1f}%', 0, 1)
    pdf.ln(5)

    headers = ['Application ID', 'Name', 'Job Title', 'Status', 'Experience', 'Created']
    data = []
    row_colors = []
    for app in applications:
        data.append([
            app.id,
            app.name,
            app.job_title,
            app.get_status_display(),
            app.experience,
            app.created_at.strftime('%Y-%m-%d')
        ])
        row_colors.append((200, 255, 200) if app.status == 'approved' else None)
    pdf.add_table(headers, data, [30, 40, 40, 30, 30, 25], row_colors)

    if status_counts:
        chart_path = 'temp_tailor_chart.png'
        create_pie_chart(status_counts, 'Tailor Applications by Status', chart_path)
        pdf.ln(10)
        pdf.cell(0, 10, 'Application Status Distribution', 0, 1, 'L')
        pdf.image(chart_path, w=100)
        os.remove(chart_path)

    pdf.output(output_path)
    report_name = os.path.basename(output_path)  # e.g., 'tailor_application_report.pdf'
    Report.objects.get_or_create(
        file_name=report_name,
        # defaults={'description': f'Tailor application report generated on {datetime.now().strftime("%Y-%m-%d")}'}
    )

def main(days=None):
    parser = argparse.ArgumentParser(description='Generate Bhavi Fashion Reports')
    parser.add_argument('--days', type=int, help='Filter reports to last N days')
    args = parser.parse_args()

    report_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
    os.makedirs(report_dir, exist_ok=True)

    try:
        generate_order_report(os.path.join(report_dir, 'order_report.pdf'), days=args.days)
        print("Order report generated successfully.")
        generate_custom_design_report(os.path.join(report_dir, 'custom_design_report.pdf'), days=args.days)
        print("Custom design report generated successfully.")
        generate_bulk_order_report(os.path.join(report_dir, 'bulk_order_report.pdf'), days=args.days)
        print("Bulk order report generated successfully.")
        generate_product_report(os.path.join(report_dir, 'product_report.pdf'), days=args.days)
        print("Product report generated successfully.")
        generate_tailor_application_report(os.path.join(report_dir, 'tailor_application_report.pdf'), days=args.days)
        print("Tailor application report generated successfully.")
    except Exception as e:
        print(f"Error generating reports: {e}")

if __name__ == '__main__':
    main()