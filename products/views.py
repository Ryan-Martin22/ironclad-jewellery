from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Q
from django.db.models.functions import Lower
from favourites.models import Favourites
from .models import Product, Category, Review
from .forms import ProductForm, ReviewForm


def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(
                    request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            queries = Q(name__icontains=query) | Q(
                description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)
    reviews = Review.objects.filter(
        product_id=product.id, status=True).order_by('-created_on')
    total_reviews = reviews.count()

    try:
        favourites = get_object_or_404(Favourites, username=request.user.id)
    except Http404:
        is_in_favourites = False
    else:
        is_in_favourites = bool(product in favourites.products.all())

    template = 'products/product_detail.html'

    context = {
        'is_in_favourites': is_in_favourites,
        'product': product,
        'reviews': reviews,
        'total_reviews': total_reviews,
    }

    return render(request, template, context)


@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Uh Oh!. Please ensure the form is valid.')
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Uh Oh Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        # Redirect back to homepage if not a superuser
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        product.delete()
        messages.success(request, f'{product.name} deleted!')
        return redirect(reverse('products'))

    return render(request, 'products/confirm_delete.html')


def submit_review(request, product_id):
    """Sumbit a product review"""
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            data = Review()
            data.rating = form.cleaned_data['rating']
            data.review = form.cleaned_data['review']
            data.product = product
            data.user_id = request.user.id
            data.save()
            messages.success(
                request, 'Thank you! Your review has been submitted.')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(
                request, "Sorry your review could not be submitted.")
            return redirect(reverse('product_detail', args=[product.id]))
    else:
        form = ReviewForm()

    template = 'products/product_detail.html'

    return render(request, template)


@login_required
def edit_review(request, review_id):
    """Edit a review"""

    review = get_object_or_404(Review, pk=review_id)
    if review.user.id is not request.user.id:
        messages.error(request, "You are not authorised to edit this review")
        return redirect(reverse('home'))
    product = review.product

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Review successfully updated!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(
                request, 'Failed to update this review. \
                    Please ensure the form is valid.')
    else:
        form = ReviewForm(instance=review)
        messages.info(request, 'You are editing your review')

    template = 'products/edit_review.html'

    context = {
        'form': form,
        'review': review,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_review(request, review_id):
    """ Delete review from the product details page """

    review = get_object_or_404(Review, pk=review_id)
    if review.user.id is not request.user.id:
        messages.error(request, "You are not authorised to delete this review")
        return redirect(reverse('home'))
    product = review.product

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Your review has been deleted!')
        return redirect(reverse_lazy('product_detail', args=[product.id]))

    return render(request, 'products/delete_review.html')
