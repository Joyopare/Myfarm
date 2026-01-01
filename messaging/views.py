from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Conversation, Message, Notification
from accounts.models import FarmerProfile, CustomerProfile

class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'messaging/conversation_list.html'
    context_object_name = 'conversations'
    
    def get_queryset(self):
        if self.request.user.user_type == 'customer':
            return Conversation.objects.filter(customer=self.request.user.customer_profile).order_by('-updated_at')
        else:
            return Conversation.objects.filter(farmer=self.request.user.farmer_profile).order_by('-updated_at')

class ConversationDetailView(LoginRequiredMixin, DetailView):
    model = Conversation
    template_name = 'messaging/conversation_detail.html'
    context_object_name = 'conversation'
    
    def get_queryset(self):
        if self.request.user.user_type == 'customer':
            return Conversation.objects.filter(customer=self.request.user.customer_profile)
        else:
            return Conversation.objects.filter(farmer=self.request.user.farmer_profile)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversation = self.get_object()
        
        # Mark messages as read
        Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=self.request.user).update(is_read=True)
        
        context['messages'] = conversation.messages.all().order_by('created_at')
        return context

@login_required
def start_conversation(request, farmer_id):
    if request.user.user_type != 'customer':
        messages.error(request, 'Only customers can start conversations with farmers.')
        return redirect('accounts:home')
    
    farmer = get_object_or_404(FarmerProfile, id=farmer_id)
    customer = request.user.customer_profile
    
    conversation, created = Conversation.objects.get_or_create(
        customer=customer,
        farmer=farmer
    )
    
    return redirect('messaging:conversation_detail', pk=conversation.pk)

@login_required
def send_message(request):
    if request.method == 'POST':
        conversation_id = request.POST.get('conversation_id')
        content = request.POST.get('content')
        
        if not content.strip():
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Check if user is part of this conversation
        if request.user.user_type == 'customer':
            if conversation.customer != request.user.customer_profile:
                return JsonResponse({'error': 'Access denied'}, status=403)
        else:
            if conversation.farmer != request.user.farmer_profile:
                return JsonResponse({'error': 'Access denied'}, status=403)
        
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        
        # Update conversation timestamp
        conversation.save()
        
        # Create notification for the other user
        if request.user.user_type == 'customer':
            recipient = conversation.farmer.user
        else:
            recipient = conversation.customer.user
        
        Notification.objects.create(
            user=recipient,
            notification_type='new_message',
            title='New Message',
            message=f'You have a new message from {request.user.username}'
        )
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'sender': message.sender.username,
            'content': message.content,
            'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'messaging/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

@login_required
def notification_count(request):
    """Return the count of unread notifications for the current user"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'success': True})
