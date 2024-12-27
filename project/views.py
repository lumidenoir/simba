import base64
from datetime import datetime, timedelta
import io
import os
import random
import urllib

from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Case, F, Func, Max, Sum, When
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.dateparse import parse_date
import matplotlib.pyplot as plt
from weasyprint import HTML

from .forms import *
from .models import *

def home(request):
    if request.user.is_authenticated:
        return render(request, 'home_wilogin.html')
    else:
        return redirect('/login')

def list(request):
    if request.user.is_authenticated:
        items = Item.objects.all()

        paginator = Paginator(items, 15)
        page_number = request.GET.get('page')
        page_items = paginator.get_page(page_number)
        if request.method == "POST":
            itype = request.POST['itype']
            quantity = float(request.POST['quantity'])
            gst = float(request.POST['gst'])
            retailer_price = round(float(request.POST['retailer_price']), 2)
            chef_price = round(float(request.POST['chef_price']), 2)
            bulk_price = round(float(request.POST['bulk_price']), 2)

            if Item.objects.filter(i_type=itype).exists():
                msg = "Item type already exists!"
                return render(request, 'list.html', {'msg': msg, 'items':page_items})

            item = Item(
                i_type=itype,
                quantity=quantity,
                gst=gst,
                retailer_price=retailer_price,
                chef_price=chef_price,
                bulk_price=bulk_price,
                tsales=0,
            )
            item.save()
            return redirect('/list')
        else:
            return render(request, 'list.html', {'items': page_items})
    else:
        return redirect('/login')

def view_login(request):
    if(request.method=="POST"):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
    return render(request, 'login.html')

def do_logout(request):
    logout(request)
    return redirect('/login')

def delete(request, id):
    item = Item.objects.filter(id=id)
    item.delete()

    return redirect('/list')

def delete_sale_item(request, id):
    sale = Sale.objects.filter(id=id).first()
    if sale:
        sale.delete()
    return redirect('/sale')

def view_delete(request):
    items = Item.objects.all()
    return render(request, 'delete.html', {'items':items})

def edit(request, id):
    if(request.method=="POST"):
        item = Item.objects.get(id=id)
        item.i_type = request.POST.get('itype')
        item.quantity = float(request.POST.get('quantity'))
        item.gst = float(request.POST.get('gst'))
        item.retailer_price = round(float(request.POST.get('retailer_price')), 2)
        item.chef_price = round(float(request.POST.get('chef_price')), 2)
        item.bulk_price = round(float(request.POST.get('bulk_price')), 2)
        item.save()
        return redirect('/list')
    else:
        items = Item.objects.filter(id=id)
        return render(request, 'edit.html', {'items':items})

def generate_sale_id():
    date_str = datetime.now().astimezone().strftime('%Y%m%d%H%M')
    random_number = f"{random.randint(100, 999):03d}"
    return f"{date_str}{random_number}"

def add_customer_info(request):
    if 'sale_id' not in request.session:
        request.session['sale_id'] = generate_sale_id()

    if request.method == "POST":
        customer_name = request.POST['customer_name']
        customer_address = request.POST['customer_address']
        customer_mobile = request.POST['customer_mobile']
        buyer_type = request.POST['buyer_type']

        request.session.update({
            'customer_name': customer_name,
            'customer_address': customer_address,
            'customer_mobile': customer_mobile,
            'buyer_type': buyer_type
        })

        return redirect('sale')

    return render(request, 'add_customer_info.html')

