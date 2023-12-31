import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView
from hitcount.views import HitCountDetailView

from .forms import ReviewForm
from .models import Book, AuthorBook, Review, Like, Save


#
# class BookDetailView(View):
#     def get(self, request, pk):
#         book = Book.objects.get(pk=pk)
#         author_books = AuthorBook.objects.filter(book=book)
#         review_set = book.review_set.filter(pk=pk)
#
#         review = ReviewForm()
#
#         context = {
#             'book': book,
#             'author_books': author_books,
#             'review': review,
#             'review_set': review_set
#         }
#         return render(request, 'book_detail.html', context)



class BookDetailView(HitCountDetailView):
    model = Book
    template_name = 'book_detail.html'
    context_object_name = 'book'
    count_hit = True


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        context['author_books'] = AuthorBook.objects.filter(book=book)
        context['review'] = ReviewForm()

        return context


class ReviewView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = Book.objects.get(pk=pk)
        review = ReviewForm(data=request.POST)

        if review.is_valid():
            Review.objects.create(
                book_id=book,
                user_id=request.user,
                star_given=review.cleaned_data['star_given'],
                review_text=review.cleaned_data['review_text']

            )
            return redirect(reverse('detail', kwargs={'pk': book.pk}))

        context = {
            'book': book,
            'review': review,
        }
        return render(request, 'book_detail.html', context)





class BookListView(View):
    def get(self, request):
        books = Book.objects.order_by('-id')
        search = request.GET.get('q', '')
        if search:
            books = books.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        if not search and books.count() == 0:
            messages.warning(request, 'There is no books.')

        paginator = Paginator(books, 4)
        page_num = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_num)

        context = {
            'books': books,
            'page_obj': page_obj,
        }
        return render(request, 'book_list.html', context)




class LikeView(LoginRequiredMixin ,View):
    def get(self, request):
        user = request.user
        post_id = request.POST.get('post_id')
        post_obj = Review.objects.get(pk=post_id)
        

        context = {
            'user': user,
            'post_obj': post_obj,
        }
        return render(request, 'book_detail.html', context)

    def post(self, request):
        user = request.user
        post_id = request.POST.get('post_id')
        post_obj = Review.objects.get(pk=post_id)
        print(post_id)

        if user in post_obj.liked.all():
            post_obj.liked.remove(user)
        else:
            post_obj.liked.add(user)

        like, created = Like.objects.get_or_create(user=user, review_id=post_id)

        if not created:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'
        like.save()

        book_id = post_obj.book_id.pk
        return redirect('detail', pk=book_id)


saved_books = []

class SaveView(LoginRequiredMixin ,View):
    def get(self, request):
        user = request.user

        context = {
            'user': user,
        }
        return render(request, 'book_detail.html', context)

    def post(self, request):
        user = request.user
        book_id = request.POST.get('book_id')
        book_id = int(book_id)
        post_obj = Book.objects.get(pk=book_id)


        if user in post_obj.saved.all():
            post_obj.saved.remove(user)
        else:
            post_obj.saved.add(user)

        save, created = Save.objects.get_or_create(user=user, book_id=book_id)

        if not created: 
            if save.value == 'Save':
                save.value = 'Saved'
                book = save.book
                if book in saved_books:
                    saved_books.remove(book)

            else:
                save.value = 'Save'
                messages.success(request, 'You saved book')
                book = save.book
                if book not in saved_books:
                    saved_books.append(book)

        save.save()

        return redirect('detail', pk=book_id)


class SavedBooksView(View):
    def get(self, request, user_id):

        if request.user.id == user_id:
            context = {
                "saved_books": saved_books
            }
            return render(request, "saved_books.html", context)
        else:
            messages.warning(request, "WTF")