def sale(request):
    if 'sale_id' not in request.session:
        return redirect('add_customer_info')

    sale_id = request.session['sale_id']
    customer_name = request.session.get('customer_name', None)
    customer_address = request.session.get('customer_address', None)
    customer_mobile = request.session.get('customer_mobile', None)
    buyer_type = request.session.get('buyer_type', None)

    if not customer_name or not customer_mobile:
        return redirect('add_customer_info')

    if request.method == "POST":
        itype = request.POST['itype']
        quantity = float(request.POST['quantity'])
        item_discount = float(request.POST['discount'] or 0)
        item = Item.objects.filter(i_type=itype).first()
        items = Item.objects.all()
        sale_items = Sale.objects.filter(sale_id=sale_id)

        if sale_items.filter(i_type=itype).exists():
            msg = "Item type already exists in the sale!"
            return render(request, 'sale.html', {'msg': msg, 'items': items})

        if item and quantity <= int(item.quantity):
            # Determine price based on buyer type
            if buyer_type == 'Retailer':
                price = item.retailer_price
            elif buyer_type == 'Chef':
                price = item.chef_price
            elif buyer_type == 'Bulk':
                price = item.bulk_price

            item.quantity -= quantity
            item.tsales += quantity
            item.save()

            subtotal = round(quantity * price, 2)
            gst_subtotal = round(subtotal * (item.gst / 100), 2)
            total_with_gst = round(subtotal + gst_subtotal, 2)

            discount_amount = round((total_with_gst * item_discount) / 100, 2)
            sale_price = round(total_with_gst - discount_amount, 2)

            sale = Sale(
                sale_id=sale_id,
                i_type=item.i_type,
                quantity=quantity,
                price=price,
                gst_subtotal=gst_subtotal,
                customer_name=customer_name,
                customer_addrs=customer_address,
                customer_mobile=customer_mobile,
                subtotal=subtotal,
                sale_price=sale_price,
                created_at=timezone.now(),
                discount=item_discount,
                payment_status='unpaid',
                return_status=0,
            )
            sale.save()

            return redirect('sale')
        else:
            msg = "Insufficient inventory!" if item else "Item not found!"
            return render(request, 'sale.html', {'msg': msg, 'items': items})
    else:
        items = Item.objects.all()
        sale_items = Sale.objects.filter(sale_id=sale_id)

        sale_data = []
        total_price = 0
        total_gst = 0
        total_discount = 0

        for sale_item in sale_items:
            item = Item.objects.filter(i_type=sale_item.i_type).first()
            if item:
                gst = item.gst
                price = sale_item.price
                quantity = sale_item.quantity
                subtotal = sale_item.subtotal
                gst_subtotal = sale_item.gst_subtotal
                discount = sale_item.discount
                total_with_gst = subtotal + gst_subtotal
                discount_amount = (total_with_gst * discount) / 100
                sale_price = round(total_with_gst - discount_amount, 2)

                sale_data.append({
                    'id': sale_item.id,
                    'item_type': sale_item.i_type,
                    'quantity': quantity,
                    'price': price,
                    'subtotal': round(subtotal, 2),
                    'gst': gst,
                    'gst_subtotal': round(gst_subtotal, 2),
                    'discount': discount,
                    'discount_amount': round(discount_amount, 2),
                    'sale_price': sale_price
                })

            total_price += subtotal
            total_gst += gst_subtotal
            total_discount += discount_amount

        grand_total = round(total_price + total_gst - total_discount, 2)

        return render(request, 'sale.html', {
            'items': items,
            'sale_data': sale_data,
            'sale_id': sale_id,
            'customer_name': customer_name,
            'customer_address': customer_address,
            'customer_mobile': customer_mobile,
            'total_price': round(total_price, 2),
            'total_gst': round(total_gst, 2),
            'grand_total': grand_total,
            'total_discount': round(total_discount, 2),
            'buyer_type': buyer_type,
        })

class Round(Func):
    function = 'ROUND'
    template = "%(function)s(%(expressions)s, 0)"

def sale_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    customer_name_filter = request.GET.get('customer_name')
    bill_no_filter = request.GET.get('bill_no')
    payment_status_filter = request.GET.get('payment_status')
    page_number = request.GET.get('page', 1)

    sales_query = Sale.objects.all()

    if start_date and end_date:
        sales_query = sales_query.filter(
            created_at__date__gte=parse_date(start_date),
            created_at__date__lte=parse_date(end_date)
        )

    if bill_no_filter and bill_no_filter.lower() != "none":
        sales_query = sales_query.filter(sale_id__icontains=bill_no_filter)

    if customer_name_filter and customer_name_filter.lower() != "none":
        sales_query = sales_query.filter(customer_name__icontains=customer_name_filter)

    if payment_status_filter:
        sales_query = sales_query.filter(payment_status=payment_status_filter)

    grouped_sales = (
        sales_query.values('sale_id')
        .annotate(
            grand_total=Round(Sum('sale_price')),
            datetime=Max('created_at'),
            payment_status=Max('payment_status'),
            customer_name=F('customer_name'),
            customer_mobile=F('customer_mobile'),
        )
        .order_by('-datetime')
    )

    paginator = Paginator(grouped_sales, 10)
    sales_page = paginator.get_page(page_number)

    total_paid = sales_query.filter(payment_status='paid').aggregate(total=Round(Sum('sale_price')))['total'] or 0
    total_unpaid = sales_query.filter(payment_status='unpaid').aggregate(total=Round(Sum('sale_price')))['total'] or 0
    total_return = sales_query.filter(payment_status='return').aggregate(total=Round(Sum('sale_price')))['total'] or 0

    sales_data = []
    for sale in sales_page:
        sale['pdf_exists'] = os.path.exists(f'bill/{sale["sale_id"]}.pdf')
        sale['is_within_7_days'] = (
            sale['datetime'] >= timezone.now() - timedelta(days=7) and sale['payment_status'] != 'return'
        )
        sales_data.append(sale)

    return render(request, 'sale_list.html', {
        'grouped_sales': sales_data,
        'start_date': start_date,
        'end_date': end_date,
        'bill_no': bill_no_filter,
        'payment_status': payment_status_filter,
        'customer_name': customer_name_filter,
        'total_paid': total_paid,
        'total_unpaid': total_unpaid,
        'total_return': total_return,
        'page_obj': sales_page,
    })

def reorder(request):
    items = Item.objects.filter(quantity__lt=5).order_by('-tsales')
    return render(request, 'reorder.html', {'insufficients': items})

def clear_sale(request):
    sale_id = request.session.get('sale_id')
    if sale_id:
        sale_items = Sale.objects.filter(sale_id=sale_id)
        for sale_item in sale_items:
            item = Item.objects.filter(i_type=sale_item.i_type).first()
            if item:
                item.quantity += sale_item.quantity
                item.tsales -= sale_item.quantity
                item.save()
        sale_items.delete()
        del request.session['sale_id']
        del request.session['customer_name']
        del request.session['customer_address']
        del request.session['customer_mobile']
    return redirect('/sale')

def checkout(request):
    customer_name = request.session.get('customer_name', None)
    customer_mobile = request.session.get('customer_mobile', None)
    customer_address = request.session.get('customer_address', None)

    if 'sale_id' not in request.session:
        return redirect('sale')

    sale_id = request.session['sale_id']
    sale_items = Sale.objects.filter(sale_id=sale_id)

    total_price = 0
    gst_total = 0
    discount_total = 0
    sale_data = []

    for sale_item in sale_items:
        item = Item.objects.filter(i_type=sale_item.i_type).first()
        if item:
            gst = item.gst
            price = sale_item.price
            quantity = sale_item.quantity
            subtotal = sale_item.subtotal
            gst_subtotal = sale_item.gst_subtotal
            discount = sale_item.discount
            total_with_gst = subtotal + gst_subtotal
            discount_amount = (total_with_gst * discount) / 100
            sale_price = round(total_with_gst - discount_amount, 2)

            sale_data.append({
                'item_type': sale_item.i_type,
                'quantity': quantity,
                'price': price,
                'subtotal': round(subtotal, 2),
                'gst': gst,
                'gst_subtotal': round(gst_subtotal, 2),
                'discount': discount,
                'discount_amount': round(discount_amount, 2),
                'sale_price': sale_price
            })

            total_price += subtotal
            gst_total += gst_subtotal
            discount_total += discount_amount

    grand_total = total_price + gst_total
    grand_total_discount = round(grand_total - discount_total, 0)

    return render(request, 'bill.html', {
        'sale_data': sale_data,
        'total_price': round(total_price,2),
        'gst': round(gst_total,2),
        'grand_total_discount': grand_total_discount,
        'discount_amount': round(discount_total,2),
        'sale_id': sale_id,
        'customer_name': customer_name,
        'customer_mobile': customer_mobile,
        'customer_address': customer_address
    })

def toggle_payment_status(request, sale_id):
    if request.method == 'POST':
        sales = Sale.objects.filter(sale_id=sale_id)
        if sales.exists():
            current_status = sales.first().payment_status
            if current_status=='return':
                new_status='return'
            else:
                new_status = 'paid' if current_status == 'unpaid' else 'unpaid'
            sales.update(payment_status=new_status)
    return redirect('sale_list')

def generate_bill(request, sale_id):
    sale_items = Sale.objects.filter(sale_id=sale_id)

    # Initialize total calculations
    total_price = 0
    gst_total = 0
    discount_total = 0
    sale_data = []

    for sale_item in sale_items:
        item = Item.objects.filter(i_type=sale_item.i_type).first()
        if item:
            # Calculate values based on the sale_item and item
            gst = item.gst
            price = sale_item.price
            quantity = sale_item.quantity
            subtotal = sale_item.subtotal
            gst_subtotal = sale_item.gst_subtotal
            discount = sale_item.discount or 0  # Ensure discount is not None
            total_with_gst = subtotal + gst_subtotal
            discount_amount = (total_with_gst * discount) / 100
            sale_price = round(total_with_gst - discount_amount, 2)

            # Add the calculated values to sale_data
            sale_data.append({
                'item_type': sale_item.i_type,
                'quantity': quantity,
                'price': price,
                'subtotal': round(subtotal, 2),
                'gst': gst,
                'gst_subtotal': round(gst_subtotal, 2),
                'discount': discount,
                'discount_amount': round(discount_amount, 2),
                'sale_price': sale_price
            })

            # Update totals
            total_price += subtotal
            gst_total += gst_subtotal
            discount_total += discount_amount

    # Calculate grand totals
    grand_total = total_price + gst_total
    grand_total_discount = round(grand_total - discount_total, 0)

    # Fetch customer details from session
    customer_name = request.session.get('customer_name', 'N/A')
    customer_mobile = request.session.get('customer_mobile', 'N/A')
    customer_address = request.session.get('customer_address', 'N/A')

    html_content = render_to_string('bill.html', {
        'sale_data': sale_data,
        'total_price': total_price,
        'gst': round(gst_total,2),
        'grand_total_discount': grand_total_discount,
        'discount_amount': round(discount_total,2),
        'sale_id': sale_id,
        'customer_name': customer_name,
        'customer_mobile': customer_mobile,
        'customer_address': customer_address
    })

    # Save the PDF
    pdf_file_path = f'bill/{sale_id}.pdf'
    os.makedirs('bill', exist_ok=True)
    HTML(string=html_content).write_pdf(pdf_file_path)

    # Clear the session data
    for key in ['sale_id', 'customer_name', 'customer_address', 'customer_mobile', 'buyer_type']:
        request.session.pop(key, None)

    # Return the PDF response
    with open(pdf_file_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{sale_id}.pdf"'
        return response

def serve_pdf(request, sale_id):
    pdf_file_path = f'bill/{sale_id}.pdf'
    if os.path.exists(pdf_file_path):
        with open(pdf_file_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{sale_id}.pdf"'
            return response
    else:
        return HttpResponse(status=404)

def view_charts(request):
    # Get current date and month
    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    # Calculate daily sales
    daily_paid = Sale.objects.filter(created_at__date=today, payment_status='paid').aggregate(total=Sum(Round('sale_price')))['total'] or 0
    daily_unpaid = Sale.objects.filter(created_at__date=today, payment_status='unpaid').aggregate(total=Sum(Round('sale_price')))['total'] or 0

    # Calculate monthly sales
    monthly_paid = Sale.objects.filter(created_at__date__gte=start_of_month, payment_status='paid').aggregate(total=Sum(Round('sale_price')))['total'] or 0
    monthly_unpaid = Sale.objects.filter(created_at__date__gte=start_of_month, payment_status='unpaid').aggregate(total=Sum(Round('sale_price')))['total'] or 0

    # Most sold items
    most_sold_items = Sale.objects.values('i_type').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:10]
    item_labels = [item['i_type'] for item in most_sold_items]
    item_sales = [item['total_quantity'] for item in most_sold_items]

    # Generate daily sales chart
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.bar(['Paid', 'Unpaid'], [daily_paid, daily_unpaid], color=['green', 'red'])
    ax1.set_title('Daily Sales')
    ax1.set_ylabel('Amount (₹)')
    ax1.set_xlabel('Payment Status')

    # Save daily sales chart to a string buffer and encode it to base64
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png')
    buf1.seek(0)
    daily_chart_url = base64.b64encode(buf1.read()).decode('utf-8')
    buf1.close()

    # Generate monthly sales chart
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.bar(['Paid', 'Unpaid'], [monthly_paid, monthly_unpaid], color=['green', 'red'])
    ax2.set_title('Monthly Sales')
    ax2.set_ylabel('Amount (₹)')
    ax2.set_xlabel('Payment Status')

    # Save monthly sales chart to a string buffer and encode it to base64
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    monthly_chart_url = base64.b64encode(buf2.read()).decode('utf-8')
    buf2.close()

    # Generate most sold items chart
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    ax3.bar(item_labels, item_sales, color='skyblue')
    ax3.set_title('Most Sold Items')
    ax3.set_ylabel('Quantity Sold')
    ax3.set_xlabel('Item Type')
    ax3.tick_params(axis='x', rotation=45)

    # Save most sold items chart to a string buffer and encode it to base64
    buf3 = io.BytesIO()
    plt.savefig(buf3, format='png')
    buf3.seek(0)
    most_sold_chart_url = base64.b64encode(buf3.read()).decode('utf-8')
    buf3.close()

    return render(request, 'view_charts.html', {
        'daily_paid': daily_paid,
        'daily_unpaid': daily_unpaid,
        'monthly_paid': monthly_paid,
        'monthly_unpaid': monthly_unpaid,
        'daily_chart_url': daily_chart_url,
        'monthly_chart_url': monthly_chart_url,
        'most_sold_chart_url': most_sold_chart_url,
    })


def return_items(request, sale_id):
    if 'return_sale_id' not in request.session:
        request.session['return_sale_id'] = generate_sale_id()

    return_sale_id = request.session['return_sale_id']
    sale_items = Sale.objects.filter(sale_id=sale_id).exclude(return_status=F('quantity'), payment_status='return')
    return_sale_items = Sale.objects.filter(sale_id=return_sale_id)
    sale_data = []
    return_data = []

    if sale_items.exists():
        customer_name = sale_items.first().customer_name
        customer_address = sale_items.first().customer_addrs
        customer_mobile = sale_items.first().customer_mobile
    else:
        customer_name = customer_address = customer_mobile = None

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = get_object_or_404(Sale, id=item_id)
        return_quantity_str = request.POST.get('return_quantity')
        return_quantity = 0

        if return_quantity_str and return_quantity_str.replace('.', '', 1).isdigit():
            return_quantity = float(return_quantity_str)
        else:
            return_quantity = item.quantity - item.return_status

        if Sale.objects.filter(sale_id=return_sale_id, i_type=item.i_type).first():
            msg = "Item already added"
            return render(request, 'return_items.html', {'msg': msg, 'sale_id': sale_id})

        if return_quantity + item.return_status > item.quantity:
            msg = "Total return quantity exceeds purchased quantity."
            return render(request, 'return_items.html',
                          {'msg': msg,
                           'sale_items': sale_items,
                           'sale_id': sale_id,
                           'return_items': return_data,
                           'return_sale_id': return_sale_id,
                           'sale_id': sale_id,
                           'customer_name': customer_name,
                           'customer_address': customer_address,
                           'customer_mobile': customer_mobile,
                           })
        item_price = item.sale_price / item.quantity
        return_sale_price = round(item_price * return_quantity, 2)

        return_sale = Sale(
            sale_id=return_sale_id,
            i_type=item.i_type,
            quantity=-return_quantity,
            price=round(item_price,2),
            customer_name=item.customer_name,
            customer_addrs=item.customer_addrs,
            customer_mobile=item.customer_mobile,
            sale_price=return_sale_price,
            created_at=timezone.now(),
            payment_status='return',
            return_status=return_quantity,
        )
        return_sale.save()
        item.return_status+=return_quantity
        item.save()
        return redirect('return_items', sale_id=sale_id)

    for sale_item in sale_items:
        if sale_item.quantity > 0:
            sale_data.append({
                'id': sale_item.id,
                'item_type': sale_item.i_type,
                'quantity_pur': sale_item.quantity,
                'quantity_left': round(sale_item.quantity-sale_item.return_status,4),
                'price': sale_item.price,
                'sale_price': sale_item.sale_price,
                'sale_price_one': round(sale_item.sale_price / sale_item.quantity, 2)
            })

    for return_item in return_sale_items:
        if return_item.quantity < 0:
            return_data.append({
                'id': return_item.id,
                'item_type': return_item.i_type,
                'quantity': -return_item.quantity,
                'sale_price': return_item.sale_price,
            })

    total_return_price = Sale.objects.filter(sale_id=return_sale_id).aggregate(total=Sum('sale_price'))['total'] or 0
    total_return_price = round(total_return_price, 2)

    return render(request, 'return_items.html', {
        'sale_items': sale_data,
        'return_items': return_data,
        'return_sale_id': return_sale_id,
        'sale_id': sale_id,
        'total_return_price': total_return_price,
        'customer_name': customer_name,
        'customer_address': customer_address,
        'customer_mobile': customer_mobile,
    })

def delete_return_item(request, id, sale_id):
    sale = Sale.objects.filter(id=id).first()
    if sale:
        old_sale = Sale.objects.filter(sale_id=sale_id, i_type=sale.i_type).first()
        if old_sale:
            old_sale.return_status -= sale.return_status
            old_sale.save()
        sale.delete()
    return redirect('return_items', sale_id=sale_id)


def clear_return(request, sale_id):
    return_sale_id = request.session.get('return_sale_id')
    if return_sale_id:
        sale_items = Sale.objects.filter(sale_id=return_sale_id)
        for sale_item in sale_items:
            item = Sale.objects.filter(sale_id=sale_id, i_type=sale_item.i_type).first()
            if item:
                item.return_status -= sale_item.return_status
                item.save()
        sale_items.delete()
        del request.session['return_sale_id']
    return redirect('/sale_list')

def checkout_return(request, sale_id):
    if 'return_sale_id' not in request.session:
        return redirect('sale_list')
    return_sale_id=request.session.get('return_sale_id')
    sale_items = Sale.objects.filter(sale_id=return_sale_id)

    first_item = sale_items.first()
    customer_name = first_item.customer_name
    customer_address = first_item.customer_addrs
    customer_mobile = first_item.customer_mobile

    sale_data = []
    total_return_price = Sale.objects.filter(sale_id=return_sale_id).aggregate(total=Sum('sale_price'))['total'] or 0
    total_return_price = round(total_return_price, 2)

    for sale_item in sale_items:
        quantity = abs(sale_item.quantity)  # Ensure positive quantity
        sale_data.append({
            'item_type': sale_item.i_type,
            'quantity': quantity,
            'sale_price': sale_item.sale_price
        })

    return render(request, 'return_bill.html', {
        'sale_data': sale_data,
        'sale_id': sale_id,
        'return_sale_id': return_sale_id,
        'customer_name': customer_name,
        'customer_mobile': customer_mobile,
        'customer_address': customer_address,
        'total_return_price': total_return_price
    })

def generate_return_bill(request, sale_id):
    # Fetch sale items
    return_sale_id=request.session.get('return_sale_id')
    sale_items = Sale.objects.filter(sale_id=return_sale_id)
    if not sale_items.exists():
        raise Http404("No sales found for the given Sale ID.")

    # Aggregate return data
    sale_data = []
    total_return_price = Sale.objects.filter(sale_id=return_sale_id).aggregate(total=Sum('sale_price'))['total'] or 0
    total_return_price = round(total_return_price, 2)

    for sale_item in sale_items:
        quantity = abs(sale_item.quantity)  # Ensure positive quantity
        sale_data.append({
            'item_type': sale_item.i_type,
            'quantity': quantity,
            'sale_price': sale_item.sale_price
        })

    # Extract customer details
    first_item = sale_items.first()
    customer_name = first_item.customer_name
    customer_address = first_item.customer_addrs
    customer_mobile = first_item.customer_mobile

    # Render HTML content for the PDF
    html_content = render_to_string('return_bill.html', {
        'sale_data': sale_data,
        'sale_id': sale_id,
        'return_sale_id': return_sale_id,
        'customer_name': customer_name,
        'customer_mobile': customer_mobile,
        'customer_address': customer_address,
        'total_return_price': round(total_return_price,0)
    })

    # Generate PDF
    pdf_file_path = f'bill/{return_sale_id}.pdf'
    os.makedirs('bill', exist_ok=True)
    HTML(string=html_content).write_pdf(pdf_file_path)

    # Clear return-related session data
    request.session.pop('return_sale_id', None)

    # Serve the PDF file
    try:
        with open(pdf_file_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{return_sale_id}.pdf"'
            return response
    except FileNotFoundError:
        raise Http404("Generated PDF file not found.")
